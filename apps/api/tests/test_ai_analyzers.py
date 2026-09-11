from unittest.mock import MagicMock

import pytest

from app.tasks.job_analysis import analyze_job_task
from app.tasks.resume_analysis import analyze_resume_task
from app.tasks.job_insight import analyze_job_insight_task


# ---------------------------------------------------------------------------
# Job analysis task
# ---------------------------------------------------------------------------


def test_analyze_job_task_success(monkeypatch):
    async def mock_run_analysis(job_id: str) -> str:
        return job_id

    monkeypatch.setattr(
        "app.tasks.job_analysis._run_analysis",
        mock_run_analysis,
    )

    result = analyze_job_task.run("test-job-id")

    assert result == "test-job-id"


def test_analyze_job_task_does_not_retry_value_error(monkeypatch):
    async def mock_run_analysis(job_id: str) -> str:
        raise ValueError("Job has no description to analyze")

    monkeypatch.setattr(
        "app.tasks.job_analysis._run_analysis",
        mock_run_analysis,
    )

    with pytest.raises(ValueError, match="Job has no description"):
        analyze_job_task.run("test-job-id")


def test_analyze_job_task_retries_unexpected_error(monkeypatch):
    async def mock_run_analysis(job_id: str) -> str:
        raise RuntimeError("Temporary AI failure")

    monkeypatch.setattr(
        "app.tasks.job_analysis._run_analysis",
        mock_run_analysis,
    )

    retry_mock = MagicMock(
        side_effect=RuntimeError("Retry requested")
    )

    monkeypatch.setattr(
        analyze_job_task,
        "retry",
        retry_mock,
    )

    with pytest.raises(RuntimeError, match="Retry requested"):
        analyze_job_task.run("test-job-id")

    retry_mock.assert_called_once()

    call_kwargs = retry_mock.call_args.kwargs

    assert isinstance(call_kwargs["exc"], RuntimeError)
    assert call_kwargs["countdown"] == 5


# ---------------------------------------------------------------------------
# Resume analysis task
# ---------------------------------------------------------------------------


def test_analyze_resume_task_success(monkeypatch):
    async def mock_run_analysis(resume_id: str) -> str:
        return resume_id

    monkeypatch.setattr(
        "app.tasks.resume_analysis._run_analysis",
        mock_run_analysis,
    )

    result = analyze_resume_task.run("test-resume-id")

    assert result == "test-resume-id"


def test_analyze_resume_task_does_not_retry_value_error(monkeypatch):
    async def mock_run_analysis(resume_id: str) -> str:
        raise ValueError("Resume has no extracted text to analyze")

    monkeypatch.setattr(
        "app.tasks.resume_analysis._run_analysis",
        mock_run_analysis,
    )

    with pytest.raises(
        ValueError,
        match="Resume has no extracted text",
    ):
        analyze_resume_task.run("test-resume-id")


def test_analyze_resume_task_retries_unexpected_error(monkeypatch):
    async def mock_run_analysis(resume_id: str) -> str:
        raise RuntimeError("Temporary AI failure")

    monkeypatch.setattr(
        "app.tasks.resume_analysis._run_analysis",
        mock_run_analysis,
    )

    retry_mock = MagicMock(
        side_effect=RuntimeError("Retry requested")
    )

    monkeypatch.setattr(
        analyze_resume_task,
        "retry",
        retry_mock,
    )

    with pytest.raises(RuntimeError, match="Retry requested"):
        analyze_resume_task.run("test-resume-id")

    retry_mock.assert_called_once()

    call_kwargs = retry_mock.call_args.kwargs

    assert isinstance(call_kwargs["exc"], RuntimeError)
    assert call_kwargs["countdown"] == 5


# ---------------------------------------------------------------------------
# Job insight task
# ---------------------------------------------------------------------------


def test_analyze_job_insight_task_success(monkeypatch):
    async def mock_run_analysis(
        job_id: str,
        resume_id: str,
    ) -> str:
        return f"{job_id}:{resume_id}"

    monkeypatch.setattr(
        "app.tasks.job_insight._run_analysis",
        mock_run_analysis,
    )

    result = analyze_job_insight_task.run(
        "test-job-id",
        "test-resume-id",
    )

    assert result == "test-job-id:test-resume-id"


def test_analyze_job_insight_task_does_not_retry_value_error(
    monkeypatch,
):
    async def mock_run_analysis(
        job_id: str,
        resume_id: str,
    ) -> str:
        raise ValueError("No job analysis found")

    monkeypatch.setattr(
        "app.tasks.job_insight._run_analysis",
        mock_run_analysis,
    )

    with pytest.raises(
        ValueError,
        match="No job analysis found",
    ):
        analyze_job_insight_task.run(
            "test-job-id",
            "test-resume-id",
        )


def test_analyze_job_insight_task_retries_unexpected_error(
    monkeypatch,
):
    async def mock_run_analysis(
        job_id: str,
        resume_id: str,
    ) -> str:
        raise RuntimeError("Temporary AI failure")

    monkeypatch.setattr(
        "app.tasks.job_insight._run_analysis",
        mock_run_analysis,
    )

    retry_mock = MagicMock(
        side_effect=RuntimeError("Retry requested")
    )

    monkeypatch.setattr(
        analyze_job_insight_task,
        "retry",
        retry_mock,
    )

    with pytest.raises(RuntimeError, match="Retry requested"):
        analyze_job_insight_task.run(
            "test-job-id",
            "test-resume-id",
        )

    retry_mock.assert_called_once()

    call_kwargs = retry_mock.call_args.kwargs

    assert isinstance(call_kwargs["exc"], RuntimeError)
    assert call_kwargs["countdown"] == 5