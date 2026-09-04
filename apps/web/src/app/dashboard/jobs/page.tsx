"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  getJobs,
  updateJob,
  deleteJob,
  type Job,
} from "@/lib/jobs-api";

import {
  JOB_STATUSES,
  type JobStatus,
} from "@/lib/job-types";

import JobForm from "./job-form";

type SortOption =
  | "newest"
  | "oldest"
  | "title-asc"
  | "title-desc"
  | "company-asc"
  | "company-desc";

const SORT_OPTIONS: {
  value: SortOption;
  label: string;
}[] = [
  { value: "newest", label: "Newest first" },
  { value: "oldest", label: "Oldest first" },
  { value: "title-asc", label: "Title A-Z" },
  { value: "title-desc", label: "Title Z-A" },
  { value: "company-asc", label: "Company A-Z" },
  { value: "company-desc", label: "Company Z-A" },
];

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [editingJob, setEditingJob] = useState<Job | null>(null);
  const [deletingJobId, setDeletingJobId] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<JobStatus | "all">(
    "all",
  );

  const [sortOption, setSortOption] =
    useState<SortOption>("newest");

  const router = useRouter();
  
  async function loadJobs() {
    try {
      setError(null);

      const data = await getJobs();

      setJobs(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load jobs.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function handleStatusChange(
    job: Job,
    status: JobStatus,
  ) {
    try {
      setError(null);

      const updatedJob = await updateJob(job.id, {
        status,
      });

      setJobs((currentJobs) =>
        currentJobs.map((currentJob) =>
          currentJob.id === updatedJob.id
            ? updatedJob
            : currentJob,
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

  async function handleDelete(job: Job) {
    const confirmed = window.confirm(
      `Delete "${job.title}" at ${job.company}?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingJobId(job.id);
      setError(null);

      await deleteJob(job.id);

      setJobs((currentJobs) =>
        currentJobs.filter((currentJob) => currentJob.id !== job.id),
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to delete job.",
      );
    } finally {
      setDeletingJobId(null);
    }
  }

  useEffect(() => {
    void loadJobs();
  }, []);

  const normalizedSearchQuery = searchQuery.trim().toLowerCase();

  const filteredJobs = jobs.filter((job) => {
    const matchesSearch =
      !normalizedSearchQuery ||
      job.title.toLowerCase().includes(normalizedSearchQuery) ||
      job.company.toLowerCase().includes(normalizedSearchQuery) ||
      (job.location?.toLowerCase().includes(normalizedSearchQuery) ??
        false);

    const matchesStatus =
      statusFilter === "all" || job.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const sortedJobs = [...filteredJobs].sort((a, b) => {
    switch (sortOption) {
      case "newest":
        return (
          new Date(b.created_at).getTime() -
          new Date(a.created_at).getTime()
        );

      case "oldest":
        return (
          new Date(a.created_at).getTime() -
          new Date(b.created_at).getTime()
        );

      case "title-asc":
        return a.title.localeCompare(b.title);

      case "title-desc":
        return b.title.localeCompare(a.title);

      case "company-asc":
        return a.company.localeCompare(b.company);

      case "company-desc":
        return b.company.localeCompare(a.company);

      default:
        return 0;
    }
  });

  if (isLoading) {
    return (
      <main className="p-8">
        <h1 className="text-2xl font-semibold">Jobs</h1>

        <p className="mt-4 text-muted-foreground">
          Loading jobs...
        </p>
      </main>
    );
  }

  return (
    <main className="p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Jobs</h1>

          <p className="mt-1 text-muted-foreground">
            Manage your job applications.
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            setShowForm((current) => !current);
            setEditingJob(null);
          }}
          className="rounded-md border px-4 py-2 font-medium"
        >
          {showForm ? "Cancel" : "Add job"}
        </button>
      </div>

      {(showForm || editingJob) && (
        <div className="mt-8">
          <JobForm
            job={editingJob ?? undefined}
            onCreated={() => {
              setShowForm(false);
              void loadJobs();
            }}
            onUpdated={() => {
              setEditingJob(null);
              void loadJobs();
            }}
            onCancel={() => {
              setEditingJob(null);
            }}
          />
        </div>
      )}

      {error && (
        <p
          className="mt-6 text-sm text-destructive"
          role="alert"
        >
          {error}
        </p>
      )}

      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <input
          type="search"
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value)}
          placeholder="Search by title, company, or location..."
          className="w-full rounded-md border px-4 py-2 outline-none focus:ring-2"
        />

        <select
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(
              event.target.value as JobStatus | "all",
            )
          }
          className="rounded-md border px-4 py-2"
        >
          <option value="all">All statuses</option>

          {JOB_STATUSES.map((status) => (
            <option key={status} value={status}>
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </option>
          ))}
        </select>

        <select
          value={sortOption}
          onChange={(event) =>
            setSortOption(event.target.value as SortOption)
          }
          className="rounded-md border px-4 py-2"
        >
          {SORT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {sortedJobs.length === 0 ? (
        <div className="mt-8 rounded-lg border p-8 text-center">
          <h2 className="font-medium">
            {searchQuery || statusFilter !== "all"
              ? "No matching jobs"
              : "No jobs yet"}
          </h2>

          <p className="mt-2 text-sm text-muted-foreground">
            {searchQuery || statusFilter !== "all"
              ? "Try changing your search or filter."
              : "Add your first job application to get started."}
          </p>
        </div>
      ) : (
        <div className="mt-8 space-y-4">
          {sortedJobs.map((job) => (
            <article
              key={job.id}
              className="rounded-lg border p-5"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="font-semibold">
                    {job.title}
                  </h2>

                  <p className="text-sm text-muted-foreground">
                    {job.company}
                    {job.location ? ` · ${job.location}` : ""}
                  </p>
                </div>

                <select
                  value={job.status}
                  onChange={(event) =>
                    void handleStatusChange(
                      job,
                      event.target.value as JobStatus,
                    )
                  }
                  className="rounded-md border px-3 py-1 text-sm"
                >
                  {JOB_STATUSES.map((status) => (
                    <option key={status} value={status}>
                      {status.charAt(0).toUpperCase() +
                        status.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              {job.description && (
                <p className="mt-4 text-sm">
                  {job.description}
                </p>
              )}

              {job.url && (
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-4 inline-block text-sm underline"
                >
                  View job posting
                </a>
              )}

              <div className="mt-5 flex gap-2">
                <button
                  type="button"
                  onClick={() =>
                    router.push(`/dashboard/jobs/${job.id}`)
                  }
                  className="rounded border px-3 py-1 text-sm"
                >
                  View
                </button>

                <button
                  type="button"
                  className="rounded-md border px-3 py-2 text-sm"
                  onClick={() => {
                    setEditingJob(job);
                    setShowForm(false);
                  }}
                >
                  Edit
                </button>

                <button
                  type="button"
                  disabled={deletingJobId === job.id}
                  onClick={() => void handleDelete(job)}
                  className="rounded-md border px-3 py-2 text-sm disabled:opacity-50"
                >
                  {deletingJobId === job.id
                    ? "Deleting..."
                    : "Delete"}
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}