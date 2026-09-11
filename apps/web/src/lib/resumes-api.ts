export interface ResumeVersion {
  id: string;
  resume_id: string;
  version: number;
  filename: string;
  content_type: string;
  size_bytes: number;
  extracted_text: string | null;
  created_at: string;
}

export interface Resume {
  id: string;
  user_id: string;
  name: string;
  current_version: number;
  created_at: string;
  updated_at: string;
}

export interface ResumeDetail extends Resume {
  versions: ResumeVersion[];
}

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const API_V1_URL = `${API_URL}/api/v1`;

async function handleResponse<T>(
  response: Response,
): Promise<T> {
  if (!response.ok) {
    const body = (await response
      .json()
      .catch(() => null)) as { detail?: string } | null;

    throw new Error(
      body?.detail ??
        `API request failed: ${response.status}`,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function getResumes(): Promise<Resume[]> {
  const response = await fetch(
    `${API_V1_URL}/resumes`,
    {
      credentials: "include",
    },
  );

  return handleResponse<Resume[]>(response);
}

export async function getResume(
  id: string,
): Promise<ResumeDetail> {
  const response = await fetch(
    `${API_V1_URL}/resumes/${id}`,
    {
      credentials: "include",
    },
  );

  return handleResponse<ResumeDetail>(response);
}

export async function uploadResume(
  file: File,
  name?: string,
): Promise<ResumeDetail> {
  const form = new FormData();

  form.append("file", file);

  if (name?.trim()) {
    form.append("name", name.trim());
  }

  const response = await fetch(
    `${API_V1_URL}/resumes`,
    {
      method: "POST",
      credentials: "include",
      body: form,
    },
  );

  return handleResponse<ResumeDetail>(response);
}

export async function uploadResumeVersion(
  id: string,
  file: File,
): Promise<ResumeDetail> {
  const form = new FormData();

  form.append("file", file);

  const response = await fetch(
    `${API_V1_URL}/resumes/${id}/versions`,
    {
      method: "POST",
      credentials: "include",
      body: form,
    },
  );

  return handleResponse<ResumeDetail>(response);
}

export async function deleteResume(
  id: string,
): Promise<void> {
  const response = await fetch(
    `${API_V1_URL}/resumes/${id}`,
    {
      method: "DELETE",
      credentials: "include",
    },
  );

  await handleResponse<void>(response);
}

export function getResumeDownloadUrl(
  id: string,
  version: number,
): string {
  return `${API_V1_URL}/resumes/${id}/versions/${version}/download`;
}