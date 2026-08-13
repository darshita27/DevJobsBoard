import { HttpClient } from '@angular/common/http';
import { Injectable, computed, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { RegisterPayload, TokenPair, User } from '../models/user.model';

const ACCESS_KEY = 'devjobs_access';
const REFRESH_KEY = 'devjobs_refresh';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly currentUserSignal = signal<User | null>(null);
  readonly currentUser = this.currentUserSignal.asReadonly();
  readonly isAuthenticated = computed(() => !!this.accessToken);

  constructor(private http: HttpClient) {}

  get accessToken(): string | null {
    return localStorage.getItem(ACCESS_KEY);
  }

  get refreshToken(): string | null {
    return localStorage.getItem(REFRESH_KEY);
  }

  register(payload: RegisterPayload): Observable<User> {
    return this.http.post<User>('/api/auth/register/', payload);
  }

  login(username: string, password: string): Observable<TokenPair> {
    return this.http.post<TokenPair>('/api/auth/token/', { username, password }).pipe(
      tap((tokens) => this.storeTokens(tokens)),
      tap(() => this.loadCurrentUser().subscribe()),
    );
  }

  loadCurrentUser(): Observable<User> {
    return this.http.get<User>('/api/auth/me/').pipe(tap((user) => this.currentUserSignal.set(user)));
  }

  refreshAccessToken(): Observable<TokenPair> {
    return this.http
      .post<TokenPair>('/api/auth/token/refresh/', { refresh: this.refreshToken })
      .pipe(tap((tokens) => this.storeTokens(tokens)));
  }

  logout(): void {
    const refresh = this.refreshToken;
    if (refresh) {
      this.http.post('/api/auth/token/blacklist/', { refresh }).subscribe({ error: () => undefined });
    }
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    this.currentUserSignal.set(null);
  }

  private storeTokens(tokens: TokenPair): void {
    localStorage.setItem(ACCESS_KEY, tokens.access);
    if (tokens.refresh) {
      localStorage.setItem(REFRESH_KEY, tokens.refresh);
    }
  }
}
