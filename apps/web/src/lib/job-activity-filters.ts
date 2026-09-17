import type {
  JobActivity,
  JobActivityType,
} from "./job-activities-api";

export type ActivityFilter = JobActivityType | "all";

export function filterActivities(
  activities: JobActivity[],
  filter: ActivityFilter,
): JobActivity[] {
  if (filter === "all") {
    return activities;
  }

  return activities.filter(
    (activity) => activity.type === filter,
  );
}