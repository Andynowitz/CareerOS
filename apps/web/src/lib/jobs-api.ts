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