import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  form = this.fb.group({
    username: ['', Validators.required],
    password: ['', Validators.required],
  });

  submitting = signal(false);
  errorMessage = signal<string | null>(null);

  submit(): void {
    if (this.form.invalid) return;

    this.submitting.set(true);
    this.errorMessage.set(null);
    const { username, password } = this.form.getRawValue();

    this.auth.login(username!, password!).subscribe({
      next: () => {
        const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl') || '/';
        this.router.navigateByUrl(returnUrl);
      },
      error: () => {
        this.errorMessage.set('Invalid username or password.');
        this.submitting.set(false);
      },
    });
  }
}
