import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, switchMap, throwError } from 'rxjs';

import { AuthService } from '../services/auth.service';

const isAuthEndpoint = (url: string) => url.includes('/api/auth/token/');

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  const token = auth.accessToken;
  const authedReq = token && !isAuthEndpoint(req.url)
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;

  return next(authedReq).pipe(
    catchError((err: unknown) => {
      if (
        err instanceof HttpErrorResponse &&
        err.status === 401 &&
        auth.refreshToken &&
        !isAuthEndpoint(req.url)
      ) {
        return auth.refreshAccessToken().pipe(
          switchMap((tokens) =>
            next(req.clone({ setHeaders: { Authorization: `Bearer ${tokens.access}` } })),
          ),
          catchError((refreshErr) => {
            auth.logout();
            router.navigate(['/login']);
            return throwError(() => refreshErr);
          }),
        );
      }
      return throwError(() => err);
    }),
  );
};
