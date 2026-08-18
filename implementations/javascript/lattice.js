"use strict";

const crypto = require("crypto");

const PROFILE_ID = "qsol-3x3x3-sierpinski-derived-memory/1";
const LEXICOGRAPHIC_TRAVERSAL = "qsol.lexicographic-27/1";
const PHI_STRIDE_TRAVERSAL = "qsol.phi-stride-27/1";
const PHI_STRIDE = 17;
const TOP_LEVEL_CELL_COUNT = 27;
const MAX_RECURSIVE_DEPTH = 8;
const MAX_ADDRESS_LENGTH = 71;
const CONFORMANCE_PROTOCOL = "qsol-lattice-conformance/1";
const SEGMENT_RE = /^L\[([0-2]),([0-2]),([0-2])\]$/;

function lexicographicCells() {
  const cells = [];
  for (let x = 0; x < 3; x += 1) {
    for (let y = 0; y < 3; y += 1) {
      for (let z = 0; z < 3; z += 1) {
        cells.push(`L[${x},${y},${z}]`);
      }
    }
  }
  if (cells.length !== 27 || new Set(cells).size !== 27) {
    throw new Error("canonical profile must contain exactly 27 unique cells");
  }
  return cells;
}

function phiStrideCells() {
  const cells = lexicographicCells();
  const order = [];
  for (let step = 0; step < TOP_LEVEL_CELL_COUNT; step += 1) {
    order.push(cells[(step * PHI_STRIDE) % TOP_LEVEL_CELL_COUNT]);
  }
  if (new Set(order).size !== TOP_LEVEL_CELL_COUNT) {
    throw new Error("phi traversal must visit every cell exactly once");
  }
  return order;
}

function parseAddress(address, maxDepth = MAX_RECURSIVE_DEPTH) {
  if (!Number.isInteger(maxDepth) || maxDepth < 1 || maxDepth > MAX_RECURSIVE_DEPTH) {
    throw new Error(`max_depth must be 1..${MAX_RECURSIVE_DEPTH}`);
  }
  if (typeof address !== "string" || address.length === 0) {
    throw new Error("address must be a non-empty string");
  }
  if (address.length > maxDepth * 8 + (maxDepth - 1)) {
    throw new Error("address exceeds canonical length limit");
  }
  const parts = address.split("/");
  if (parts.length > maxDepth) {
    throw new Error("address exceeds recursive depth limit");
  }
  return parts.map((segment) => {
    const match = SEGMENT_RE.exec(segment);
    if (match === null || match[0].length !== segment.length) {
      throw new Error("invalid lattice address");
    }
    return [Number(match[1]), Number(match[2]), Number(match[3])];
  });
}

function sortJson(value) {
  if (Array.isArray(value)) {
    return value.map(sortJson);
  }
  if (value !== null && typeof value === "object") {
    const output = {};
    for (const key of Object.keys(value).sort()) {
      output[key] = sortJson(value[key]);
    }
    return output;
  }
  if (typeof value === "number" && !Number.isFinite(value)) {
    throw new Error("non-finite JSON number");
  }
  return value;
}

function canonicalJsonBytes(value) {
  return Buffer.from(JSON.stringify(sortJson(value)), "utf8");
}

function conformancePayload() {
  return {
    protocol: CONFORMANCE_PROTOCOL,
    profile_id: PROFILE_ID,
    lexicographic_traversal_id: LEXICOGRAPHIC_TRAVERSAL,
    phi_traversal_id: PHI_STRIDE_TRAVERSAL,
    phi_stride: PHI_STRIDE,
    modulus: TOP_LEVEL_CELL_COUNT,
    max_recursive_depth: MAX_RECURSIVE_DEPTH,
    max_address_length: MAX_ADDRESS_LENGTH,
    lexicographic_cells: lexicographicCells(),
    phi_stride_cells: phiStrideCells(),
  };
}

function profileFingerprint() {
  const digest = crypto.createHash("sha256").update(canonicalJsonBytes(conformancePayload())).digest("hex");
  return `sha256:${digest}`;
}

function conformanceRecord() {
  return { fingerprint: profileFingerprint(), ...conformancePayload() };
}

module.exports = {
  CONFORMANCE_PROTOCOL,
  LEXICOGRAPHIC_TRAVERSAL,
  MAX_ADDRESS_LENGTH,
  MAX_RECURSIVE_DEPTH,
  PHI_STRIDE,
  PHI_STRIDE_TRAVERSAL,
  PROFILE_ID,
  TOP_LEVEL_CELL_COUNT,
  canonicalJsonBytes,
  conformancePayload,
  conformanceRecord,
  lexicographicCells,
  parseAddress,
  phiStrideCells,
  profileFingerprint,
};
