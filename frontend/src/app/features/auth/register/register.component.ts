import { Component, inject, signal } from '@angular/core';
import { AbstractControl, FormBuilder, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';

function passwordsMatch(control: AbstractControl): ValidationErrors | null {
  const password = control.get('password')?.value;
  const confirm = control.get('confirmPassword')?.value;
  return password && confirm && password !== confirm ? { mismatch: true } : null;
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss',
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);

  form = this.fb.group(
    {
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required],
    },
    { validators: passwordsMatch },
  );

  submitting = signal(false);
  errorMessage = signal<string | null>(null);

  submit(): void {
    if (this.form.invalid) return;

    this.submitting.set(true);
    this.errorMessage.set(null);
    const { username, email, password } = this.form.getRawValue();

    this.auth.register({ username: username!, email: email!, password: password! }).subscribe({
      next: () => {
        this.auth.login(username!, password!).subscribe({
          next: () => this.router.navigateByUrl('/'),
          error: () => this.router.navigateByUrl('/login'),
        });
      },
      error: (err) => {
        const detail = err?.error?.username?.[0] || err?.error?.email?.[0] || err?.error?.password?.[0];
        this.errorMessage.set(detail || 'Could not create account. Please check your details.');
        this.submitting.set(false);
      },
    });
  }
}
