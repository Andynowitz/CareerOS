"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getJobs,
  updateJob,
  type Job,
} from "@/lib/jobs-api";
import {
  JOB_STATUSES,
  type JobStatus,
} from "@/lib/job-types";

const STATUS_LABELS: Record<JobStatus, string> = {
  saved: "Saved",
  applied: "Applied",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
};

export default function KanbanPage() {
  const router = useRouter();

  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadJobs() {
      try {
        setIsLoading(true);
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

  async function handleStatusChange(
    jobId: string,
    newStatus: JobStatus,
  ) {
    try {
      setError(null);

      const updatedJob = await updateJob(jobId, {
        status: newStatus,
      });

      setJobs((currentJobs) =>
        currentJobs.map((job) =>
          job.id === jobId ? updatedJob : job,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update job status.",
      );
    }
  }

  if (isLoading) {
    return (
      <main className="p-6">
        <p>Loading jobs...</p>
      </main>
    );
  }

  return (
    <main className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            Application Board
          </h1>

          <p className="text-sm text-gray-500">
            Manage your applications by status.
          </p>
        </div>

        <button
          type="button"
          onClick={() => router.push("/dashboard/jobs")}
          className="rounded border px-4 py-2 text-sm"
        >
          List View
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {JOB_STATUSES.map((status) => {
          const statusJobs = jobs.filter(
            (job) => job.status === status,
          );

          return (
            <section
              key={status}
              className="min-h-64 rounded-lg border bg-gray-50 p-4"
            >
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-semibold">
                  {STATUS_LABELS[status]}
                </h2>

                <span className="rounded-full bg-white px-2 py-1 text-xs">
                  {statusJobs.length}
                </span>
              </div>

              <div className="space-y-3">
                {statusJobs.length === 0 ? (
                  <p className="text-sm text-gray-400">
                    No applications
                  </p>
                ) : (
                  statusJobs.map((job) => (
                    <article
                      key={job.id}
                      className="rounded-lg border bg-white p-4 shadow-sm"
                    >
                      <button
                        type="button"
                        onClick={() =>
                          router.push(
                            `/dashboard/jobs/${job.id}`,
                          )
                        }
                        className="text-left"
                      >
                        <h3 className="font-medium hover:underline">
                          {job.title}
                        </h3>

                        <p className="text-sm text-gray-600">
                          {job.company}
                        </p>

                        {job.location && (
                          <p className="mt-1 text-xs text-gray-500">
                            {job.location}
                          </p>
                        )}
                      </button>

                      <div className="mt-4">
                        <label
                          htmlFor={`status-${job.id}`}
                          className="mb-1 block text-xs text-gray-500"
                        >
                          Change status
                        </label>

                        <select
                          id={`status-${job.id}`}
                          value={job.status}
                          onChange={(event) =>
                            void handleStatusChange(
                              job.id,
                              event.target.value as JobStatus,
                            )
                          }
                          className="w-full rounded border px-2 py-1 text-sm"
                        >
                          {JOB_STATUSES.map(
                            (option) => (
                              <option
                                key={option}
                                value={option}
                              >
                                {STATUS_LABELS[option]}
                              </option>
                            ),
                          )}
                        </select>
                      </div>
                    </article>
                  ))
                )}
              </div>
            </section>
          );
        })}
      </div>
    </main>
  );
}