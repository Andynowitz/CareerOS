"use client";

import { useEffect, useState } from "react";

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

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingJob, setEditingJob] = useState<Job | null>(null);
  const [deletingJobId, setDeletingJobId] = useState<string | null>(null);

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

  useEffect(() => {
    void loadJobs();
  }, []);

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

  if (isLoading) {
    return (
      <main className="p-8">
        <h1 className="text-2xl font-semibold">Jobs</h1>
        <p className="mt-4 text-muted-foreground">Loading jobs...</p>
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
        <p className="mt-6 text-sm text-destructive" role="alert">
          {error}
        </p>
      )}

      {jobs.length === 0 ? (
        <div className="mt-8 rounded-lg border p-8 text-center">
          <h2 className="font-medium">No jobs yet</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Add your first job application to get started.
          </p>
        </div>
      ) : (
        <div className="mt-8 space-y-4">
          {jobs.map((job) => (
            <article
              key={job.id}
              className="rounded-lg border p-5"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="font-semibold">{job.title}</h2>

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
                      {status.charAt(0).toUpperCase() + status.slice(1)}
                    </option>
                  ))}
                </select>

              </div>

              {job.description && (
                <p className="mt-4 text-sm">{job.description}</p>
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
                  {deletingJobId === job.id ? "Deleting..." : "Delete"}
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}