import { Component, OnInit, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';
import { FavoriteService } from '../../../core/services/favorite.service';
import { JobService } from '../../../core/services/job.service';
import { Category, EXPERIENCE_LEVELS, ExperienceLevel, JobListItem, WorkMode } from '../../../core/models/job.model';
import { JobCardComponent } from '../../../shared/components/job-card/job-card.component';

const PAGE_SIZE = 12;

@Component({
  selector: 'app-job-list',
  standalone: true,
  imports: [FormsModule, JobCardComponent],
  templateUrl: './job-list.component.html',
  styleUrl: './job-list.component.scss',
})
export class JobListComponent implements OnInit {
  jobs = signal<JobListItem[]>([]);
  categories = signal<Category[]>([]);
  count = signal(0);
  page = signal(1);
  loading = signal(false);
  errorMessage = signal<string | null>(null);
  favoriteIdByJob = signal<Map<number, number>>(new Map());

  category = '';
  city = '';
  workMode: WorkMode | '' = '';
  experience: ExperienceLevel | '' = '';
  search = '';

  readonly experienceLevels = EXPERIENCE_LEVELS;

  totalPages = computed(() => Math.max(1, Math.ceil(this.count() / PAGE_SIZE)));

  constructor(
    private jobService: JobService,
    private favoriteService: FavoriteService,
    public auth: AuthService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.jobService.categories().subscribe((cats) => this.categories.set(cats));
    this.loadJobs();
    this.loadFavorites();
  }

  loadJobs(): void {
    this.loading.set(true);
    this.errorMessage.set(null);
    this.jobService
      .list({
        category: this.category,
        city: this.city,
        work_mode: this.workMode,
        experience: this.experience,
        search: this.search,
        page: this.page(),
      })
      .subscribe({
        next: (res) => {
          this.jobs.set(res.results);
          this.count.set(res.count);
          this.loading.set(false);
        },
        error: () => {
          this.errorMessage.set('Could not load jobs. Is the backend running?');
          this.loading.set(false);
        },
      });
  }

  loadFavorites(): void {
    if (!this.auth.isAuthenticated()) return;
    this.favoriteService.list().subscribe((favs) => {
      const map = new Map<number, number>();
      favs.forEach((f) => map.set(f.job.id, f.id));
      this.favoriteIdByJob.set(map);
    });
  }

  applyFilters(): void {
    this.page.set(1);
    this.loadJobs();
  }

  goToPage(p: number): void {
    if (p < 1 || p > this.totalPages()) return;
    this.page.set(p);
    this.loadJobs();
  }

  onFavoriteToggle(job: JobListItem): void {
    if (!this.auth.isAuthenticated()) {
      this.router.navigate(['/login'], { queryParams: { returnUrl: '/' } });
      return;
    }
    const map = this.favoriteIdByJob();
    const existingId = map.get(job.id);
    if (existingId) {
      this.favoriteService.remove(existingId).subscribe(() => {
        const next = new Map(map);
        next.delete(job.id);
        this.favoriteIdByJob.set(next);
      });
    } else {
      this.favoriteService.add(job.id).subscribe((fav) => {
        const next = new Map(map);
        next.set(job.id, fav.id);
        this.favoriteIdByJob.set(next);
      });
    }
  }
}
