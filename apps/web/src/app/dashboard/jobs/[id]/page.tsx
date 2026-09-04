"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import {
  getJob,
  updateJob,
  type Job,
} from "@/lib/jobs-api";

import {
  createJobActivity,
  getJobActivities,
  type JobActivity,
  type JobActivityType,
} from "@/lib/job-activities-api";

const ACTIVITY_TYPES: {
  value: JobActivityType;
  label: string;
}[] = [
  { value: "note", label: "Note" },
  { value: "email", label: "Email" },
  { value: "phone_call", label: "Phone Call" },
  { value: "interview", label: "Interview" },
  { value: "offer", label: "Offer" },
  { value: "rejection", label: "Rejection" },
  { value: "other", label: "Other" },
];

function formatDate(date: string): string {
  return new Date(date).toLocaleString();
}

function formatActivityType(type: JobActivityType): string {
  switch (type) {
    case "created":
      return "Created";
    case "status_changed":
      return "Status Changed";
    case "note":
      return "Note";
    case "email":
      return "Email";
    case "phone_call":
      return "Phone Call";
    case "interview":
      return "Interview";
    case "offer":
      return "Offer";
    case "rejection":
      return "Rejection";
    case "other":
      return "Other";
  }
}

export default function JobDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();

  const jobId = params.id;

  const [job, setJob] = useState<Job | null>(null);
  const [activities, setActivities] = useState<JobActivity[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [activityType, setActivityType] =
    useState<JobActivityType>("note");

  const [description, setDescription] = useState("");
  const [isCreatingActivity, setIsCreatingActivity] =
    useState(false);

  async function handleStatusChange(newStatus: Job["status"]) {
    if (!job || newStatus === job.status) {
        return;
    }

    try {
        setError(null);

        const updatedJob = await updateJob(job.id, {
        status: newStatus,
        });

        setJob(updatedJob);

        const updatedActivities = await getJobActivities(job.id);
        setActivities(updatedActivities);
    } catch (err) {
        setError(
        err instanceof Error
            ? err.message
            : "Failed to update job status.",
        );
    }
    }

  useEffect(() => {
    async function loadData() {
        try {
        setIsLoading(true);
        setError(null);

        const [jobData, activityData] = await Promise.all([
            getJob(jobId),
            getJobActivities(jobId),
        ]);

        setJob(jobData);
        setActivities(activityData);
        } catch (err) {
        setError(
            err instanceof Error
            ? err.message
            : "Failed to load job.",
        );
        } finally {
        setIsLoading(false);
        }
    }

    if (jobId) {
        void loadData();
    }
    }, [jobId]);

  async function handleCreateActivity(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!description.trim()) {
      return;
    }

    try {
      setIsCreatingActivity(true);
      setError(null);

      await createJobActivity(jobId, {
        type: activityType,
        description: description.trim(),
      });

      setDescription("");

      const updatedActivities = await getJobActivities(jobId);
      setActivities(updatedActivities);

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create activity.",
      );
    } finally {
      setIsCreatingActivity(false);
    }
  }

  if (isLoading) {
    return (
      <main className="mx-auto max-w-4xl p-6">
        <p>Loading...</p>
      </main>
    );
  }

  if (error && !job) {
    return (
      <main className="mx-auto max-w-4xl p-6">
        <button
          type="button"
          onClick={() => router.push("/dashboard/jobs")}
          className="mb-6 text-sm underline"
        >
          ← Back to Jobs
        </button>

        <p className="text-red-600">{error}</p>
      </main>
    );
  }

  if (!job) {
    return (
      <main className="mx-auto max-w-4xl p-6">
        <p>Job not found.</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl space-y-8 p-6">
      <button
        type="button"
        onClick={() => router.push("/dashboard/jobs")}
        className="text-sm underline"
      >
        ← Back to Jobs
      </button>

      {/* Job information */}
      <section className="space-y-4">
        <div>
          <h1 className="text-3xl font-bold">
            {job.title}
          </h1>

          <p className="text-lg text-gray-600">
            {job.company}
          </p>
        </div>

        <div className="grid gap-4 rounded-lg border p-5 sm:grid-cols-2">
          <div>
            <p className="text-sm text-gray-500">
              Location
            </p>

            <p>
              {job.location ?? "Not specified"}
            </p>
          </div>

          <div>
            <p className="text-sm text-gray-500">
              Status
            </p>

            <p className="capitalize">
              {job.status}
            </p>
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
                value={job.status}
                onChange={(event) =>
                void handleStatusChange(
                    event.target.value as Job["status"],
                )
                }
                className="mt-1 rounded border px-3 py-2"
            >
                <option value="saved">Saved</option>
                <option value="applied">Applied</option>
                <option value="interview">Interview</option>
                <option value="offer">Offer</option>
                <option value="rejected">Rejected</option>
                <option value="withdrawn">Withdrawn</option>
            </select>
          </div>

          <div>
            <p className="text-sm text-gray-500">
              Created
            </p>

            <p>{formatDate(job.created_at)}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500">
              Last Updated
            </p>

            <p>{formatDate(job.updated_at)}</p>
          </div>

          {job.url && (
            <div className="sm:col-span-2">
              <p className="text-sm text-gray-500">
                Job URL
              </p>

              <a
                href={job.url}
                target="_blank"
                rel="noopener noreferrer"
                className="break-all underline"
              >
                {job.url}
              </a>
            </div>
          )}


          {job.description && (
            <div className="sm:col-span-2">
              <p className="text-sm text-gray-500">
                Description
              </p>

              <p className="whitespace-pre-wrap">
                {job.description}
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Add activity */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">
          Add Activity
        </h2>

        <form
          onSubmit={handleCreateActivity}
          className="space-y-4 rounded-lg border p-5"
        >
          <div>
            <label
              htmlFor="activity-type"
              className="mb-1 block text-sm font-medium"
            >
              Type
            </label>

            <select
              id="activity-type"
              value={activityType}
              onChange={(event) =>
                setActivityType(
                  event.target.value as JobActivityType,
                )
              }
              className="w-full rounded border p-2"
            >
              {ACTIVITY_TYPES.map((type) => (
                <option
                  key={type.value}
                  value={type.value}
                >
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label
              htmlFor="activity-description"
              className="mb-1 block text-sm font-medium"
            >
              Description
            </label>

            <textarea
              id="activity-description"
              value={description}
              onChange={(event) =>
                setDescription(event.target.value)
              }
              placeholder="Describe what happened..."
              rows={4}
              className="w-full rounded border p-2"
            />
          </div>

          <button
            type="submit"
            disabled={
              isCreatingActivity ||
              !description.trim()
            }
            className="rounded bg-black px-4 py-2 text-white disabled:opacity-50"
          >
            {isCreatingActivity
              ? "Adding..."
              : "Add Activity"}
          </button>
        </form>
      </section>

      {/* Activity timeline */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">
          Activity
        </h2>

        {activities.length === 0 ? (
          <p className="text-gray-500">
            No activity yet.
          </p>
        ) : (
          <div className="space-y-4">
            {activities.map((activity) => (
              <article
                key={activity.id}
                className="rounded-lg border p-5"
              >
                <div className="flex flex-col justify-between gap-2 sm:flex-row">
                  <div>
                    <h3 className="font-semibold">
                      {formatActivityType(
                        activity.type,
                      )}
                    </h3>

                    {activity.description && (
                      <p className="mt-1 whitespace-pre-wrap text-gray-700">
                        {activity.description}
                      </p>
                    )}
                  </div>

                  <time className="text-sm text-gray-500">
                    {formatDate(activity.created_at)}
                  </time>
                </div>

                {activity.type === "status_changed" &&
                  activity.old_status &&
                  activity.new_status && (
                    <p className="mt-3 text-sm">
                      <span className="capitalize">
                        {activity.old_status}
                      </span>
                      {" → "}
                      <span className="capitalize">
                        {activity.new_status}
                      </span>
                    </p>
                  )}
              </article>
            ))}
          </div>
        )}
      </section>

      {error && (
        <p className="text-sm text-red-600">
          {error}
        </p>
      )}
    </main>
  );
}