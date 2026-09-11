from unittest.mock import MagicMock

import pytest

from app.tasks.job_analysis import analyze_job_task


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
    assert "countdown" in call_kwargs