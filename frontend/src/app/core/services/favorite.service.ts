import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Favorite } from '../models/job.model';

@Injectable({ providedIn: 'root' })
export class FavoriteService {
  constructor(private http: HttpClient) {}

  list(): Observable<Favorite[]> {
    return this.http.get<Favorite[]>('/api/favorites/');
  }

  add(jobId: number): Observable<Favorite> {
    return this.http.post<Favorite>('/api/favorites/', { job_id: jobId });
  }

  remove(favoriteId: number): Observable<void> {
    return this.http.delete<void>(`/api/favorites/${favoriteId}/`);
  }
}
