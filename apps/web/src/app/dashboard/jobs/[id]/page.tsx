"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import {
  analyzeJob,
  createJobMatch,
  getJob,
  getJobAnalysis,
  getJobAnalysisStatus,
  getLatestJobMatch,
  updateJob,
  type Job,
  type JobAnalysis,
  type JobMatch,
} from "@/lib/jobs-api";

import {
  createJobActivity,
  getJobActivities,
  type JobActivity,
  type JobActivityType,
} from "@/lib/job-activities-api";

import {
  getResumes,
  type Resume,
} from "@/lib/resumes-api";

import {
  filterActivities,
  type ActivityFilter,
} from "@/lib/job-activity-filters";

import {
  getApplicationAssistant,
  type ApplicationAssistant,
} from "@/lib/application-assistant-api";

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

function formatTaskStatus(status: string): string {
  switch (status) {
    case "PENDING":
      return "Queued";
    case "STARTED":
      return "Processing";
    case "SUCCESS":
      return "Completed";
    case "FAILURE":
      return "Failed";
    default:
      return status;
  }
}

function formatScore(score: number): string {
  return `${Math.round(score)}%`;
}

export default function JobDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();

  const jobId = params.id;

  const [job, setJob] = useState<Job | null>(null);
  const [activities, setActivities] = useState<JobActivity[]>([]);
  const [activityFilter, setActivityFilter] =
    useState<ActivityFilter>("all");
  const [analysis, setAnalysis] = useState<JobAnalysis | null>(null);

  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [jobMatch, setJobMatch] = useState<JobMatch | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingResumes, setIsLoadingResumes] = useState(true);
  const [isLoadingMatch, setIsLoadingMatch] = useState(false);

  const [analysisStatus, setAnalysisStatus] = useState<string | null>(
    null,
  );
  const [analysisError, setAnalysisError] = useState<string | null>(
    null,
  );

  const [matchError, setMatchError] = useState<string | null>(null);

  const [error, setError] = useState<string | null>(null);

  const [activityType, setActivityType] =
    useState<JobActivityType>("note");

  const [description, setDescription] = useState("");
  const [isCreatingActivity, setIsCreatingActivity] =
    useState(false);

  const pollingTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(
    null,
  );

  const [applicationAssistant, setApplicationAssistant] =
    useState<ApplicationAssistant | null>(null);
  const [assistantLoading, setAssistantLoading] = useState(true);
  const [assistantError, setAssistantError] = useState<string | null>(null);
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

  const id = params.id as string;
  
  useEffect(() => {
    async function loadApplicationAssistant() {
      try {
        setAssistantError(null);

        const data = await getApplicationAssistant(id);

        setApplicationAssistant(data);
      } catch (err) {
        setAssistantError(
          err instanceof Error
            ? err.message
            : "Failed to load application assistant.",
        );
      } finally {
        setAssistantLoading(false);
      }
    }

    void loadApplicationAssistant();
  }, [id]);

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

  useEffect(() => {
    let cancelled = false;

    async function loadAnalysis() {
      try {
        setIsLoadingAnalysis(true);

        const existingAnalysis = await getJobAnalysis(jobId);

        if (!cancelled) {
          setAnalysis(existingAnalysis);
        }
      } catch {
        if (!cancelled) {
          setAnalysis(null);
        }
      } finally {
        if (!cancelled) {
          setIsLoadingAnalysis(false);
        }
      }
    }

    if (jobId) {
      void loadAnalysis();
    }

    return () => {
      cancelled = true;
    };
  }, [jobId]);

  useEffect(() => {
    let cancelled = false;

    async function loadResumes() {
      try {
        setIsLoadingResumes(true);
        setMatchError(null);

        const resumeData = await getResumes();

        if (!cancelled) {
          setResumes(resumeData);

          if (resumeData.length > 0) {
            const firstResume = resumeData[0];

            if (firstResume) {
              setSelectedResumeId(firstResume.id);
            }
          }
        }
      } catch (err) {
        if (!cancelled) {
          setMatchError(
            err instanceof Error
              ? err.message
              : "Failed to load resumes.",
          );
        }
      } finally {
        if (!cancelled) {
          setIsLoadingResumes(false);
        }
      }
    }

    if (jobId) {
      void loadResumes();
    }

    return () => {
      cancelled = true;
    };
  }, [jobId]);

  useEffect(() => {
    let cancelled = false;

    async function loadLatestMatch() {
      if (!selectedResumeId) {
        setJobMatch(null);
        return;
      }

      try {
        const latestMatch = await getLatestJobMatch(
          jobId,
          selectedResumeId,
        );

        if (!cancelled) {
          setJobMatch(latestMatch);
        }
      } catch {
        if (!cancelled) {
          setJobMatch(null);
        }
      }
    }

    if (jobId && selectedResumeId) {
      void loadLatestMatch();
    }

    return () => {
      cancelled = true;
    };
  }, [jobId, selectedResumeId]);

  useEffect(() => {
    return () => {
      if (pollingTimeoutRef.current) {
        clearTimeout(pollingTimeoutRef.current);
      }
    };
  }, []);

  async function pollAnalysisStatus(
    taskId: string,
  ): Promise<void> {
    try {
      const result = await getJobAnalysisStatus(jobId, taskId);

      setAnalysisStatus(result.status);

      if (result.status === "SUCCESS") {
        const completedAnalysis = await getJobAnalysis(jobId);

        setAnalysis(completedAnalysis);
        setIsAnalyzing(false);
        return;
      }

      if (result.status === "FAILURE") {
        setAnalysisError(
          "The job analysis failed. Please try again.",
        );
        setIsAnalyzing(false);
        return;
      }

      pollingTimeoutRef.current = setTimeout(() => {
        void pollAnalysisStatus(taskId);
      }, 1500);
    } catch (err) {
      setAnalysisError(
        err instanceof Error
          ? err.message
          : "Failed to check analysis status.",
      );
      setIsAnalyzing(false);
    }
  }

  async function handleAnalyzeJob() {
    try {
      setIsAnalyzing(true);
      setAnalysisStatus("PENDING");
      setAnalysisError(null);

      const task = await analyzeJob(jobId);

      setAnalysisStatus(task.status);

      await pollAnalysisStatus(task.task_id);
    } catch (err) {
      setAnalysisError(
        err instanceof Error
          ? err.message
          : "Failed to start job analysis.",
      );
      setIsAnalyzing(false);
    }
  }

  async function handleCreateMatch() {
    if (!selectedResumeId) {
      setMatchError("Please select a resume first.");
      return;
    }

    try {
      setIsLoadingMatch(true);
      setMatchError(null);

      const match = await createJobMatch(
        jobId,
        selectedResumeId,
      );

      setJobMatch(match);
    } catch (err) {
      setMatchError(
        err instanceof Error
          ? err.message
          : "Failed to calculate job match.",
      );
    } finally {
      setIsLoadingMatch(false);
    }
  }

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

  const filteredActivities = filterActivities(
    activities,
    activityFilter,
  );

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
          <h1 className="text-3xl font-bold">{job.title}</h1>

          <p className="text-lg text-gray-600">{job.company}</p>
        </div>

        <div className="grid gap-4 rounded-lg border p-5 sm:grid-cols-2">
          <div>
            <p className="text-sm text-gray-500">Location</p>

            <p>{job.location ?? "Not specified"}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500">Status</p>

            <p className="capitalize">{job.status}</p>
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
            <p className="text-sm text-gray-500">Created</p>

            <p>{formatDate(job.created_at)}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500">Last Updated</p>

            <p>{formatDate(job.updated_at)}</p>
          </div>

          {job.url && (
            <div className="sm:col-span-2">
              <p className="text-sm text-gray-500">Job URL</p>

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
              <p className="text-sm text-gray-500">Description</p>

              <p className="whitespace-pre-wrap">{job.description}</p>
            </div>
          )}
        </div>
      </section>

      {/* AI Job Analysis */}
      <section className="space-y-4">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div>
            <h2 className="text-2xl font-semibold">AI Job Analysis</h2>

            <p className="text-sm text-gray-500">
              Extract requirements and important information from the
              job description.
            </p>
          </div>

          <button
            type="button"
            onClick={() => void handleAnalyzeJob()}
            disabled={
              isAnalyzing ||
              !job.description?.trim()
            }
            className="rounded bg-black px-4 py-2 text-sm text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isAnalyzing
              ? "Analyzing..."
              : analysis
                ? "Analyze Again"
                : "Analyze Job"}
          </button>
        </div>

        {!job.description?.trim() && (
          <div className="rounded-lg border p-5 text-sm text-gray-500">
            Add a job description before running AI analysis.
          </div>
        )}

        {isAnalyzing && (
          <div className="rounded-lg border p-5">
            <p className="font-medium">
              {analysisStatus
                ? formatTaskStatus(analysisStatus)
                : "Starting analysis..."}
            </p>

            <p className="mt-1 text-sm text-gray-500">
              The AI is analyzing the job description. This may take a
              few seconds.
            </p>
          </div>
        )}

        {analysisError && (
          <div className="rounded-lg border border-red-300 bg-red-50 p-5 text-sm text-red-700">
            {analysisError}
          </div>
        )}

        {isLoadingAnalysis ? (
          <div className="rounded-lg border p-5">
            <p className="text-sm text-gray-500">
              Loading existing analysis...
            </p>
          </div>
        ) : analysis ? (
          <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-lg border p-5">
                <h3 className="font-semibold">Required Skills</h3>

                {analysis.required_skills.length === 0 ? (
                  <p className="mt-2 text-sm text-gray-500">
                    None identified.
                  </p>
                ) : (
                  <ul className="mt-3 list-disc space-y-1 pl-5">
                    {analysis.required_skills.map((skill) => (
                      <li key={skill}>{skill}</li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="rounded-lg border p-5">
                <h3 className="font-semibold">Preferred Skills</h3>

                {analysis.preferred_skills.length === 0 ? (
                  <p className="mt-2 text-sm text-gray-500">
                    None identified.
                  </p>
                ) : (
                  <ul className="mt-3 list-disc space-y-1 pl-5">
                    {analysis.preferred_skills.map((skill) => (
                      <li key={skill}>{skill}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className="rounded-lg border p-5">
              <h3 className="font-semibold">Responsibilities</h3>

              {analysis.responsibilities.length === 0 ? (
                <p className="mt-2 text-sm text-gray-500">
                  None identified.
                </p>
              ) : (
                <ul className="mt-3 list-disc space-y-1 pl-5">
                  {analysis.responsibilities.map(
                    (responsibility) => (
                      <li key={responsibility}>
                        {responsibility}
                      </li>
                    ),
                  )}
                </ul>
              )}
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-lg border p-5">
                <h3 className="font-semibold">
                  Experience Requirements
                </h3>

                <p className="mt-2 whitespace-pre-wrap text-sm">
                  {analysis.experience_requirements ??
                    "Not specified."}
                </p>
              </div>

              <div className="rounded-lg border p-5">
                <h3 className="font-semibold">
                  Education Requirements
                </h3>

                <p className="mt-2 whitespace-pre-wrap text-sm">
                  {analysis.education_requirements ??
                    "Not specified."}
                </p>
              </div>
            </div>

            <div className="rounded-lg border p-5">
              <h3 className="font-semibold">Keywords</h3>

              {analysis.keywords.length === 0 ? (
                <p className="mt-2 text-sm text-gray-500">
                  None identified.
                </p>
              ) : (
                <div className="mt-3 flex flex-wrap gap-2">
                  {analysis.keywords.map((keyword) => (
                    <span
                      key={keyword}
                      className="rounded-full border px-3 py-1 text-sm"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {analysis.salary_information && (
              <div className="rounded-lg border p-5">
                <h3 className="font-semibold">
                  Salary Information
                </h3>

                <div className="mt-3 space-y-2 text-sm">
                  {Object.entries(
                    analysis.salary_information,
                  ).map(([key, value]) => (
                    <div
                      key={key}
                      className="flex justify-between gap-4"
                    >
                      <span className="font-medium capitalize">
                        {key.replace(/_/g, " ")}
                      </span>

                      <span className="text-right">
                        {value ?? "Not specified"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <p className="text-xs text-gray-500">
              Analysis created {formatDate(analysis.created_at)}
            </p>
          </div>
        ) : (
          !isAnalyzing && (
            <div className="rounded-lg border p-5">
              <p className="text-sm text-gray-500">
                No analysis available yet. Run the AI analysis to
                extract requirements from this job.
              </p>
            </div>
          )
        )}
      </section>

      {/* Job Match */}
      <section className="space-y-4">
        <div>
          <h2 className="text-2xl font-semibold">Job Match</h2>

          <p className="text-sm text-gray-500">
            Calculate how well a resume matches this job using the
            deterministic matching engine.
          </p>
        </div>

        <div className="rounded-lg border p-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
            <div className="flex-1">
              <label
                htmlFor="resume"
                className="mb-1 block text-sm font-medium"
              >
                Resume
              </label>

              {isLoadingResumes ? (
                <p className="text-sm text-gray-500">
                  Loading resumes...
                </p>
              ) : resumes.length === 0 ? (
                <p className="text-sm text-gray-500">
                  No resumes available. Upload a resume first.
                </p>
              ) : (
                <select
                  id="resume"
                  value={selectedResumeId}
                  onChange={(event) => {
                    setSelectedResumeId(event.target.value);
                    setJobMatch(null);
                    setMatchError(null);
                  }}
                  className="w-full rounded border px-3 py-2"
                >
                  {resumes.map((resume) => (
                    <option
                      key={resume.id}
                      value={resume.id}
                    >
                      {resume.name} — v{resume.current_version}
                    </option>
                  ))}
                </select>
              )}
            </div>

            <button
              type="button"
              onClick={() => void handleCreateMatch()}
              disabled={
                isLoadingMatch ||
                isLoadingResumes ||
                resumes.length === 0 ||
                !selectedResumeId
              }
              className="rounded bg-black px-4 py-2 text-sm text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isLoadingMatch
                ? "Calculating..."
                : jobMatch
                  ? "Recalculate Match"
                  : "Calculate Match"}
            </button>
          </div>
        </div>

        {matchError && (
          <div className="rounded-lg border border-red-300 bg-red-50 p-5 text-sm text-red-700">
            {matchError}
          </div>
        )}

        {jobMatch && (
          <div className="space-y-6">
            <div className="rounded-lg border p-6">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div className="text-center">
                  <p className="text-4xl font-bold">
                    {formatScore(jobMatch.score)}
                  </p>

                  <p className="text-sm text-gray-500">Overall Match</p>
                </div>

                <p className="text-xs text-gray-500">
                  Calculated {formatDate(jobMatch.created_at)}
                </p>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
              {[
                [
                  "Required Skills",
                  jobMatch.required_skills_score,
                ],
                [
                  "Preferred Skills",
                  jobMatch.preferred_skills_score,
                ],
                [
                  "Experience",
                  jobMatch.experience_score,
                ],
                [
                  "Education",
                  jobMatch.education_score,
                ],
                [
                  "Keywords",
                  jobMatch.keywords_score,
                ],
              ].map(([label, score]) => (
                <div
                  key={label as string}
                  className="rounded-lg border p-4"
                >
                  <p className="text-sm text-gray-500">
                    {label as string}
                  </p>

                  <p className="mt-1 text-2xl font-semibold">
                    {label === "Preferred Skills" &&
                    jobMatch.matched_preferred_skills.length === 0 &&
                    jobMatch.missing_preferred_skills.length === 0
                      ? "Not specified"
                      : formatScore((score as number) * 100)}
                  </p>
                </div>
              ))}
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-lg border p-5">
                <h3 className="font-semibold">
                  Matched Required Skills
                </h3>

                {jobMatch.matched_required_skills.length === 0 ? (
                  <p className="mt-2 text-sm text-gray-500">
                    None.
                  </p>
                ) : (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {jobMatch.matched_required_skills.map(
                      (skill) => (
                        <span
                          key={skill}
                          className="rounded-full border px-3 py-1 text-sm"
                        >
                          ✓ {skill}
                        </span>
                      ),
                    )}
                  </div>
                )}
              </div>

              <div className="rounded-lg border p-5">
                <h3 className="font-semibold">
                  Missing Required Skills
                </h3>

                {jobMatch.missing_required_skills.length === 0 ? (
                  <p className="mt-2 text-sm text-gray-500">
                    None.
                  </p>
                ) : (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {jobMatch.missing_required_skills.map(
                      (skill) => (
                        <span
                          key={skill}
                          className="rounded-full border px-3 py-1 text-sm"
                        >
                          {skill}
                        </span>
                      ),
                    )}
                  </div>
                )}
              </div>

              <div className="rounded-lg border p-5">
                <h3 className="font-semibold">
                  Matched Preferred Skills
                </h3>

                {jobMatch.matched_preferred_skills.length === 0 ? (
                  <p className="mt-2 text-sm text-gray-500">
                    None.
                  </p>
                ) : (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {jobMatch.matched_preferred_skills.map(
                      (skill) => (
                        <span
                          key={skill}
                          className="rounded-full border px-3 py-1 text-sm"
                        >
                          ✓ {skill}
                        </span>
                      ),
                    )}
                  </div>
                )}
              </div>

              <div className="rounded-lg border p-5">
                <h3 className="font-semibold">
                  Missing Preferred Skills
                </h3>

                {jobMatch.missing_preferred_skills.length === 0 ? (
                  <p className="mt-2 text-sm text-gray-500">
                    None.
                  </p>
                ) : (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {jobMatch.missing_preferred_skills.map(
                      (skill) => (
                        <span
                          key={skill}
                          className="rounded-full border px-3 py-1 text-sm"
                        >
                          {skill}
                        </span>
                      ),
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="rounded-lg border p-5">
              <h3 className="font-semibold">
                Why this score?
              </h3>

              {jobMatch.explanations.length === 0 ? (
                <p className="mt-2 text-sm text-gray-500">
                  No explanation available.
                </p>
              ) : (
                <ul className="mt-3 list-disc space-y-2 pl-5 text-sm">
                  {jobMatch.explanations.map(
                    (explanation) => (
                      <li key={explanation}>
                        {explanation}
                      </li>
                    ),
                  )}
                </ul>
              )}
            </div>
          </div>
        )}
      </section>

      {/* Add activity */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Add Activity</h2>

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

      
      <section className="rounded-lg border bg-white p-6 shadow-sm">
        <div className="mb-6">
          <h2 className="text-xl font-semibold">
            Application Assistant
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Actionable information for managing this application.
          </p>
        </div>

        {assistantLoading && (
          <p className="text-sm text-gray-500">
            Loading application assistant...
          </p>
        )}

        {assistantError && (
          <p className="text-sm text-red-600">
            {assistantError}
          </p>
        )}

        {!assistantLoading &&
          !assistantError &&
          applicationAssistant && (
            <div className="space-y-6">
              {applicationAssistant.missing_information.length > 0 && (
                <div>
                  <h3 className="mb-2 font-medium">
                    Missing information
                  </h3>

                  <ul className="list-disc space-y-1 pl-5 text-sm text-gray-600">
                    {applicationAssistant.missing_information.map(
                      (item) => (
                        <li key={item}>{item}</li>
                      ),
                    )}
                  </ul>
                </div>
              )}

              <div>
                <h3 className="mb-3 font-medium">
                  Application checklist
                </h3>

                <div className="space-y-2">
                  {applicationAssistant.checklist.map((item) => (
                    <div
                      key={item.item}
                      className="flex items-center gap-2 text-sm"
                    >
                      <span>
                        {item.completed ? "✓" : "○"}
                      </span>

                      <span
                        className={
                          item.completed
                            ? "text-gray-500 line-through"
                            : "text-gray-900"
                        }
                      >
                        {item.item}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="mb-3 font-medium">
                  Next actions
                </h3>

                <ul className="space-y-2">
                  {applicationAssistant.next_actions.map(
                    (action) => (
                      <li
                        key={action}
                        className="rounded-md bg-gray-50 p-3 text-sm"
                      >
                        {action}
                      </li>
                    ),
                  )}
                </ul>
              </div>

              <div>
                <h3 className="mb-2 font-medium">
                  Follow-up
                </h3>

                <p className="text-sm">
                  {applicationAssistant.follow_up_needed
                    ? "A follow-up may be appropriate."
                    : "No follow-up is currently needed."}
                </p>

                {applicationAssistant.last_activity_at && (
                  <p className="mt-1 text-xs text-gray-500">
                    Last activity:{" "}
                    {new Date(
                      applicationAssistant.last_activity_at,
                    ).toLocaleString()}
                  </p>
                )}
              </div>
            </div>
          )}
      </section>

      {/* Activity timeline */}
      <section className="space-y-4">
        <div>
          <h2 className="text-2xl font-semibold">
            Activity Timeline
          </h2>

          <p className="text-sm text-gray-500">
            Track everything that happened during this application.
          </p>
        </div>

        {/* Activity filters */}
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setActivityFilter("all")}
            className={`rounded border px-3 py-1.5 text-sm ${
              activityFilter === "all"
                ? "bg-black text-white"
                : "bg-white"
            }`}
          >
            All
          </button>

          {ACTIVITY_TYPES.map((type) => (
            <button
              key={type.value}
              type="button"
              onClick={() => setActivityFilter(type.value)}
              className={`rounded border px-3 py-1.5 text-sm ${
                activityFilter === type.value
                  ? "bg-black text-white"
                  : "bg-white"
              }`}
            >
              {type.label}
            </button>
          ))}

          <button
            type="button"
            onClick={() => setActivityFilter("status_changed")}
            className={`rounded border px-3 py-1.5 text-sm ${
              activityFilter === "status_changed"
                ? "bg-black text-white"
                : "bg-white"
            }`}
          >
            Status Changes
          </button>

          <button
            type="button"
            onClick={() => setActivityFilter("created")}
            className={`rounded border px-3 py-1.5 text-sm ${
              activityFilter === "created"
                ? "bg-black text-white"
                : "bg-white"
            }`}
          >
            Created
          </button>
        </div>

        {filteredActivities.length === 0 ? (
          <div className="rounded-lg border p-5">
            <p className="text-gray-500">
              No activities match the selected filter.
            </p>
          </div>
        ) : (
          <div className="relative space-y-6 pl-6">
            <div className="absolute bottom-0 left-2 top-0 w-px bg-gray-200" />

            {filteredActivities.map((activity) => (
              <article
                key={activity.id}
                className="relative rounded-lg border bg-white p-5"
              >
                <div className="absolute -left-[1.65rem] top-6 h-3 w-3 rounded-full border-2 border-white bg-black" />

                <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-start">
                  <div>
                    <h3 className="font-semibold">
                      {formatActivityType(activity.type)}
                    </h3>

                    <time className="text-sm text-gray-500">
                      {formatDate(activity.created_at)}
                    </time>
                  </div>
                </div>

                {activity.type === "status_changed" &&
                  activity.old_status &&
                  activity.new_status && (
                    <div className="mt-3 rounded-md bg-gray-50 p-3 text-sm">
                      <span className="capitalize">
                        {activity.old_status}
                      </span>

                      {" → "}

                      <span className="font-medium capitalize">
                        {activity.new_status}
                      </span>
                    </div>
                  )}

                {activity.description && (
                  <p className="mt-3 whitespace-pre-wrap text-gray-700">
                    {activity.description}
                  </p>
                )}
              </article>
            ))}
          </div>
        )}
      </section>

      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </main>
  );
}
