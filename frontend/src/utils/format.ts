export const EMPTY_VALUE = "—";

export function toFiniteNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  if (typeof value !== "number" && typeof value !== "string") {
    return null;
  }
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

export function formatNumber(
  value: unknown,
  digits = 2,
  fallback = EMPTY_VALUE,
): string {
  const number = toFiniteNumber(value);
  if (number === null) {
    return fallback;
  }
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(number);
}

export function formatInteger(value: unknown, fallback = EMPTY_VALUE): string {
  const number = toFiniteNumber(value);
  if (number === null) {
    return fallback;
  }
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(
    number,
  );
}

export function formatPercent(
  value: unknown,
  digits = 1,
  fallback = EMPTY_VALUE,
): string {
  const formatted = formatNumber(value, digits, fallback);
  return formatted === fallback ? fallback : `${formatted}%`;
}

export function formatDistance(value: unknown, fallback = EMPTY_VALUE): string {
  const meters = toFiniteNumber(value);
  return meters === null ? fallback : `${formatNumber(meters / 1000, 2)} km`;
}

export function formatDuration(value: unknown, fallback = EMPTY_VALUE): string {
  const seconds = toFiniteNumber(value);
  return seconds === null ? fallback : `${formatInteger(seconds / 60)} min`;
}

export function formatDate(value: unknown, fallback = EMPTY_VALUE): string {
  if (typeof value !== "string" && typeof value !== "number") {
    return fallback;
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return fallback;
  }
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}
