"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  getJobs,
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

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString();
}

export default function DashboardPage() {
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
            : "Failed to load dashboard.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    void loadJobs();
  }, []);

  if (isLoading) {
    return (
      <main className="p-6">
        <h1 className="text-2xl font-bold">
          Dashboard
        </h1>

        <p className="mt-4 text-sm text-gray-500">
          Loading dashboard...
        </p>
      </main>
    );
  }

  const counts = JOB_STATUSES.reduce(
    (result, status) => {
      result[status] = jobs.filter(
        (job) => job.status === status,
      ).length;

      return result;
    },
    {} as Record<JobStatus, number>,
  );

  const recentJobs = [...jobs]
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() -
        new Date(a.created_at).getTime(),
    )
    .slice(0, 5);

  return (
    <main className="p-6">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            Application Dashboard
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            Overview of your job applications.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() =>
              router.push("/dashboard/jobs")
            }
            className="rounded border px-4 py-2 text-sm"
          >
            Applications
          </button>

          <button
            type="button"
            onClick={() =>
              router.push("/dashboard/kanban")
            }
            className="rounded border px-4 py-2 text-sm"
          >
            Kanban
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <section className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border bg-white p-5">
          <p className="text-sm text-gray-500">
            Total Applications
          </p>

          <p className="mt-2 text-3xl font-bold">
            {jobs.length}
          </p>
        </div>

        <div className="rounded-lg border bg-white p-5">
          <p className="text-sm text-gray-500">
            Applied
          </p>

          <p className="mt-2 text-3xl font-bold">
            {counts.applied}
          </p>
        </div>

        <div className="rounded-lg border bg-white p-5">
          <p className="text-sm text-gray-500">
            Interviews
          </p>

          <p className="mt-2 text-3xl font-bold">
            {counts.interview}
          </p>
        </div>

        <div className="rounded-lg border bg-white p-5">
          <p className="text-sm text-gray-500">
            Offers
          </p>

          <p className="mt-2 text-3xl font-bold">
            {counts.offer}
          </p>
        </div>
      </section>

      <section className="mb-8 rounded-lg border bg-white p-5">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">
              Application Pipeline
            </h2>

            <p className="text-sm text-gray-500">
              Current distribution of your applications.
            </p>
          </div>

          <button
            type="button"
            onClick={() =>
              router.push("/dashboard/kanban")
            }
            className="text-sm underline"
          >
            Open Kanban
          </button>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {JOB_STATUSES.map((status) => (
            <div
              key={status}
              className="rounded border p-4"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">
                  {STATUS_LABELS[status]}
                </span>

                <span className="text-lg font-bold">
                  {counts[status]}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border bg-white p-5">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">
              Recent Applications
            </h2>

            <p className="text-sm text-gray-500">
              Your five most recently created applications.
            </p>
          </div>

          <button
            type="button"
            onClick={() =>
              router.push("/dashboard/jobs")
            }
            className="text-sm underline"
          >
            View all
          </button>
        </div>

        {recentJobs.length === 0 ? (
          <p className="text-sm text-gray-500">
            No applications yet.
          </p>
        ) : (
          <div className="divide-y">
            {recentJobs.map((job) => (
              <button
                key={job.id}
                type="button"
                onClick={() =>
                  router.push(
                    `/dashboard/jobs/${job.id}`,
                  )
                }
                className="flex w-full items-center justify-between gap-4 py-4 text-left hover:bg-gray-50"
              >
                <div>
                  <p className="font-medium">
                    {job.title}
                  </p>

                  <p className="text-sm text-gray-600">
                    {job.company}
                  </p>

                  {job.location && (
                    <p className="text-xs text-gray-500">
                      {job.location}
                    </p>
                  )}
                </div>

                <div className="shrink-0 text-right">
                  <p className="text-sm font-medium">
                    {STATUS_LABELS[job.status]}
                  </p>

                  <p className="text-xs text-gray-500">
                    {formatDate(job.created_at)}
                  </p>
                </div>
              </button>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}