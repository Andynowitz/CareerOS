from __future__ import annotations

from collections import Counter
from typing import Counter as CounterType

from app.models.job import Job, JobStatus
from app.models.job_activity import JobActivity, JobActivityType

class ApplicationInsightsService:
    @staticmethod
    def calculate(
        jobs: list[Job],
        activities: list[JobActivity],
    ) -> dict[str, object]:
        total_applications = len(jobs)

        status_counts = Counter(
            job.status.value
            for job in jobs
        )

        applied_count = sum(
            1
            for job in jobs
            if job.status
            in {
                JobStatus.APPLIED,
                JobStatus.INTERVIEW,
                JobStatus.OFFER,
                JobStatus.REJECTED,
                JobStatus.WITHDRAWN,
            }
        )

        interview_count = sum(
            1
            for job in jobs
            if job.status
            in {
                JobStatus.INTERVIEW,
                JobStatus.OFFER,
            }
        )

        offer_count = sum(
            1
            for job in jobs
            if job.status == JobStatus.OFFER
        )

        response_count = sum(
            1
            for job in jobs
            if job.status
            in {
                JobStatus.INTERVIEW,
                JobStatus.OFFER,
                JobStatus.REJECTED,
                JobStatus.WITHDRAWN,
            }
        )

        response_rate = (
            response_count / applied_count * 100
            if applied_count
            else 0.0
        )

        interview_rate = (
            interview_count / applied_count * 100
            if applied_count
            else 0.0
        )

        offer_rate = (
            offer_count / applied_count * 100
            if applied_count
            else 0.0
        )

        transition_counts: CounterType[str] = Counter()

        for activity in activities:
            if (
                activity.type == JobActivityType.STATUS_CHANGED
                and activity.old_status
                and activity.new_status
            ):
                key = (
                    f"{activity.old_status}"
                    f"->{activity.new_status}"
                )
                transition_counts[key] += 1

        return {
            "total_applications": total_applications,
            "applied": applied_count,
            "interviews": interview_count,
            "offers": offer_count,
            "response_count": response_count,
            "response_rate": round(response_rate, 2),
            "interview_rate": round(interview_rate, 2),
            "offer_rate": round(offer_rate, 2),
            "funnel": {
                status.value: status_counts.get(status.value, 0)
                for status in JobStatus
            },
            "status_transitions": dict(
                sorted(transition_counts.items())
            ),
        }