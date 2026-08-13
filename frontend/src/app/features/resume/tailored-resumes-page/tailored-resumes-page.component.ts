import { DatePipe } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ResumeTailorService } from '../../../core/services/resume-tailor.service';
import { TailoredResume } from '../../../core/models/resume.model';

@Component({
  selector: 'app-tailored-resumes-page',
  standalone: true,
  imports: [RouterLink, DatePipe],
  templateUrl: './tailored-resumes-page.component.html',
  styleUrl: './tailored-resumes-page.component.scss',
})
export class TailoredResumesPageComponent implements OnInit {
  items = signal<TailoredResume[]>([]);
  loading = signal(true);

  constructor(private resumeTailorService: ResumeTailorService) {}

  ngOnInit(): void {
    this.resumeTailorService.history().subscribe((items) => {
      this.items.set(items);
      this.loading.set(false);
    });
  }

  remove(id: number): void {
    this.resumeTailorService.remove(id).subscribe(() => {
      this.items.set(this.items().filter((i) => i.id !== id));
    });
  }

  download(item: TailoredResume): void {
    const blob = new Blob([item.tailored_resume], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const baseName = (item.job_title || 'tailored-resume').toLowerCase().replace(/[^a-z0-9]+/g, '-');
    a.href = url;
    a.download = `resume-${baseName}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }
}
