import { describe, expect, it, vi } from "vitest";

import { getApplicationAssistant } from "./application-assistant-api";

describe("getApplicationAssistant", () => {
  it("requests the assistant endpoint for a job", async () => {
    const mockResponse = {
      job_id: "job-123",
      status: "interview",
      missing_information: [],
      checklist: [
        {
          item: "Prepare for interview",
          completed: false,
        },
      ],
      next_actions: ["Prepare for the upcoming interview."],
      follow_up_needed: false,
      last_activity_at: null,
      days_since_activity: null,
    };

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(mockResponse), {
          status: 200,
          headers: {
            "Content-Type": "application/json",
          },
        }),
      ),
    );

    const result = await getApplicationAssistant("job-123");

    expect(result).toEqual(mockResponse);

    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/jobs/job-123/assistant",
      {
        credentials: "include",
      },
    );
  });

  it("throws when the API request fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(null, {
          status: 404,
        }),
      ),
    );

    await expect(
      getApplicationAssistant("job-123"),
    ).rejects.toThrow("API request failed: 404");
  });
});