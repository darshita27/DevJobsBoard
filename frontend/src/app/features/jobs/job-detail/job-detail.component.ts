import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';
import { FavoriteService } from '../../../core/services/favorite.service';
import { JobService } from '../../../core/services/job.service';
import { JobDetail } from '../../../core/models/job.model';

@Component({
  selector: 'app-job-detail',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './job-detail.component.html',
  styleUrl: './job-detail.component.scss',
})
export class JobDetailComponent implements OnInit {
  job = signal<JobDetail | null>(null);
  loading = signal(true);
  notFound = signal(false);
  favoriteId = signal<number | null>(null);

  readonly workModeLabel: Record<string, string> = {
    remote: 'Remote',
    onsite: 'On-site',
    hybrid: 'Hybrid',
    unspecified: 'Not specified',
  };

  constructor(
    private route: ActivatedRoute,
    private jobService: JobService,
    private favoriteService: FavoriteService,
    public auth: AuthService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    const slug = this.route.snapshot.paramMap.get('slug');
    if (!slug) {
      this.notFound.set(true);
      this.loading.set(false);
      return;
    }
    this.jobService.detail(slug).subscribe({
      next: (job) => {
        this.job.set(job);
        this.loading.set(false);
        this.syncFavoriteState();
      },
      error: () => {
        this.notFound.set(true);
        this.loading.set(false);
      },
    });
  }

  private syncFavoriteState(): void {
    if (!this.auth.isAuthenticated()) return;
    this.favoriteService.list().subscribe((favs) => {
      const match = favs.find((f) => f.job.id === this.job()?.id);
      this.favoriteId.set(match ? match.id : null);
    });
  }

  toggleFavorite(): void {
    if (!this.auth.isAuthenticated()) {
      this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
      return;
    }
    const job = this.job();
    if (!job) return;

    const currentFavId = this.favoriteId();
    if (currentFavId) {
      this.favoriteService.remove(currentFavId).subscribe(() => this.favoriteId.set(null));
    } else {
      this.favoriteService.add(job.id).subscribe((fav) => this.favoriteId.set(fav.id));
    }
  }
}
