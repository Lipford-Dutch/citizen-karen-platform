import { describe, expect, it } from "vitest";

import { agencies, searchAgencies } from "./agencies";


describe("agency directory", () => {
  it("preserves the de-duplicated repository research directory", () => {
    expect(agencies).toHaveLength(28);
    expect(new Set(agencies.map((agency) => agency.slug)).size).toBe(28);
  });

  it("matches plain-language problems", () => {
    expect(searchAgencies("unsafe workplace").map((agency) => agency.slug)).toContain("osha");
    expect(searchAgencies("robocall").map((agency) => agency.slug)).toEqual(["fcc"]);
    expect(searchAgencies("lost package").map((agency) => agency.slug)).toContain("usps");
  });

  it("returns all destinations for an empty query", () => {
    expect(searchAgencies("  ")).toEqual(agencies);
  });
});
