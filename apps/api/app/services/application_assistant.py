from __future__ import annotations

from datetime import datetime, timezone

from app.models.job import JobStatus
from app.models.job_activity import JobActivity, JobActivityType


class ApplicationAssistantService:
    @staticmethod
    def build(
        job,
        activities: list[JobActivity],
    ) -> dict:
        missing_information: list[str] = []
        checklist: list[dict[str, object]] = []
        next_actions: list[str] = []

        # Missing job information
        if not job.description or not job.description.strip():
            missing_information.append("Job description")

        if not job.location or not job.location.strip():
            missing_information.append("Job location")

        if not job.url:
            missing_information.append("Job URL")

        # Status-based checklist and next actions
        if job.status == JobStatus.SAVED:
            checklist.extend(
                [
                    {
                        "item": "Review job requirements",
                        "completed": bool(
                            job.description
                            and job.description.strip()
                        ),
                    },
                    {
                        "item": "Prepare application",
                        "completed": False,
                    },
                    {
                        "item": "Submit application",
                        "completed": False,
                    },
                ]
            )

            next_actions.append(
                "Review the job requirements and prepare your application."
            )

            if job.description and job.description.strip():
                next_actions.append(
                    "Submit the application when your documents are ready."
                )

        elif job.status == JobStatus.APPLIED:
            checklist.extend(
                [
                    {
                        "item": "Application submitted",
                        "completed": True,
                    },
                    {
                        "item": "Track employer response",
                        "completed": False,
                    },
                    {
                        "item": "Follow up if appropriate",
                        "completed": False,
                    },
                ]
            )

            next_actions.append(
                "Monitor your application for a response."
            )
            next_actions.append(
                "Consider following up if you have not heard back."
            )

        elif job.status == JobStatus.INTERVIEW:
            checklist.extend(
                [
                    {
                        "item": "Application submitted",
                        "completed": True,
                    },
                    {
                        "item": "Interview scheduled",
                        "completed": True,
                    },
                    {
                        "item": "Prepare for interview",
                        "completed": False,
                    },
                ]
            )

            next_actions.append(
                "Prepare for the upcoming interview."
            )

        elif job.status == JobStatus.OFFER:
            checklist.extend(
                [
                    {
                        "item": "Offer received",
                        "completed": True,
                    },
                    {
                        "item": "Review offer",
                        "completed": False,
                    },
                ]
            )

            next_actions.append(
                "Review the offer and decide on the next step."
            )

        elif job.status == JobStatus.REJECTED:
            checklist.extend(
                [
                    {
                        "item": "Application completed",
                        "completed": True,
                    },
                    {
                        "item": "Record outcome",
                        "completed": True,
                    },
                ]
            )

            next_actions.append(
                "Review the outcome and continue with other applications."
            )

        elif job.status == JobStatus.WITHDRAWN:
            checklist.extend(
                [
                    {
                        "item": "Application withdrawn",
                        "completed": True,
                    },
                ]
            )

            next_actions.append(
                "No further action is required for this application."
            )

        # Activity-based follow-up information
        last_activity_at = None

        if activities:
            last_activity_at = max(
                activity.created_at
                for activity in activities
            )

        days_since_activity = None

        if last_activity_at is not None:
            now = datetime.now(timezone.utc)

            if last_activity_at.tzinfo is None:
                last_activity_at = last_activity_at.replace(
                    tzinfo=timezone.utc
                )

            days_since_activity = (
                now - last_activity_at
            ).days

        follow_up_needed = (
            job.status == JobStatus.APPLIED
            and days_since_activity is not None
            and days_since_activity >= 7
        )

        if follow_up_needed:
            next_actions.insert(
                0,
                "Consider following up on this application.",
            )

        return {
            "job_id": str(job.id),
            "status": job.status.value,
            "missing_information": missing_information,
            "checklist": checklist,
            "next_actions": next_actions,
            "follow_up_needed": follow_up_needed,
            "last_activity_at": last_activity_at,
            "days_since_activity": days_since_activity,
        }