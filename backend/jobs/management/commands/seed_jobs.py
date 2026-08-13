import datetime as dt

from django.core.management.base import BaseCommand

from jobs.models import Category, Job, Skill

CATEGORIES = [
    'Full Stack Developer', 'React Developer', 'Frontend Developer',
    'Backend Developer', 'Machine Learning Intern', 'MERN Stack Developer',
]

SAMPLE_JOBS = [
    dict(company='Razorpay', title='Full Stack Builder', location='Bengaluru', city='Bengaluru',
         work_mode='onsite', category='Full Stack Developer',
         skills=['CI/CD', 'Node.js', 'React'], experience_text='3-6 years',
         min_experience_years=3, max_experience_years=6,
         salary_text='Not disclosed', eligibility="Bachelor's degree (B.Tech/B.E./BCA/B.Sc).",
         description='Razorpay is hiring a Full Stack Builder in Bengaluru. The role centres on CI/CD.',
         deadline=None, apply_url='https://job-boards.greenhouse.io/razorpaysoftwareprivatelimited/jobs/4699107005',
         posted_date='2026-06-30', source='greenhouse:razorpay'),
    dict(company='PhonePe', title='Software Engineer, React Native', location='Bangalore', city='Bangalore',
         work_mode='onsite', category='React Developer',
         skills=['JavaScript', 'TypeScript', 'Go', 'React', 'React Native'], experience_text='3-5 years',
         min_experience_years=3, max_experience_years=5,
         salary_text='Not disclosed', eligibility='Open to candidates meeting the technical requirements.',
         description='PhonePe is hiring a Software Engineer, React Native (3-5 Years) in Bangalore.',
         deadline=None, apply_url='https://job-boards.greenhouse.io/phonepe/jobs/7795782003',
         posted_date='2026-07-08', source='greenhouse:phonepe'),
    dict(company='Amazon', title='Applied Scientist II, International Machine Learning', location='Bengaluru, Karnataka, IND',
         city='Bengaluru', work_mode='unspecified', category='Machine Learning Intern',
         skills=['Python', 'Java', 'C++', 'TensorFlow', 'Machine Learning', 'Deep Learning'], experience_text='3+ years',
         min_experience_years=3, max_experience_years=None,
         salary_text='Not disclosed', eligibility="Bachelor's degree; Master's an advantage.",
         description='Amazon is hiring an Applied Scientist II, International Machine Learning in Bengaluru.',
         deadline=None, apply_url='https://www.amazon.jobs/en/jobs/10482155/applied-scientist-ii-international-machine-learning',
         posted_date='2026-07-22', source='amazon'),
    dict(company='Adobe', title='Computer Scientist II (Full Stack)', location='Noida', city='Noida',
         work_mode='unspecified', category='Full Stack Developer',
         skills=['JavaScript', 'TypeScript', 'Java', 'React', 'Node.js', 'GraphQL'], experience_text='6-8 years',
         min_experience_years=6, max_experience_years=8,
         salary_text='Not disclosed', eligibility="Bachelor's degree (B.Tech/B.E./BCA/B.Sc).",
         description='Adobe is hiring a Computer Scientist II (Full Stack) in Noida.',
         deadline=None, apply_url='https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Noida/Computer-Scientist-II--Full-Stack-_R170676',
         posted_date='2026-07-27', source='workday:adobe'),
    dict(company='Adobe', title='Computer Scientist (Full Stack - Frontend Heavy)', location='Bangalore', city='Bangalore',
         work_mode='unspecified', category='Full Stack Developer',
         skills=['Java', 'Express', 'DynamoDB', 'SQL', 'NoSQL', 'AWS'], experience_text='7-10 years',
         min_experience_years=7, max_experience_years=10,
         salary_text='Not disclosed', eligibility="Bachelor's degree (B.Tech/B.E./BCA/B.Sc).",
         description='Adobe is hiring a Computer Scientist (Full Stack - Frontend Heavy) in Bangalore.',
         deadline=None, apply_url='https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Bangalore/Computer-Scientist---Full-Stack---Frontend-Heavy--_R170649-1',
         posted_date='2026-07-29', source='workday:adobe'),
    dict(company='Adobe', title='Software Development Engineer 3 - Frontend', location='Noida', city='Noida',
         work_mode='unspecified', category='Frontend Developer',
         skills=['JavaScript', 'TypeScript', 'Express', 'HTML', 'CSS', 'LLM', 'Generative AI'], experience_text='Not specified',
         min_experience_years=None, max_experience_years=None,
         salary_text='Not disclosed', eligibility="Bachelor's degree; Master's an advantage.",
         description='Adobe is hiring a Software Development Engineer 3 - Frontend in Noida.',
         deadline=None, apply_url='https://adobe.wd5.myworkdayjobs.com/external_experienced/job/Noida/Software-Development-Engineer-3---Frontend_R170811',
         posted_date='2026-07-27', source='workday:adobe'),
    dict(company='Groww', title='SDE II - Backend', location='Bengaluru', city='Bengaluru',
         work_mode='onsite', category='Backend Developer',
         skills=['Java', 'Spring Boot', 'Kafka', 'MySQL', 'Redis'], experience_text='2-4 years',
         min_experience_years=2, max_experience_years=4,
         salary_text='Not disclosed', eligibility="Bachelor's degree (B.Tech/B.E.).",
         description='Groww is hiring an SDE II - Backend in Bengaluru, building high-scale trading systems.',
         deadline=None, apply_url='https://groww.in/careers', posted_date='2026-07-15', source='greenhouse:groww'),
    dict(company='Postman', title='Frontend Engineer - Platform', location='Bengaluru', city='Bengaluru',
         work_mode='hybrid', category='Frontend Developer',
         skills=['React', 'TypeScript', 'Redux', 'Webpack'], experience_text='2-5 years',
         min_experience_years=2, max_experience_years=5,
         salary_text='Not disclosed', eligibility="Bachelor's degree in CS or equivalent.",
         description='Postman is hiring a Frontend Engineer to work on the core API platform UI.',
         deadline=None, apply_url='https://www.postman.com/careers', posted_date='2026-07-18', source='greenhouse:postman'),
    dict(company='Razorpay', title='MERN Stack Developer Intern', location='Bengaluru', city='Bengaluru',
         work_mode='onsite', category='MERN Stack Developer',
         skills=['MongoDB', 'Express', 'React', 'Node.js'], experience_text='0-1 years',
         min_experience_years=0, max_experience_years=1,
         salary_text='₹40,000/month', eligibility='Final-year students or recent graduates.',
         description='Razorpay is hiring a MERN Stack Developer Intern to build internal dashboards.',
         deadline='2026-09-15', apply_url='https://razorpay.com/jobs/', posted_date='2026-08-01', source='greenhouse:razorpay'),
    dict(company='PhonePe', title='Machine Learning Intern', location='Bangalore', city='Bangalore',
         work_mode='onsite', category='Machine Learning Intern',
         skills=['Python', 'PyTorch', 'NLP', 'Pandas'], experience_text='0-1 years',
         min_experience_years=0, max_experience_years=1,
         salary_text='₹50,000/month', eligibility='Pursuing or completed a degree in CS/AI/ML.',
         description='PhonePe is hiring a Machine Learning Intern to work on fraud-detection models.',
         deadline='2026-09-01', apply_url='https://www.phonepe.com/careers/', posted_date='2026-08-03', source='greenhouse:phonepe'),
    dict(company='Zerodha', title='Full Stack Developer Intern', location='Bengaluru', city='Bengaluru',
         work_mode='onsite', category='Full Stack Developer',
         skills=['React', 'Node.js', 'PostgreSQL', 'TypeScript'], experience_text='0-1 years',
         min_experience_years=0, max_experience_years=1,
         salary_text='₹35,000/month', eligibility='Final-year students or recent graduates.',
         description='Zerodha is hiring a Full Stack Developer Intern to build internal trading tools.',
         deadline='2026-09-20', apply_url='https://zerodha.com/careers/', posted_date='2026-08-05', source='greenhouse:zerodha'),
    dict(company='CRED', title='Backend Engineer Intern', location='Bengaluru', city='Bengaluru',
         work_mode='onsite', category='Backend Developer',
         skills=['Java', 'Spring Boot', 'Kafka', 'MySQL'], experience_text='0-1 years',
         min_experience_years=0, max_experience_years=1,
         salary_text='₹45,000/month', eligibility='Final-year students or recent graduates.',
         description='CRED is hiring a Backend Engineer Intern to work on the payments platform.',
         deadline='2026-09-10', apply_url='https://careers.cred.club/', posted_date='2026-08-04', source='greenhouse:cred'),
    dict(company='Swiggy', title='Frontend Developer Intern', location='Bengaluru', city='Bengaluru',
         work_mode='onsite', category='Frontend Developer',
         skills=['React', 'TypeScript', 'CSS', 'Redux'], experience_text='0-1 years',
         min_experience_years=0, max_experience_years=1,
         salary_text='₹40,000/month', eligibility='Final-year students or recent graduates.',
         description='Swiggy is hiring a Frontend Developer Intern to work on the customer ordering app.',
         deadline='2026-09-25', apply_url='https://careers.swiggy.com/', posted_date='2026-08-06', source='greenhouse:swiggy'),
    dict(company='Meesho', title='MERN Stack Developer Intern', location='Bengaluru', city='Bengaluru',
         work_mode='onsite', category='MERN Stack Developer',
         skills=['MongoDB', 'Express', 'React', 'Node.js'], experience_text='0-1 years',
         min_experience_years=0, max_experience_years=1,
         salary_text='₹35,000/month', eligibility='Final-year students or recent graduates.',
         description='Meesho is hiring a MERN Stack Developer Intern to build seller-side tools.',
         deadline='2026-09-18', apply_url='https://careers.meesho.io/', posted_date='2026-08-02', source='greenhouse:meesho'),
    dict(company='Flipkart', title='Software Development Engineer Intern', location='Bengaluru', city='Bengaluru',
         work_mode='onsite', category='Full Stack Developer',
         skills=['Java', 'React', 'Microservices', 'AWS'], experience_text='0-1 years',
         min_experience_years=0, max_experience_years=1,
         salary_text='₹50,000/month', eligibility='Final-year students or recent graduates.',
         description='Flipkart is hiring an SDE Intern to work on the seller platform.',
         deadline='2026-09-30', apply_url='https://www.flipkartcareers.com/', posted_date='2026-08-07', source='greenhouse:flipkart'),
    dict(company='Zomato', title='React Developer Intern', location='Gurugram', city='Gurugram',
         work_mode='onsite', category='React Developer',
         skills=['React', 'Redux', 'JavaScript', 'REST'], experience_text='0-1 years',
         min_experience_years=0, max_experience_years=1,
         salary_text='₹30,000/month', eligibility='Final-year students or recent graduates.',
         description='Zomato is hiring a React Developer Intern to work on the restaurant partner dashboard.',
         deadline='2026-09-12', apply_url='https://www.zomato.com/careers', posted_date='2026-08-01', source='greenhouse:zomato'),
    dict(company='Freshworks', title='Machine Learning Intern', location='Chennai', city='Chennai',
         work_mode='onsite', category='Machine Learning Intern',
         skills=['Python', 'scikit-learn', 'Pandas', 'NLP'], experience_text='0-1 years',
         min_experience_years=0, max_experience_years=1,
         salary_text='₹40,000/month', eligibility='Pursuing or completed a degree in CS/AI/ML.',
         description='Freshworks is hiring a Machine Learning Intern to work on support-ticket automation.',
         deadline='2026-09-22', apply_url='https://www.freshworks.com/company/careers/', posted_date='2026-08-08', source='greenhouse:freshworks'),
    dict(company='Groww', title='Frontend Developer Intern', location='Bengaluru', city='Bengaluru',
         work_mode='onsite', category='Frontend Developer',
         skills=['React', 'TypeScript', 'Webpack', 'CSS'], experience_text='0-1 years',
         min_experience_years=0, max_experience_years=1,
         salary_text='₹35,000/month', eligibility='Final-year students or recent graduates.',
         description='Groww is hiring a Frontend Developer Intern to work on investor-facing UI.',
         deadline='2026-09-16', apply_url='https://groww.in/careers', posted_date='2026-08-05', source='greenhouse:groww'),
    dict(company='Groww', title='Software Development Engineer - Senior', location='Bengaluru', city='Bengaluru',
         work_mode='onsite', category='Backend Developer',
         skills=['Java', 'Microservices', 'Kafka', 'PostgreSQL'], experience_text='8-12 years',
         min_experience_years=8, max_experience_years=12,
         salary_text='Not disclosed', eligibility="Bachelor's degree; Master's an advantage.",
         description='Groww is hiring a Senior SDE to lead backend platform architecture.',
         deadline=None, apply_url='https://groww.in/careers', posted_date='2026-07-25', source='greenhouse:groww'),
    dict(company='Postman', title='Principal Frontend Architect', location='Bengaluru', city='Bengaluru',
         work_mode='hybrid', category='Frontend Developer',
         skills=['React', 'TypeScript', 'Design Systems', 'WebAssembly'], experience_text='12+ years',
         min_experience_years=12, max_experience_years=None,
         salary_text='Not disclosed', eligibility='Extensive experience leading frontend architecture.',
         description='Postman is hiring a Principal Frontend Architect to define the platform UI direction.',
         deadline=None, apply_url='https://www.postman.com/careers', posted_date='2026-07-30', source='greenhouse:postman'),
]


class Command(BaseCommand):
    help = 'Seed the database with sample job listings (idempotent — safe to rerun).'

    def handle(self, *args, **options):
        cat_objs = {}
        for name in CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=name)
            cat_objs[name] = cat

        created = 0
        updated = 0
        for entry in SAMPLE_JOBS:
            entry = dict(entry)
            skills_names = entry.pop('skills')
            category_name = entry.pop('category')
            deadline = entry.pop('deadline')
            posted_date = entry.pop('posted_date')
            company = entry.pop('company')
            title = entry.pop('title')

            job, was_created = Job.objects.update_or_create(
                company=company, title=title,
                defaults={
                    **entry,
                    'category': cat_objs[category_name],
                    'deadline': dt.date.fromisoformat(deadline) if deadline else None,
                    'posted_date': dt.date.fromisoformat(posted_date) if posted_date else None,
                },
            )
            created += was_created
            updated += not was_created

            skills = [Skill.objects.get_or_create(name=s)[0] for s in skills_names]
            job.skills.set(skills)

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete: {created} job(s) created, {updated} updated.'
        ))
