from django.core.management.base import BaseCommand

from jobs.ingest.roles import MAX_AGE_DAYS, match_bucket, matches_location
from jobs.ingest.sources.amazon import fetch_amazon
from jobs.ingest.sources.greenhouse import fetch_greenhouse
from jobs.ingest.sources.unstop import fetch_unstop
from jobs.ingest.sources.workday import fetch_workday
from jobs.ingest.text import (
    days_ago, detect_work_mode, extract_deadline, extract_eligibility,
    extract_experience, extract_salary, extract_skills, fingerprint, norm_city,
)
from jobs.models import Category, Job, Skill

SOURCE_FETCHERS = {
    'greenhouse': fetch_greenhouse,
    'workday': fetch_workday,
    'amazon': fetch_amazon,
    'unstop': fetch_unstop,
}


class Command(BaseCommand):
    help = 'Fetch live job postings from Greenhouse, Workday and Amazon and load them into the database.'

    def add_arguments(self, parser):
        parser.add_argument('--source', choices=['all', *SOURCE_FETCHERS.keys()], default='all')
        parser.add_argument('--keep-existing', action='store_true', help='Do not clear existing jobs before importing')

    def handle(self, *args, **opts):
        def log(msg, warn=False):
            self.stdout.write((self.style.WARNING if warn else self.style.NOTICE)(msg))

        source_names = list(SOURCE_FETCHERS.keys()) if opts['source'] == 'all' else [opts['source']]

        raw = []
        for name in source_names:
            fetched = SOURCE_FETCHERS[name](log)
            log(f'{name}: {len(fetched)} postings collected')
            raw.extend(fetched)

        if not raw:
            self.stdout.write(self.style.ERROR(
                'No postings collected from any source — aborting, existing data left untouched.'
            ))
            return

        # ---- filter, classify, enrich, in-run dedupe ---------------------------
        seen = {}
        counts = {'raw': len(raw), 'no_match': 0, 'no_url': 0, 'off_region': 0, 'stale': 0, 'dupe': 0, 'kept': 0}

        for r in raw:
            title, company, location = r.get('title'), r.get('company'), r.get('location')
            if not title or not company:
                counts['no_match'] += 1
                continue
            if not r.get('apply_url'):
                counts['no_url'] += 1
                continue

            bucket = match_bucket(title)
            if not bucket:
                counts['no_match'] += 1
                continue
            if not matches_location(location):
                counts['off_region'] += 1
                continue

            age = days_ago(r.get('posted_date'))
            if age is not None and age > MAX_AGE_DAYS:
                counts['stale'] += 1
                continue

            fp = fingerprint(company, title, location)
            if fp in seen:
                counts['dupe'] += 1
                continue

            description = r.get('description') or ''
            combined = f'{title}\n{description}'
            exp_text, min_exp, max_exp = extract_experience(description, title)

            seen[fp] = {
                'fingerprint': fp,
                'title': str(title).strip(),
                'company': str(company).strip(),
                'location': str(location or 'Not specified').strip(),
                'city': norm_city(location).title() if norm_city(location) else '',
                'work_mode': detect_work_mode(location, title, description),
                'category_label': bucket['label'],
                'skills': extract_skills(combined),
                'experience_text': exp_text,
                'min_experience_years': min_exp,
                'max_experience_years': max_exp,
                'salary_text': extract_salary(combined) or 'Not disclosed',
                'eligibility': extract_eligibility(combined),
                'description': description[:4000],
                'deadline': extract_deadline(combined),
                'apply_url': r['apply_url'],
                'posted_date': r.get('posted_date'),
                'source': r.get('source', ''),
            }
            counts['kept'] += 1

        log(f"process: kept {counts['kept']} of {counts['raw']} "
            f"(no_match={counts['no_match']} no_url={counts['no_url']} off_region={counts['off_region']} "
            f"stale={counts['stale']} dupe={counts['dupe']})")

        if not seen:
            self.stdout.write(self.style.ERROR(
                'Nothing survived filtering — aborting before touching the database.'
            ))
            return

        # ---- replace existing data, then upsert ---------------------------------
        if not opts['keep_existing']:
            deleted, _ = Job.objects.all().delete()
            log(f'cleared {deleted} existing job row(s) (and their favorites) before import')

        created = updated = 0
        for entry in seen.values():
            category, _ = Category.objects.get_or_create(name=entry.pop('category_label'))
            skill_names = entry.pop('skills')

            job, was_created = Job.objects.update_or_create(
                fingerprint=entry.pop('fingerprint'),
                defaults={**entry, 'category': category, 'is_active': True},
            )
            job.skills.set([Skill.objects.get_or_create(name=s)[0] for s in skill_names])

            created += was_created
            updated += not was_created

        self.stdout.write(self.style.SUCCESS(
            f'Import complete: {created} job(s) created, {updated} updated, {Job.objects.count()} total active.'
        ))
