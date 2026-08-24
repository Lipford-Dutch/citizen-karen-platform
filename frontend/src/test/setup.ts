import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { expect } from "vitest";
import { afterEach } from "vitest";
import { toHaveNoViolations } from "jest-axe";


expect.extend(toHaveNoViolations);

afterEach(() => cleanup());

Object.defineProperty(window, "scrollTo", {
  configurable: true,
  value: () => undefined,
});
