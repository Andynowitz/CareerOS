from io import BytesIO

from httpx import AsyncClient
import pytest

def pdf_bytes() -> bytes:
    return b"%PDF-1.4 fake pdf content"


class FakeStorage:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def put(
        self,
        data,
        size,
        content_type,
        user_id,
        resume_id,
        version,
    ) -> str:
        key = f"{user_id}/{resume_id}/v{version}"
        self.objects[key] = data.read()
        return key

    def get(self, object_key):
        return BytesIO(self.objects[object_key])

    def delete(self, object_key) -> None:
        self.objects.pop(object_key, None)


async def test_list_resumes(client: AsyncClient) -> None:
    response = await client.get("/api/v1/resumes")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_resume_upload(
    client: AsyncClient,
    monkeypatch,
) -> None:
    fake = FakeStorage()

    from app.api.v1.endpoints import resumes as resumes_endpoint

    monkeypatch.setattr(
        resumes_endpoint,
        "ResumeStorage",
        lambda: fake,
    )

    monkeypatch.setattr(
        resumes_endpoint,
        "parse_resume",
        lambda data, content_type: "John Doe\nSoftware Engineer",
    )

    response = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "cv.pdf",
                BytesIO(pdf_bytes()),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "cv.pdf"
    assert body["current_version"] == 1
    assert len(body["versions"]) == 1
    assert body["versions"][0]["version"] == 1


async def test_resume_version_upload(
    client: AsyncClient,
    monkeypatch,
) -> None:
    fake = FakeStorage()

    from app.api.v1.endpoints import resumes as resumes_endpoint

    monkeypatch.setattr(
        resumes_endpoint,
        "ResumeStorage",
        lambda: fake,
    )

    monkeypatch.setattr(
        resumes_endpoint,
        "parse_resume",
        lambda data, content_type: "text",
    )

    created = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "cv.pdf",
                BytesIO(pdf_bytes()),
                "application/pdf",
            )
        },
    )

    resume_id = created.json()["id"]

    response = await client.post(
        f"/api/v1/resumes/{resume_id}/versions",
        files={
            "file": (
                "cv-v2.pdf",
                BytesIO(pdf_bytes()),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["current_version"] == 2
    assert len(body["versions"]) == 2


async def test_resume_upload_rejects_large_file(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "cv.pdf",
                BytesIO(b"x" * (10 * 1024 * 1024 + 1)),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413


async def test_resume_upload_rejects_invalid_type(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "cv.txt",
                BytesIO(b"hello"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


async def test_resume_download(
    client: AsyncClient,
    monkeypatch,
) -> None:
    fake = FakeStorage()

    from app.api.v1.endpoints import resumes as resumes_endpoint

    monkeypatch.setattr(
        resumes_endpoint,
        "ResumeStorage",
        lambda: fake,
    )

    monkeypatch.setattr(
        resumes_endpoint,
        "parse_resume",
        lambda data, content_type: "text",
    )

    created = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "cv.pdf",
                BytesIO(pdf_bytes()),
                "application/pdf",
            )
        },
    )

    resume_id = created.json()["id"]

    response = await client.get(
        f"/api/v1/resumes/{resume_id}/versions/1/download"
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/pdf"
    )


async def test_resume_delete_removes_storage(
    client: AsyncClient,
    monkeypatch,
) -> None:
    fake = FakeStorage()

    from app.api.v1.endpoints import resumes as resumes_endpoint

    monkeypatch.setattr(
        resumes_endpoint,
        "ResumeStorage",
        lambda: fake,
    )

    monkeypatch.setattr(
        resumes_endpoint,
        "parse_resume",
        lambda data, content_type: "text",
    )

    created = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "cv.pdf",
                BytesIO(pdf_bytes()),
                "application/pdf",
            )
        },
    )

    resume_id = created.json()["id"]

    assert fake.objects

    deleted = await client.delete(
        f"/api/v1/resumes/{resume_id}"
    )

    assert deleted.status_code == 204
    assert not fake.objects


async def test_resume_upload_rejects_invalid_docx_structure(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "resume.docx",
                BytesIO(b"PK\x03\x04not-a-real-docx"),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("filename", "content", "content_type", "expected_status"),
    [
        (
            "resume.txt",
            b"plain text",
            "text/plain",
            400,
        ),
        (
            "resume.pdf",
            b"not-a-real-pdf",
            "application/pdf",
            400,
        ),
        (
            "resume.docx",
            b"not-a-real-docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            400,
        ),
    ],
)
async def test_resume_file_validation_rejects_invalid_files(
    client: AsyncClient,
    filename: str,
    content: bytes,
    content_type: str,
    expected_status: int,
) -> None:
    response = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                filename,
                BytesIO(content),
                content_type,
            )
        },
    )

    assert response.status_code == expected_status


