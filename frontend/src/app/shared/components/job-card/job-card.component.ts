import { Component, EventEmitter, Input, Output } from '@angular/core';
import { RouterLink } from '@angular/router';

import { JobListItem } from '../../../core/models/job.model';

@Component({
  selector: 'app-job-card',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './job-card.component.html',
  styleUrl: './job-card.component.scss',
})
export class JobCardComponent {
  @Input({ required: true }) job!: JobListItem;
  @Input() showFavoriteButton = false;
  @Input() isFavorited = false;
  @Output() favoriteToggle = new EventEmitter<JobListItem>();

  readonly workModeLabel: Record<string, string> = {
    remote: 'Remote',
    onsite: 'On-site',
    hybrid: 'Hybrid',
    unspecified: 'Not specified',
  };
}
