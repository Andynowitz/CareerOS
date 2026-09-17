import type { Job } from "./jobs-api";
import type { JobStatus } from "./job-types";

export type DateFilter =
  | "all"
  | "7-days"
  | "30-days"
  | "90-days"
  | "older";

export type MatchScoreFilter =
  | "all"
  | "60"
  | "70"
  | "80"
  | "90";

export type SortOption =
  | "newest"
  | "oldest"
  | "title-asc"
  | "title-desc"
  | "company-asc"
  | "company-desc";

export interface JobFilterOptions {
  searchQuery: string;
  statusFilter: JobStatus | "all";
  dateFilter: DateFilter;
  matchScoreFilter: MatchScoreFilter;
  matchScores: Record<string, number>;
  now?: number;
}

export function matchesDateFilter(
  job: Job,
  dateFilter: DateFilter,
  now = Date.now(),
): boolean {
  if (dateFilter === "all") {
    return true;
  }

  const createdAt = new Date(job.created_at).getTime();

  if (dateFilter === "older") {
    return createdAt < now - 90 * 24 * 60 * 60 * 1000;
  }

  const days = {
    "7-days": 7,
    "30-days": 30,
    "90-days": 90,
  } as const;

  return createdAt >= now - days[dateFilter] * 24 * 60 * 60 * 1000;
}

export function filterJobs(
  jobs: Job[],
  options: JobFilterOptions,
): Job[] {
  const normalizedSearchQuery =
    options.searchQuery.trim().toLowerCase();

  return jobs.filter((job) => {
    const matchesSearch =
      !normalizedSearchQuery ||
      job.title.toLowerCase().includes(normalizedSearchQuery) ||
      job.company.toLowerCase().includes(normalizedSearchQuery) ||
      (job.location?.toLowerCase().includes(normalizedSearchQuery) ??
        false);

    const matchesStatus =
      options.statusFilter === "all" ||
      job.status === options.statusFilter;

    const matchesDate = matchesDateFilter(
      job,
      options.dateFilter,
      options.now,
    );

    const matchesScore =
        options.matchScoreFilter === "all" ||
        (options.matchScores[job.id] ?? -1) >=
            Number(options.matchScoreFilter);

    return (
        matchesSearch &&
        matchesStatus &&
        matchesDate &&
        matchesScore
    );
  });
}

export function sortJobs(
  jobs: Job[],
  sortOption: SortOption,
): Job[] {
  return [...jobs].sort((a, b) => {
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
}