#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const lattice = require("./lattice.js");

const root = path.resolve(__dirname, "../..");
const fixture = JSON.parse(fs.readFileSync(path.join(root, "conformance/profile-v1.json"), "utf8"));
const adversarial = JSON.parse(fs.readFileSync(path.join(root, "examples/address-adversarial.json"), "utf8"));

const actual = lattice.conformanceRecord();
const expectedBytes = lattice.canonicalJsonBytes(fixture);
const actualBytes = lattice.canonicalJsonBytes(actual);
if (!actualBytes.equals(expectedBytes)) {
  throw new Error("JavaScript conformance record diverges from canonical fixture");
}
if (lattice.profileFingerprint() !== fixture.fingerprint) {
  throw new Error("JavaScript profile fingerprint diverges from canonical fixture");
}
if (lattice.lexicographicCells().length !== 27 || new Set(lattice.phiStrideCells()).size !== 27) {
  throw new Error("JavaScript traversal is not a 27-cell bijection");
}
for (const cell of fixture.lexicographic_cells) {
  lattice.parseAddress(cell);
}
for (const testCase of adversarial) {
  let rejected = false;
  try {
    lattice.parseAddress(testCase.address);
  } catch (_error) {
    rejected = true;
  }
  if (!rejected) {
    throw new Error(`JavaScript parser accepted adversarial case: ${testCase.name || "unnamed"}`);
  }
}

process.stdout.write(JSON.stringify({
  status: "valid",
  implementation: "javascript-node",
  profile_id: lattice.PROFILE_ID,
  profile_fingerprint: lattice.profileFingerprint(),
  fixture: "conformance/profile-v1.json",
}) + "\n");
