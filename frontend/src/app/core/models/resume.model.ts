export interface TailoredResume {
  id: number;
  job_slug: string | null;
  job_title: string;
  company: string;
  tailored_resume: string;
  summary_of_changes: string[];
  matched_keywords: string[];
  ats_tips: string[];
  created_at: string;
}

export interface TailorResumeRequest {
  job_slug?: string;
  job_description?: string;
  resume_text?: string;
  resume_file?: File;
}
