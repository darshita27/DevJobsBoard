import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./features/jobs/job-list/job-list.component').then((m) => m.JobListComponent),
  },
  {
    path: 'jobs/:slug',
    loadComponent: () => import('./features/jobs/job-detail/job-detail.component').then((m) => m.JobDetailComponent),
  },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/register/register.component').then((m) => m.RegisterComponent),
  },
  {
    path: 'favorites',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/favorites/favorites-page/favorites-page.component').then((m) => m.FavoritesPageComponent),
  },
  {
    path: 'tailor-resume',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/resume/tailor-resume-page/tailor-resume-page.component').then(
        (m) => m.TailorResumePageComponent,
      ),
  },
  {
    path: 'jobs/:slug/tailor-resume',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/resume/tailor-resume-page/tailor-resume-page.component').then(
        (m) => m.TailorResumePageComponent,
      ),
  },
  {
    path: 'my-tailored-resumes',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/resume/tailored-resumes-page/tailored-resumes-page.component').then(
        (m) => m.TailoredResumesPageComponent,
      ),
  },
  { path: '**', redirectTo: '' },
];
