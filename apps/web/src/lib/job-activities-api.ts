export type JobActivityType =
  | "created"
  | "status_changed"
  | "note"
  | "email"
  | "phone_call"
  | "interview"
  | "offer"
  | "rejection"
  | "other";

export interface JobActivity {
  id: string;
  job_id: string;
  user_id: string;
  type: JobActivityType;
  description: string | null;
  old_status: string | null;
  new_status: string | null;
  created_at: string;
}

export interface CreateJobActivityInput {
  type: JobActivityType;
  description?: string | null;
}

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const API_V1_URL = `${API_URL}/api/v1`;

async function handleResponse<T>(
  response: Response,
): Promise<T> {
  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status}`,
    );
  }

  return response.json() as Promise<T>;
}

export async function getJobActivities(
  jobId: string,
): Promise<JobActivity[]> {
  const response = await fetch(
    `${API_V1_URL}/jobs/${jobId}/activities`,
    {
      credentials: "include",
    },
  );

  return handleResponse<JobActivity[]>(response);
}

export async function createJobActivity(
  jobId: string,
  data: CreateJobActivityInput,
): Promise<JobActivity> {
  const response = await fetch(
    `${API_V1_URL}/jobs/${jobId}/activities`,
    {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    },
  );

  return handleResponse<JobActivity>(response);
}