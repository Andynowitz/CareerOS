"use client";

import { useEffect, useState } from "react";

import { getJobs, type Job } from "@/lib/jobs-api";
import { JOB_STATUSES, type JobStatus } from "@/lib/job-types";

const STATUS_LABELS: Record<JobStatus, string> = {
  saved: "Saved",
  applied: "Applied",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
};

export default function KanbanPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadJobs() {
      try {
        setError(null);

        const data = await getJobs();

        setJobs(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load jobs.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    void loadJobs();
  }, []);

  if (isLoading) {
    return (
      <main className="p-8">
        <h1 className="text-2xl font-semibold">Kanban</h1>
        <p className="mt-4 text-muted-foreground">
          Loading jobs...
        </p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="p-8">
        <h1 className="text-2xl font-semibold">Kanban</h1>
        <p className="mt-4 text-destructive">{error}</p>
      </main>
    );
  }

  return (
    <main className="p-8">
      <div>
        <h1 className="text-2xl font-semibold">Kanban</h1>
        <p className="mt-1 text-muted-foreground">
          Manage your job applications by status.
        </p>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {JOB_STATUSES.map((status) => (
          <KanbanColumn
            key={status}
            status={status}
            jobs={jobs}
          />
        ))}
      </div>
    </main>
  );
}

interface KanbanColumnProps {
  status: JobStatus;
  jobs: Job[];
}

function KanbanColumn({
  status,
  jobs,
}: KanbanColumnProps) {
  const jobsForStatus = jobs.filter(
    (job) => job.status === status,
  );

  return (
    <section className="min-h-[500px] rounded-lg border bg-muted/30 p-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold">
          {STATUS_LABELS[status]}
        </h2>

        <span className="rounded-full border px-2 py-1 text-xs">
          {jobsForStatus.length}
        </span>
      </div>

      <div className="mt-4 min-h-[420px] space-y-3">
        {jobsForStatus.length === 0 ? (
          <div className="rounded-md border border-dashed p-4">
            <p className="text-center text-sm text-muted-foreground">
              No jobs
            </p>
          </div>
        ) : (
          jobsForStatus.map((job) => (
            <article
              key={job.id}
              className="rounded-md border bg-background p-4 shadow-sm"
            >
              <h3 className="font-medium">{job.title}</h3>

              <p className="mt-1 text-sm text-muted-foreground">
                {job.company}
              </p>

              {job.location && (
                <p className="mt-1 text-xs text-muted-foreground">
                  {job.location}
                </p>
              )}
            </article>
          ))
        )}
      </div>
    </section>
  );
}