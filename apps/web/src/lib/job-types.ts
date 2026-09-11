export const JOB_STATUSES = [
  "saved",
  "applied",
  "interview",
  "offer",
  "rejected",
  "withdrawn",
] as const;

export type JobStatus = (typeof JOB_STATUSES)[number];