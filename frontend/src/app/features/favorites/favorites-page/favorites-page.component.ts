import { Component, OnInit, signal } from '@angular/core';

import { FavoriteService } from '../../../core/services/favorite.service';
import { Favorite } from '../../../core/models/job.model';
import { JobCardComponent } from '../../../shared/components/job-card/job-card.component';

@Component({
  selector: 'app-favorites-page',
  standalone: true,
  imports: [JobCardComponent],
  templateUrl: './favorites-page.component.html',
  styleUrl: './favorites-page.component.scss',
})
export class FavoritesPageComponent implements OnInit {
  favorites = signal<Favorite[]>([]);
  loading = signal(true);

  constructor(private favoriteService: FavoriteService) {}

  ngOnInit(): void {
    this.favoriteService.list().subscribe((favs) => {
      this.favorites.set(favs);
      this.loading.set(false);
    });
  }

  remove(favoriteId: number): void {
    this.favoriteService.remove(favoriteId).subscribe(() => {
      this.favorites.set(this.favorites().filter((f) => f.id !== favoriteId));
    });
  }
}
