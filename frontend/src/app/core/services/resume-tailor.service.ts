import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { TailorResumeRequest, TailoredResume } from '../models/resume.model';

@Injectable({ providedIn: 'root' })
export class ResumeTailorService {
  constructor(private http: HttpClient) {}

  tailor(request: TailorResumeRequest): Observable<TailoredResume> {
    const form = new FormData();
    if (request.job_slug) form.set('job_slug', request.job_slug);
    if (request.job_description) form.set('job_description', request.job_description);
    if (request.resume_text) form.set('resume_text', request.resume_text);
    if (request.resume_file) form.set('resume_file', request.resume_file);
    return this.http.post<TailoredResume>('/api/tailor-resume/', form);
  }

  history(): Observable<TailoredResume[]> {
    return this.http.get<TailoredResume[]>('/api/tailored-resumes/');
  }

  remove(id: number): Observable<void> {
    return this.http.delete<void>(`/api/tailored-resumes/${id}/`);
  }
}
