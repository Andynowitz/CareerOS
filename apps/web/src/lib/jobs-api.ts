import type { JobStatus } from "./job-types";

export interface Job {
  id: string;
  user_id: string;
  title: string;
  company: string;
  location: string | null;
  url: string | null;
  description: string | null;
  status: JobStatus;
  created_at: string;
  updated_at: string;
}

export interface CreateJobInput {
  title: string;
  company: string;
  location?: string | null;
  url?: string | null;
  description?: string | null;
  status?: JobStatus;
}

export interface UpdateJobInput {
  title?: string;
  company?: string;
  location?: string | null;
  url?: string | null;
  description?: string | null;
  status?: JobStatus;
}

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const API_V1_URL = `${API_URL}/api/v1`;

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function getJobs(): Promise<Job[]> {
  const response = await fetch(`${API_V1_URL}/jobs`, {
    credentials: "include",
  });

  return handleResponse<Job[]>(response);
}

export async function getJob(id: string): Promise<Job> {
  const response = await fetch(`${API_V1_URL}/jobs/${id}`, {
    credentials: "include",
  });

  return handleResponse<Job>(response);
}


export async function createJob(data: CreateJobInput): Promise<Job> {
  const response = await fetch(`${API_V1_URL}/jobs`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return handleResponse<Job>(response);
}

export async function updateJob(
  id: string,
  data: UpdateJobInput,
): Promise<Job> {
  const response = await fetch(`${API_V1_URL}/jobs/${id}`, {
    method: "PATCH",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return handleResponse<Job>(response);
}


export async function deleteJob(id: string): Promise<void> {
  const response = await fetch(`${API_V1_URL}/jobs/${id}`, {
    method: "DELETE",
    credentials: "include",
  });

  await handleResponse<void>(response);
}


export interface AnalysisTaskResponse {
  task_id: string;
  status: string;
}

export interface JobAnalysis {
  id: string;
  job_id: string;
  required_skills: string[];
  preferred_skills: string[];
  responsibilities: string[];
  experience_requirements: string | null;
  education_requirements: string | null;
  keywords: string[];
  salary_information: Record<string, string | number | null> | null;
  raw_analysis: Record<string, unknown> | null;
  created_at: string;
}

export async function analyzeJob(
  id: string,
): Promise<AnalysisTaskResponse> {
  const response = await fetch(`${API_V1_URL}/jobs/${id}/analysis`, {
    method: "POST",
    credentials: "include",
  });

  return handleResponse<AnalysisTaskResponse>(response);
}

export async function getJobAnalysis(
  id: string,
): Promise<JobAnalysis> {
  const response = await fetch(`${API_V1_URL}/jobs/${id}/analysis`, {
    credentials: "include",
  });

  return handleResponse<JobAnalysis>(response);
}

export async function getJobAnalysisStatus(
  jobId: string,
  taskId: string,
): Promise<AnalysisTaskResponse> {
  const response = await fetch(
    `${API_V1_URL}/jobs/${jobId}/analysis/status/${taskId}`,
    {
      credentials: "include",
    },
  );

  return handleResponse<AnalysisTaskResponse>(response);
}


export interface JobMatch {
  id: string;
  job_id: string;
  resume_id: string;
  score: number;

  required_skills_score: number;
  preferred_skills_score: number;
  experience_score: number;
  education_score: number;
  keywords_score: number;

  matched_required_skills: string[];
  missing_required_skills: string[];
  matched_preferred_skills: string[];
  missing_preferred_skills: string[];

  explanations: string[];

  created_at: string;
}

export interface JobMatchHistory {
  matches: JobMatch[];
}

export async function createJobMatch(
  jobId: string,
  resumeId: string,
): Promise<JobMatch> {
  const response = await fetch(
    `${API_V1_URL}/jobs/${jobId}/matches`,
    {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        resume_id: resumeId,
      }),
    },
  );

  return handleResponse<JobMatch>(response);
}

export async function getLatestJobMatch(
  jobId: string,
  resumeId: string,
): Promise<JobMatch> {
  const response = await fetch(
    `${API_V1_URL}/jobs/${jobId}/matches/latest?resume_id=${encodeURIComponent(resumeId)}`,
    {
      credentials: "include",
    },
  );

  return handleResponse<JobMatch>(response);
}

export async function getJobMatchHistory(
  jobId: string,
  resumeId: string,
): Promise<JobMatchHistory> {
  const response = await fetch(
    `${API_V1_URL}/jobs/${jobId}/matches/history?resume_id=${encodeURIComponent(resumeId)}`,
    {
      credentials: "include",
    },
  );

  return handleResponse<JobMatchHistory>(response);
}