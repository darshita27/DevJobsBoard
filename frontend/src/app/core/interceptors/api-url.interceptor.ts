import { HttpInterceptorFn } from '@angular/common/http';

import { environment } from '../../../environments/environment';

export const apiUrlInterceptor: HttpInterceptorFn = (req, next) => {
  if (environment.apiUrl && req.url.startsWith('/api/')) {
    return next(req.clone({ url: environment.apiUrl + req.url }));
  }
  return next(req);
};
