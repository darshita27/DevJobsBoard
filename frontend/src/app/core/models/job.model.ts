export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Category {
  id: number;
  name: string;
  slug: string;
}

export interface Skill {
  id: number;
  name: string;
}

export type WorkMode = 'remote' | 'onsite' | 'hybrid' | 'unspecified';

export type ExperienceLevel = 'fresher' | 'junior' | 'mid' | 'senior' | 'lead';

export const EXPERIENCE_LEVELS: { value: ExperienceLevel; label: string }[] = [
  { value: 'fresher', label: 'Fresher / Intern (0-1 yrs)' },
  { value: 'junior', label: 'Junior (1-3 yrs)' },
  { value: 'mid', label: 'Mid-level (3-6 yrs)' },
  { value: 'senior', label: 'Senior (6-10 yrs)' },
  { value: 'lead', label: 'Lead / Principal (10+ yrs)' },
];

export interface JobListItem {
  id: number;
  slug: string;
  title: string;
  company: string;
  location: string;
  city: string;
  work_mode: WorkMode;
  category: Category | null;
  salary_text: string;
  experience_text: string;
  deadline: string | null;
  posted_date: string | null;
}

export interface JobDetail extends JobListItem {
  skills: Skill[];
  eligibility: string;
  description: string;
  apply_url: string;
  source: string;
  is_active: boolean;
  is_favorited: boolean;
}

export interface Favorite {
  id: number;
  job: JobListItem;
  created_at: string;
}

export interface JobFilters {
  category?: string;
  city?: string;
  work_mode?: WorkMode | '';
  experience?: ExperienceLevel | '';
  search?: string;
  page?: number;
}
