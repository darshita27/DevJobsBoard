import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { JobService } from '../../../core/services/job.service';
import { ResumeTailorService } from '../../../core/services/resume-tailor.service';
import { JobDetail } from '../../../core/models/job.model';
import { TailoredResume } from '../../../core/models/resume.model';

type InputMode = 'paste' | 'file';

@Component({
  selector: 'app-tailor-resume-page',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './tailor-resume-page.component.html',
  styleUrl: './tailor-resume-page.component.scss',
})
export class TailorResumePageComponent implements OnInit {
  jobSlug: string | null = null;
  job = signal<JobDetail | null>(null);
  loadingJob = signal(false);

  inputMode = signal<InputMode>('paste');
  jobDescription = '';
  resumeText = '';
  resumeFile: File | null = null;
  resumeFileName = signal<string>('');

  submitting = signal(false);
  errorMsg = signal<string | null>(null);
  result = signal<TailoredResume | null>(null);
  copied = signal(false);

  constructor(
    private route: ActivatedRoute,
    private jobService: JobService,
    private resumeTailorService: ResumeTailorService,
  ) {}

  ngOnInit(): void {
    this.jobSlug = this.route.snapshot.paramMap.get('slug');
    if (this.jobSlug) {
      this.loadingJob.set(true);
      this.jobService.detail(this.jobSlug).subscribe({
        next: (job) => {
          this.job.set(job);
          this.loadingJob.set(false);
        },
        error: () => this.loadingJob.set(false),
      });
    }
  }

  setInputMode(mode: InputMode): void {
    this.inputMode.set(mode);
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    this.resumeFile = file;
    this.resumeFileName.set(file ? file.name : '');
  }

  canSubmit(): boolean {
    const hasJd = !!this.jobSlug || this.jobDescription.trim().length > 0;
    const hasResume = this.inputMode() === 'paste' ? this.resumeText.trim().length > 0 : !!this.resumeFile;
    return hasJd && hasResume && !this.submitting();
  }

  submit(): void {
    if (!this.canSubmit()) return;
    this.submitting.set(true);
    this.errorMsg.set(null);
    this.result.set(null);

    this.resumeTailorService
      .tailor({
        job_slug: this.jobSlug ?? undefined,
        job_description: this.jobSlug ? undefined : this.jobDescription.trim(),
        resume_text: this.inputMode() === 'paste' ? this.resumeText.trim() : undefined,
        resume_file: this.inputMode() === 'file' ? this.resumeFile ?? undefined : undefined,
      })
      .subscribe({
        next: (res) => {
          this.result.set(res);
          this.submitting.set(false);
        },
        error: (err) => {
          this.errorMsg.set(err?.error?.detail || 'Something went wrong while tailoring your resume.');
          this.submitting.set(false);
        },
      });
  }

  copyToClipboard(): void {
    const text = this.result()?.tailored_resume;
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
      this.copied.set(true);
      setTimeout(() => this.copied.set(false), 2000);
    });
  }

  download(): void {
    const res = this.result();
    if (!res) return;
    const blob = new Blob([res.tailored_resume], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const baseName = (res.job_title || 'tailored-resume').toLowerCase().replace(/[^a-z0-9]+/g, '-');
    a.href = url;
    a.download = `resume-${baseName}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  startOver(): void {
    this.result.set(null);
    this.errorMsg.set(null);
  }
}
