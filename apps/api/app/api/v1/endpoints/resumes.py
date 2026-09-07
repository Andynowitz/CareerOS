from __future__ import annotations

import io
from pathlib import Path
import zipfile
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import get_current_user
from app.db.session import get_db_session
from app.models.resume import Resume, ResumeVersion
from app.schemas.resume import ResumeDetailResponse, ResumeResponse
from app.schemas.user import CurrentUserResponse
from app.services.resume_parser import ResumeParserError, parse_resume
from app.services.resume_storage import ResumeStorage, ResumeStorageError

router = APIRouter(prefix="/resumes", tags=["resumes"])

MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_TYPES = {
    "application/pdf": b"%PDF-",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": b"PK\x03\x04",
}


def validate_file(
    filename: str,
    content_type: str | None,
    data: bytes,
) -> str:
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX resumes are supported",
        )

    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Resume exceeds the 10 MB size limit",
        )

    if not data.startswith(ALLOWED_TYPES[content_type]):
        raise HTTPException(
            status_code=400,
            detail="File content does not match its declared format",
        )

    if content_type == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                names = set(archive.namelist())

                if (
                    "[Content_Types].xml" not in names
                    or "word/document.xml" not in names
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid DOCX file",
                    )

        except zipfile.BadZipFile as exc:
            raise HTTPException(
                status_code=400,
                detail="Invalid DOCX file",
            ) from exc

    if not filename.strip():
        raise HTTPException(
            status_code=400,
            detail="A filename is required",
        )

    return content_type


async def get_resume_or_404(
    resume_id: UUID,
    user_id: str,
    db: AsyncSession,
) -> Resume:
    result = await db.execute(
        select(Resume)
        .where(
            Resume.id == resume_id,
            Resume.user_id == user_id,
        )
        .options(
            selectinload(Resume.versions),
        )
    )

    resume = result.scalar_one_or_none()

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    return resume

@router.get("", response_model=list[ResumeResponse])
async def list_resumes(
    current_user: CurrentUserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[Resume]:
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(Resume.updated_at.desc())
    )

    return list(result.scalars().all())


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: UUID,
    current_user: CurrentUserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> Resume:
    return await get_resume_or_404(
        resume_id,
        current_user.id,
        db,
    )


@router.post(
    "",
    response_model=ResumeDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
    current_user: CurrentUserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> Resume:
    data = await file.read()

    content_type = validate_file(
        file.filename or "resume",
        file.content_type,
        data,
    )

    try:
        extracted_text = parse_resume(
            data,
            content_type,
        )
    except ResumeParserError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    resume = Resume(
        user_id=current_user.id,
        name=(name or file.filename or "Resume").strip(),
    )

    db.add(resume)
    await db.flush()

    version = ResumeVersion(
        resume_id=resume.id,
        version=1,
        filename=file.filename or "resume",
        content_type=content_type,
        size_bytes=len(data),
        object_key="",
        extracted_text=extracted_text,
    )

    db.add(version)
    await db.flush()

    try:
        storage = ResumeStorage()

        version.object_key = storage.put(
            io.BytesIO(data),
            len(data),
            content_type,
            current_user.id,
            resume.id,
            1,
        )

    except ResumeStorageError as exc:
        await db.rollback()

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    try:
        await db.commit()

    except Exception:
        await db.rollback()

        try:
            ResumeStorage().delete(
                version.object_key,
            )
        except ResumeStorageError:
            pass

        raise

    await db.refresh(
        resume,
        ["versions"],
    )

    return resume


@router.post(
    "/{resume_id}/versions",
    response_model=ResumeDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume_version(
    resume_id: UUID,
    file: UploadFile = File(...),
    current_user: CurrentUserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> Resume:
    resume = await get_resume_or_404(
        resume_id=resume_id,
        user_id=current_user.id,
        db=db,
    )

    locked = await db.execute(
        select(Resume)
        .where(Resume.id == resume.id)
        .with_for_update()
    )

    resume = locked.scalar_one()

    data = await file.read()

    content_type = validate_file(
        file.filename or "resume",
        file.content_type,
        data,
    )

    try:
        extracted_text = parse_resume(
            data,
            content_type,
        )
    except ResumeParserError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    next_version = resume.current_version + 1

    version = ResumeVersion(
        resume_id=resume.id,
        version=next_version,
        filename=file.filename or "resume",
        content_type=content_type,
        size_bytes=len(data),
        object_key="",
        extracted_text=extracted_text,
    )

    db.add(version)

    resume.current_version = next_version

    await db.flush()

    try:
        storage = ResumeStorage()

        version.object_key = storage.put(
            io.BytesIO(data),
            len(data),
            content_type,
            current_user.id,
            resume.id,
            next_version,
        )

    except ResumeStorageError as exc:
        await db.rollback()

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    try:
        await db.commit()

    except Exception:
        await db.rollback()

        try:
            ResumeStorage().delete(
                version.object_key,
            )
        except ResumeStorageError:
            pass

        raise

    result = await db.execute(
        select(Resume).where(Resume.id == resume.id)
    )

    resume = result.scalar_one()

    await db.refresh(resume, ["versions"])

    return resume


@router.get(
    "/{resume_id}/versions/{version}/download",
)
async def download_resume(
    resume_id: UUID,
    version: int,
    current_user: CurrentUserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> StreamingResponse:
    resume = await get_resume_or_404(
        resume_id,
        current_user.id,
        db,
    )

    result = await db.execute(
        select(ResumeVersion).where(
            ResumeVersion.resume_id == resume.id,
            ResumeVersion.version == version,
        )
    )

    resume_version = result.scalar_one_or_none()

    if resume_version is None:
        raise HTTPException(
            status_code=404,
            detail="Resume version not found",
        )

    try:
        response = ResumeStorage().get(
            resume_version.object_key,
        )

    except ResumeStorageError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    return StreamingResponse(
        response,
        media_type=resume_version.content_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{Path(resume_version.filename).name}"'
            )
        },
    )


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_resume(
    resume_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUserResponse = Depends(get_current_user),
) -> None:
    resume = await get_resume_or_404(
        resume_id=resume_id,
        user_id=current_user.id,
        db=session,
    )

    storage = ResumeStorage()

    for version in resume.versions:
        try:
            storage.delete(version.object_key)
        except ResumeStorageError:
            pass

    await session.delete(resume)
    await session.commit()