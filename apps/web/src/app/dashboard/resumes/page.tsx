"use client";

import { ChangeEvent, useEffect, useState } from "react";

import {
  deleteResume,
  getResume,
  getResumes,
  uploadResume,
  uploadResumeVersion,
  getResumeDownloadUrl,
  type Resume,
  type ResumeDetail,
} from "@/lib/resumes-api";

const MAX_SIZE = 10 * 1024 * 1024;

const ACCEPTED =
  ".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document";

function formatBytes(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedResume, setSelectedResume] =
    useState<string | null>(null);
  const [name, setName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] =
    useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] =
    useState(false);
  const [expanded, setExpanded] =
    useState<string | null>(null);
  const [details, setDetails] =
    useState<Record<string, ResumeDetail>>({});

  async function loadResumes() {
    try {
      setError(null);
      setResumes(await getResumes());
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load resumes.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadResumes();
  }, []);

  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const next =
      event.target.files?.[0] ?? null;

    setFile(next);
    setError(null);

    if (next && next.size > MAX_SIZE) {
      setError(
        "The file must be 10 MB or smaller.",
      );
    }
  }

  async function handleUpload() {
    if (!file || file.size > MAX_SIZE) {
      return;
    }

    try {
      setIsUploading(true);
      setError(null);

      if (selectedResume) {
        await uploadResumeVersion(
          selectedResume,
          file,
        );
      } else {
        await uploadResume(file, name);
      }

      setFile(null);
      setName("");
      setSelectedResume(null);

      await loadResumes();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to upload resume.",
      );
    } finally {
      setIsUploading(false);
    }
  }

  async function toggleDetails(id: string) {
    if (expanded === id) {
      setExpanded(null);
      return;
    }

    try {
      setError(null);

      if (!details[id]) {
        const detail = await getResume(id);

        setDetails((current) => ({
          ...current,
          [id]: detail,
        }));
      }

      setExpanded(id);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load resume versions.",
      );
    }
  }

  async function handleDelete(id: string) {
    if (
      !window.confirm(
        "Delete this resume and all its versions?",
      )
    ) {
      return;
    }

    try {
      setError(null);

      await deleteResume(id);
      await loadResumes();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete resume.",
      );
    }
  }

  return (
    <main className="mx-auto max-w-4xl space-y-8 p-6">
      <div>
        <h1 className="text-3xl font-bold">
          Resumes
        </h1>

        <p className="mt-2 text-gray-600">
          Upload, manage and version your resumes.
        </p>
      </div>

      {error && (
        <p className="rounded border border-red-300 p-3 text-red-600">
          {error}
        </p>
      )}

      <section className="space-y-4 rounded-lg border p-5">
        <h2 className="text-xl font-semibold">
          {selectedResume
            ? "Upload new version"
            : "Upload resume"}
        </h2>

        {!selectedResume && (
          <input
            value={name}
            onChange={(e) =>
              setName(e.target.value)
            }
            placeholder="Resume name (optional)"
            className="w-full rounded border px-3 py-2"
          />
        )}

        <input
          type="file"
          accept={ACCEPTED}
          onChange={handleFileChange}
        />

        <p className="text-sm text-gray-500">
          PDF or DOCX, maximum 10 MB.
        </p>

        {selectedResume && (
          <button
            type="button"
            onClick={() =>
              setSelectedResume(null)
            }
            className="mr-3 text-sm underline"
          >
            Cancel version upload
          </button>
        )}

        <button
          type="button"
          disabled={
            !file ||
            isUploading ||
            !!error
          }
          onClick={() =>
            void handleUpload()
          }
          className="rounded bg-black px-4 py-2 text-white disabled:opacity-50"
        >
          {isUploading
            ? "Uploading..."
            : selectedResume
              ? "Upload version"
              : "Upload resume"}
        </button>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">
          Your resumes
        </h2>

        {isLoading ? (
          <p>Loading...</p>
        ) : resumes.length === 0 ? (
          <p className="text-gray-600">
            No resumes uploaded yet.
          </p>
        ) : (
          resumes.map((resume) => (
            <article
              key={resume.id}
              className="rounded-lg border p-5"
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h3 className="font-semibold">
                    {resume.name}
                  </h3>

                  <p className="text-sm text-gray-500">
                    Current version:{" "}
                    {resume.current_version}
                  </p>

                  <p className="text-sm text-gray-500">
                    Updated:{" "}
                    {new Date(
                      resume.updated_at,
                    ).toLocaleString()}
                  </p>
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() =>
                      void toggleDetails(
                        resume.id,
                      )
                    }
                    className="rounded border px-3 py-2 text-sm"
                  >
                    {expanded === resume.id
                      ? "Hide versions"
                      : "View versions"}
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      setSelectedResume(
                        resume.id,
                      )
                    }
                    className="rounded border px-3 py-2 text-sm"
                  >
                    New version
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      void handleDelete(
                        resume.id,
                      )
                    }
                    className="rounded border border-red-300 px-3 py-2 text-sm text-red-600"
                  >
                    Delete
                  </button>
                </div>
              </div>

              {expanded === resume.id &&
                details[resume.id] && (
                  <div className="mt-5 border-t pt-4">
                    <h4 className="font-medium">
                      Versions
                    </h4>

                    <ul className="mt-2 space-y-2">
                      {details[resume.id]?.versions.map( (version) => (
                          <li
                            key={version.id}
                            className="flex flex-wrap items-center justify-between gap-3 text-sm"
                          >
                            <span>
                              v
                              {version.version}{" "}
                              ·{" "}
                              {version.filename}{" "}
                              ·{" "}
                              {formatBytes(
                                version.size_bytes,
                              )}
                            </span>

                            <a
                              href={getResumeDownloadUrl(
                                resume.id,
                                version.version,
                              )}
                              className="underline"
                            >
                              Download
                            </a>
                          </li>
                        ),
                      )}
                    </ul>
                  </div>
                )}
            </article>
          ))
        )}
      </section>
    </main>
  );
}