import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HomePage from "./page";

describe("HomePage", () => {
  it("renders the CareerOS application", () => {
    render(<HomePage />);

    expect(screen.getByText(/CareerOS/i)).toBeInTheDocument();
  });
});