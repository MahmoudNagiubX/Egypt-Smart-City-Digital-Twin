export function toFiniteNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  if (typeof value !== "number" && typeof value !== "string") {
    return null;
  }
  const num = Number(value);
  if (Number.isFinite(num)) {
    return num;
  }
  return null;
}

export function formatNumber(value: unknown, digits = 2, fallback = "—"): string {
  const num = toFiniteNumber(value);
  if (num === null) {
    return fallback;
  }
  return num.toFixed(digits);
}

export function formatInteger(value: unknown, fallback = "—"): string {
  const num = toFiniteNumber(value);
  if (num === null) {
    return fallback;
  }
  return Math.round(num).toLocaleString();
}

export function formatPercent(value: unknown, digits = 1, fallback = "—"): string {
  const num = toFiniteNumber(value);
  if (num === null) {
    return fallback;
  }
  return `${num.toFixed(digits)}%`;
}
