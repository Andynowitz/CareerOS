import asyncio

from sqlalchemy import select

from app.ai.analyzers.job_analyzer import JobAnalyzer
from app.ai.client import AIClient
from app.db.session import AsyncSessionLocal
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.repositories.job_analysis import JobAnalysisRepository
from app.services.job_analysis import JobAnalysisService


async def main() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Job).limit(1)
        )

        job = result.scalar_one_or_none()

        if job is None:
            print("No job found.")
            return

        # Use a realistic description for this test.
        job_description = """
        We are looking for a Backend Java Developer to join our team.

        Requirements:
        - Strong Java knowledge
        - Spring Boot experience
        - PostgreSQL
        - REST API development
        - At least 2 years of professional experience
        - Bachelor's degree in Computer Science or a related field

        Responsibilities:
        - Develop and maintain backend services
        - Design REST APIs
        - Work with PostgreSQL databases
        - Collaborate with frontend developers

        Nice to have:
        - Docker
        - Kubernetes
        - AWS

        Salary: EUR 3,500 - 4,500 gross per month.
        """

        client = AIClient()
        analyzer = JobAnalyzer(client)
        repository = JobAnalysisRepository(session)

        service = JobAnalysisService(
            analyzer=analyzer,
            repository=repository,
        )

        analysis = await service.analyze_job(
            job_id=job.id,
            job_description=job_description,
        )

        print("\n=== SAVED AI ANALYSIS ===")
        print({
            "id": analysis.id,
            "job_id": analysis.job_id,
            "required_skills": analysis.required_skills,
            "preferred_skills": analysis.preferred_skills,
            "responsibilities": analysis.responsibilities,
            "experience_requirements": analysis.experience_requirements,
            "education_requirements": analysis.education_requirements,
            "keywords": analysis.keywords,
            "salary_information": analysis.salary_information,
        })

        saved = await session.get(
            JobAnalysis,
            analysis.id,
        )

        if saved is None:
            raise RuntimeError(
                "Analysis was not found in the database."
            )

        print("\nDatabase verification successful.")


if __name__ == "__main__":
    asyncio.run(main())