async def test_resume_file_validation_rejects_oversized_file(
    client: AsyncClient,
) -> None:
    oversized_pdf = b"%PDF-" + b"x" * (10 * 1024 * 1024)

    response = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "large.pdf",
                BytesIO(oversized_pdf),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Resume exceeds the 10 MB size limit"


async def test_resume_file_validation_rejects_mime_signature_mismatch(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "resume.pdf",
                BytesIO(b"this-is-not-a-pdf"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "File content does not match its declared format"
    )


async def test_resume_file_validation_rejects_empty_filename(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "   ",
                BytesIO(pdf_bytes()),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "A filename is required"


async def test_other_user_cannot_get_resume(
    client: AsyncClient,
    as_second_user,
    monkeypatch,
) -> None:
    fake = FakeStorage()

    from app.api.v1.endpoints import resumes as resumes_endpoint

    monkeypatch.setattr(
        resumes_endpoint,
        "ResumeStorage",
        lambda: fake,
    )

    monkeypatch.setattr(
        resumes_endpoint,
        "parse_resume",
        lambda data, content_type: "text",
    )

    created = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "cv.pdf",
                BytesIO(pdf_bytes()),
                "application/pdf",
            )
        },
    )

    resume_id = created.json()["id"]

    async with as_second_user():
        response = await client.get(
            f"/api/v1/resumes/{resume_id}"
        )

    assert response.status_code == 404


async def test_other_user_cannot_upload_resume_version(
    client: AsyncClient,
    as_second_user,
    monkeypatch,
) -> None:
    fake = FakeStorage()

    from app.api.v1.endpoints import resumes as resumes_endpoint

    monkeypatch.setattr(
        resumes_endpoint,
        "ResumeStorage",
        lambda: fake,
    )

    monkeypatch.setattr(
        resumes_endpoint,
        "parse_resume",
        lambda data, content_type: "text",
    )

    created = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "cv.pdf",
                BytesIO(pdf_bytes()),
                "application/pdf",
            )
        },
    )

    resume_id = created.json()["id"]

    async with as_second_user():
        response = await client.post(
            f"/api/v1/resumes/{resume_id}/versions",
            files={
                "file": (
                    "cv-v2.pdf",
                    BytesIO(pdf_bytes()),
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 404


async def test_other_user_cannot_download_resume(
    client: AsyncClient,
    as_second_user,
    monkeypatch,
) -> None:
    fake = FakeStorage()

    from app.api.v1.endpoints import resumes as resumes_endpoint

    monkeypatch.setattr(
        resumes_endpoint,
        "ResumeStorage",
        lambda: fake,
    )

    monkeypatch.setattr(
        resumes_endpoint,
        "parse_resume",
        lambda data, content_type: "text",
    )

    created = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "cv.pdf",
                BytesIO(pdf_bytes()),
                "application/pdf",
            )
        },
    )

    resume_id = created.json()["id"]

    async with as_second_user():
        response = await client.get(
            f"/api/v1/resumes/{resume_id}/versions/1/download"
        )

    assert response.status_code == 404


async def test_other_user_cannot_delete_resume(
    client: AsyncClient,
    as_second_user,
    monkeypatch,
) -> None:
    fake = FakeStorage()

    from app.api.v1.endpoints import resumes as resumes_endpoint

    monkeypatch.setattr(
        resumes_endpoint,
        "ResumeStorage",
        lambda: fake,
    )

    monkeypatch.setattr(
        resumes_endpoint,
        "parse_resume",
        lambda data, content_type: "text",
    )

    created = await client.post(
        "/api/v1/resumes",
        files={
            "file": (
                "cv.pdf",
                BytesIO(pdf_bytes()),
                "application/pdf",
            )
        },
    )

    resume_id = created.json()["id"]

    async with as_second_user():
        response = await client.delete(
            f"/api/v1/resumes/{resume_id}"
        )

    assert response.status_code == 404

    # Original user's resume must still exist.
    response = await client.get(
        f"/api/v1/resumes/{resume_id}"
    )

    assert response.status_code == 200

