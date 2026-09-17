"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  getJobs,
  updateJob,
  deleteJob,
  analyzeJob,
  getJobAnalysis,
  getJobAnalysisStatus,
  getLatestJobMatch,
  type Job,
  type JobAnalysis,
} from "@/lib/jobs-api";

import {
  JOB_STATUSES,
  type JobStatus,
} from "@/lib/job-types";

import JobForm from "./job-form";

import {
  getResumes,
  type Resume,
} from "@/lib/resumes-api";

import {
  filterJobs,
  sortJobs,
  type DateFilter,
  type MatchScoreFilter,
  type SortOption,
} from "@/lib/job-filters";


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
  
  const [dateFilter, setDateFilter] =
    useState<DateFilter>("all");
  const [sortOption, setSortOption] =
    useState<SortOption>("newest");

  const router = useRouter();
  
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [matchScoreFilter, setMatchScoreFilter] =
    useState<MatchScoreFilter>("all");

  const [matchScores, setMatchScores] = useState<
    Record<string, number>
  >({});
  const [matchScoresLoading, setMatchScoresLoading] =
    useState(false);

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

  useEffect(() => {
    async function loadResumes() {
      try {
        const data = await getResumes();

        setResumes(data);

        const firstResume = data[0];

        if (firstResume) {
          setSelectedResumeId(firstResume.id);
        }
      } catch {
        setResumes([]);
      }
    }

    void loadResumes();
  }, []);


  useEffect(() => {
    if (!selectedResumeId || jobs.length === 0) {
      setMatchScores({});
      return;
    }

    async function loadMatchScores() {
      setMatchScoresLoading(true);

      const scores: Record<string, number> = {};

      await Promise.all(
        jobs.map(async (job) => {
          try {
            const match = await getLatestJobMatch(
              job.id,
              selectedResumeId,
            );

            scores[job.id] = match.score;
          } catch {
            // No match available for this job.
          }
        }),
      );

      setMatchScores(scores);
      setMatchScoresLoading(false);
    }

    void loadMatchScores();
  }, [jobs, selectedResumeId]);

  const normalizedSearchQuery = searchQuery.trim().toLowerCase();

  const filteredJobs = filterJobs(jobs, {
    searchQuery,
    statusFilter,
    dateFilter,
    matchScoreFilter,
    matchScores,
  });

  const sortedJobs = sortJobs(filteredJobs, sortOption);

  
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
          value={dateFilter}
          onChange={(event) =>
            setDateFilter(event.target.value as DateFilter)
          }
          className="rounded-md border px-4 py-2"
        >
          <option value="all">All dates</option>
          <option value="7-days">Last 7 days</option>
          <option value="30-days">Last 30 days</option>
          <option value="90-days">Last 90 days</option>
          <option value="older">Older than 90 days</option>
        </select>
        
        <select
          value={selectedResumeId}
          onChange={(event) => {
            setSelectedResumeId(event.target.value);
            setMatchScoreFilter("all");
          }}
          disabled={resumes.length === 0}
          className="rounded-md border px-4 py-2"
        >
          <option value="">
            {resumes.length === 0
              ? "No resumes available"
              : "Select resume"}
          </option>

          {resumes.map((resume) => (
            <option key={resume.id} value={resume.id}>
              {resume.name}
            </option>
          ))}
        </select>


        <select
          value={matchScoreFilter}
          onChange={(event) =>
            setMatchScoreFilter(
              event.target.value as MatchScoreFilter,
            )
          }
          disabled={!selectedResumeId || matchScoresLoading}
          className="rounded-md border px-4 py-2"
        >
          <option value="all">All match scores</option>
          <option value="60">60%+ match</option>
          <option value="70">70%+ match</option>
          <option value="80">80%+ match</option>
          <option value="90">90%+ match</option>
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
            {searchQuery ||
              statusFilter !== "all" ||
              dateFilter !== "all" ||
              matchScoreFilter !== "all"
              ? "No matching jobs"
              : "No jobs yet"}
          </h2>

          <p className="mt-2 text-sm text-muted-foreground">
            {searchQuery ||
            statusFilter !== "all" ||
            dateFilter !== "all" ||
            matchScoreFilter !== "all"
              ? "Try changing your search or filters."
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

                {selectedResumeId &&
                  matchScores[job.id] !== undefined && (
                    <p className="mt-2 text-sm font-medium">
                      Match score:{" "}
                      {Math.round(matchScores[job.id] ?? 0)}%
                    </p>
                )}
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