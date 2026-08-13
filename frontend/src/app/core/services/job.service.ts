import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Category, JobDetail, JobFilters, JobListItem, Paginated } from '../models/job.model';

@Injectable({ providedIn: 'root' })
export class JobService {
  constructor(private http: HttpClient) {}

  list(filters: JobFilters): Observable<Paginated<JobListItem>> {
    let params = new HttpParams();
    if (filters.category) params = params.set('category', filters.category);
    if (filters.city) params = params.set('city', filters.city);
    if (filters.work_mode) params = params.set('work_mode', filters.work_mode);
    if (filters.experience) params = params.set('experience', filters.experience);
    if (filters.search) params = params.set('search', filters.search);
    if (filters.page) params = params.set('page', filters.page);
    return this.http.get<Paginated<JobListItem>>('/api/jobs/', { params });
  }

  detail(slug: string): Observable<JobDetail> {
    return this.http.get<JobDetail>(`/api/jobs/${slug}/`);
  }

  categories(): Observable<Category[]> {
    return this.http.get<Category[]>('/api/categories/');
  }
}
