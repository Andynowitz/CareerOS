import { describe, expect, it } from "vitest";

import {
  filterJobs,
  matchesDateFilter,
  sortJobs,
  type JobFilterOptions,
} from "./job-filters";
import type { Job } from "./jobs-api";

const NOW = new Date("2026-09-14T12:00:00Z").getTime();

const jobs: Job[] = [
  {
    id: "1",
    user_id: "user-1",
    title: "Java Developer",
    company: "Tech Corp",
    location: "Vienna",
    url: "https://example.com/java",
    description: "Java backend development",
    status: "applied",
    created_at: "2026-09-13T12:00:00Z",
    updated_at: "2026-09-13T12:00:00Z",
  },
  {
    id: "2",
    user_id: "user-1",
    title: "C# Developer",
    company: "Software GmbH",
    location: "Graz",
    url: "https://example.com/csharp",
    description: "C# and .NET development",
    status: "interview",
    created_at: "2026-08-01T12:00:00Z",
    updated_at: "2026-08-01T12:00:00Z",
  },
  {
    id: "3",
    user_id: "user-1",
    title: "Python Developer",
    company: "Data Systems",
    location: "Linz",
    url: "https://example.com/python",
    description: "Python and data engineering",
    status: "saved",
    created_at: "2026-05-01T12:00:00Z",
    updated_at: "2026-05-01T12:00:00Z",
  },
];

const baseOptions: JobFilterOptions = {
  searchQuery: "",
  statusFilter: "all",
  dateFilter: "all",
  matchScoreFilter: "all",
  matchScores: {},
  now: NOW,
};

describe("matchesDateFilter", () => {
  it("matches recent jobs", () => {
    expect(matchesDateFilter(jobs[0]!, "7-days", NOW)).toBe(true);
  });

  it("matches jobs from the last 30 days", () => {
    expect(matchesDateFilter(jobs[1]!, "30-days", NOW)).toBe(false);
    expect(matchesDateFilter(jobs[0]!, "30-days", NOW)).toBe(true);
  });

  it("matches jobs older than 90 days", () => {
    expect(matchesDateFilter(jobs[2]!, "older", NOW)).toBe(true);
  });

  it("matches all jobs when the date filter is all", () => {
    expect(matchesDateFilter(jobs[2]!, "all", NOW)).toBe(true);
  });
});

describe("filterJobs", () => {
  it("filters by title", () => {
    const result = filterJobs(jobs, {
      ...baseOptions,
      searchQuery: "java",
    });

    expect(result).toHaveLength(1);
    expect(result[0]!.title).toBe("Java Developer");
  });

  it("filters by company", () => {
    const result = filterJobs(jobs, {
      ...baseOptions,
      searchQuery: "software",
    });

    expect(result).toHaveLength(1);
    expect(result[0]!!.company).toBe("Software GmbH");
  });

  it("filters by location", () => {
    const result = filterJobs(jobs, {
      ...baseOptions,
      searchQuery: "linz",
    });

    expect(result).toHaveLength(1);
    expect(result[0]!.location).toBe("Linz");
  });

  it("filters by application status", () => {
    const result = filterJobs(jobs, {
      ...baseOptions,
      statusFilter: "interview",
    });

    expect(result).toHaveLength(1);
    expect(result[0]!.id).toBe("2");
  });

  it("filters by match score", () => {
    const result = filterJobs(jobs, {
      ...baseOptions,
      matchScoreFilter: "80",
      matchScores: {
        "1": 85,
        "2": 75,
        "3": 95,
      },
    });

    expect(result).toHaveLength(2);
    expect(result.map((job) => job.id)).toEqual(["1", "3"]);
  });

it("combines multiple filters", () => {
    const result = filterJobs(jobs, {
        ...baseOptions,
        searchQuery: "java",
        matchScoreFilter: "80",
        matchScores: {
        "1": 85,
        "2": 75,
        "3": 95,
        },
});

expect(result).toHaveLength(1);
expect(result[0]!   .id).toBe("1");
});

  it("returns no jobs when nothing matches", () => {
    const result = filterJobs(jobs, {
      ...baseOptions,
      searchQuery: "Android",
    });

    expect(result).toHaveLength(0);
  });
});

describe("sortJobs", () => {
  it("sorts newest first", () => {
    const result = sortJobs(jobs, "newest");

    expect(result.map((job) => job.id)).toEqual(["1", "2", "3"]);
  });

  it("sorts oldest first", () => {
    const result = sortJobs(jobs, "oldest");

    expect(result.map((job) => job.id)).toEqual(["3", "2", "1"]);
  });

  it("sorts titles A-Z", () => {
    const result = sortJobs(jobs, "title-asc");

    expect(result.map((job) => job.title)).toEqual([
      "C# Developer",
      "Java Developer",
      "Python Developer",
    ]);
  });

  it("sorts titles Z-A", () => {
    const result = sortJobs(jobs, "title-desc");

    expect(result.map((job) => job.title)).toEqual([
      "Python Developer",
      "Java Developer",
      "C# Developer",
    ]);
  });

  it("sorts companies A-Z", () => {
    const result = sortJobs(jobs, "company-asc");

    expect(result.map((job) => job.company)).toEqual([
      "Data Systems",
      "Software GmbH",
      "Tech Corp",
    ]);
  });

  it("sorts companies Z-A", () => {
    const result = sortJobs(jobs, "company-desc");

    expect(result.map((job) => job.company)).toEqual([
      "Tech Corp",
      "Software GmbH",
      "Data Systems",
    ]);
  });
});