import { describe, expect, it } from "vitest";

import {
  filterActivities,
  type ActivityFilter,
} from "./job-activity-filters";

import type { JobActivity } from "./job-activities-api";

const activities: JobActivity[] = [
  {
    id: "1",
    job_id: "job-1",
    user_id: "user-1",
    type: "created",
    description: "Job created",
    old_status: null,
    new_status: null,
    created_at: "2026-09-01T10:00:00Z",
  },
  {
    id: "2",
    job_id: "job-1",
    user_id: "user-1",
    type: "status_changed",
    description: "Status changed",
    old_status: "saved",
    new_status: "applied",
    created_at: "2026-09-02T10:00:00Z",
  },
  {
    id: "3",
    job_id: "job-1",
    user_id: "user-1",
    type: "note",
    description: "Follow up next week",
    old_status: null,
    new_status: null,
    created_at: "2026-09-03T10:00:00Z",
  },
  {
    id: "4",
    job_id: "job-1",
    user_id: "user-1",
    type: "email",
    description: "Sent application email",
    old_status: null,
    new_status: null,
    created_at: "2026-09-04T10:00:00Z",
  },
];

describe("filterActivities", () => {
  it("returns all activities when the filter is all", () => {
    expect(filterActivities(activities, "all")).toEqual(
      activities,
    );
  });

  it("filters status change activities", () => {
    expect(
      filterActivities(activities, "status_changed"),
    ).toHaveLength(1);

    expect(
      filterActivities(activities, "status_changed")[0].id,
    ).toBe("2");
  });

  it("filters activities by type", () => {
    expect(
      filterActivities(activities, "note"),
    ).toHaveLength(1);

    expect(
      filterActivities(activities, "email"),
    ).toHaveLength(1);
  });

  it("returns an empty array when no activities match", () => {
    const filter: ActivityFilter = "interview";

    expect(
      filterActivities(activities, filter),
    ).toEqual([]);
  });
});