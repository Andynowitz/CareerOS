"use client";

import { useEffect, useState } from "react";

import {
  createJob,
  updateJob,
  type Job,
} from "@/lib/jobs-api";
import { JOB_STATUSES, type JobStatus } from "@/lib/job-types";

interface JobFormProps {
  job?: Job;
  onCreated?: () => void;
  onUpdated?: () => void;
  onCancel?: () => void;
}

export default function JobForm({
  job,
  onCreated,
  onUpdated,
  onCancel,
}: JobFormProps) {
  const isEditing = Boolean(job);

  const [title, setTitle] = useState(job?.title ?? "");
  const [company, setCompany] = useState(job?.company ?? "");
  const [location, setLocation] = useState(job?.location ?? "");
  const [url, setUrl] = useState(job?.url ?? "");
  const [description, setDescription] = useState(
    job?.description ?? "",
  );
  const [status, setStatus] = useState<JobStatus>(
    job?.status ?? "saved",
  );

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setTitle(job?.title ?? "");
    setCompany(job?.company ?? "");
    setLocation(job?.location ?? "");
    setUrl(job?.url ?? "");
    setDescription(job?.description ?? "");
    setStatus(job?.status ?? "saved");
    setError(null);
  }, [job]);

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    try {
      setIsSubmitting(true);
      setError(null);

      const data = {
        title,
        company,
        location: location || null,
        url: url || null,
        description: description || null,
        status,
      };

      if (job) {
        await updateJob(job.id, data);
        onUpdated?.();
      } else {
        await createJob(data);

        setTitle("");
        setCompany("");
        setLocation("");
        setUrl("");
        setDescription("");
        setStatus("saved");

        onCreated?.();
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : isEditing
            ? "Failed to update job."
            : "Failed to create job.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-lg border p-6"
    >
      <div>
        <h2 className="text-lg font-semibold">
          {isEditing ? "Edit job" : "Add job"}
        </h2>

        <p className="mt-1 text-sm text-muted-foreground">
          {isEditing
            ? "Update your job application."
            : "Add a new job application."}
        </p>
      </div>

      <div>
        <label htmlFor="title" className="block text-sm font-medium">
          Job title
        </label>

        <input
          id="title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          required
          className="mt-1 w-full rounded-md border px-3 py-2"
          placeholder="Software Engineer"
        />
      </div>

      <div>
        <label htmlFor="company" className="block text-sm font-medium">
          Company
        </label>

        <input
          id="company"
          value={company}
          onChange={(event) => setCompany(event.target.value)}
          required
          className="mt-1 w-full rounded-md border px-3 py-2"
          placeholder="Example GmbH"
        />
      </div>

      <div>
        <label
          htmlFor="location"
          className="block text-sm font-medium"
        >
          Location
        </label>

        <input
          id="location"
          value={location}
          onChange={(event) => setLocation(event.target.value)}
          className="mt-1 w-full rounded-md border px-3 py-2"
          placeholder="Vienna, Austria"
        />
      </div>

      <div>
        <label htmlFor="url" className="block text-sm font-medium">
          Job URL
        </label>

        <input
          id="url"
          type="url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          className="mt-1 w-full rounded-md border px-3 py-2"
          placeholder="https://..."
        />
      </div>

      <div>
        <label
          htmlFor="description"
          className="block text-sm font-medium"
        >
          Description
        </label>

        <textarea
          id="description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          rows={6}
          className="mt-1 w-full rounded-md border px-3 py-2"
          placeholder="Paste the job description..."
        />
      </div>

      <div>
        <label
          htmlFor="status"
          className="block text-sm font-medium"
        >
          Status
        </label>

        <select
          id="status"
          value={status}
          onChange={(event) =>
            setStatus(event.target.value as JobStatus)
          }
          className="mt-1 w-full rounded-md border px-3 py-2"
        >
          {JOB_STATUSES.map((jobStatus) => (
            <option key={jobStatus} value={jobStatus}>
              {jobStatus}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      )}

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-md border px-4 py-2 font-medium disabled:opacity-50"
        >
          {isSubmitting
            ? isEditing
              ? "Saving..."
              : "Adding..."
            : isEditing
              ? "Save changes"
              : "Add job"}
        </button>

        {isEditing && onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="rounded-md border px-4 py-2 disabled:opacity-50"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}