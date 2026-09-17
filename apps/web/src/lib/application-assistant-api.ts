export interface ApplicationChecklistItem {
  item: string;
  completed: boolean;
}

export interface ApplicationAssistant {
  job_id: string;
  status: string;
  missing_information: string[];
  checklist: ApplicationChecklistItem[];
  next_actions: string[];
  follow_up_needed: boolean;
  last_activity_at: string | null;
  days_since_activity: number | null;
}

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const API_V1_URL = `${API_URL}/api/v1`;

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function getApplicationAssistant(
  jobId: string,
): Promise<ApplicationAssistant> {
  const response = await fetch(
    `${API_V1_URL}/jobs/${jobId}/assistant`,
    {
      credentials: "include",
    },
  );

  return handleResponse<ApplicationAssistant>(response);
}