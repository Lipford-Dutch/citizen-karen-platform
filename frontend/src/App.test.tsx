import { fireEvent, render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import App from "./App";


function renderApp(path = "/") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

describe("Citizen Karen app", () => {
  it("renders and filters the official destination directory", () => {
    renderApp("/directory");

    expect(screen.getByRole("heading", { name: /one clear path/i })).toBeInTheDocument();
    fireEvent.change(screen.getByRole("searchbox"), { target: { value: "unsafe workplace" } });
    expect(screen.getByRole("link", { name: /workplace safety/i })).toBeInTheDocument();
  });

  it("renders the FCC form with explicit consent", () => {
    renderApp("/file/fcc");

    expect(screen.getByRole("heading", { name: /tell us what happened/i })).toBeInTheDocument();
    expect(screen.getByRole("checkbox", { name: /authorize citizen karen/i })).toBeRequired();
    expect(screen.getByText(/do not include social security/i)).toBeInTheDocument();
  });

  it("has no detectable axe violations on the directory", async () => {
    const { container } = renderApp("/directory");

    expect(await axe(container)).toHaveNoViolations();
  });

  it("has no detectable axe violations on the FCC form", async () => {
    const { container } = renderApp("/file/fcc");

    expect(await axe(container)).toHaveNoViolations();
  });
});
