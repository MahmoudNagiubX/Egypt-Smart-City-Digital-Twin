import { expect, test, describe } from 'vitest'
import {
  formatDate,
  formatDistance,
  formatDuration,
  formatInteger,
  formatNumber,
  formatPercent,
  toFiniteNumber,
} from '../utils/format'

describe('Formatting Helper Utilities', () => {
  test('toFiniteNumber works correctly for numbers, numeric strings, and invalid inputs', () => {
    expect(toFiniteNumber(123)).toBe(123)
    expect(toFiniteNumber("456.78")).toBe(456.78)
    expect(toFiniteNumber("12,345")).toBe(null)
    expect(toFiniteNumber(undefined)).toBe(null)
    expect(toFiniteNumber(null)).toBe(null)
    expect(toFiniteNumber("")).toBe(null)
    expect(toFiniteNumber(NaN)).toBe(null)
    expect(toFiniteNumber(Infinity)).toBe(null)
    expect(toFiniteNumber(true)).toBe(null)
    expect(toFiniteNumber({})).toBe(null)
  })

  test('formatNumber formats finite numbers safely', () => {
    expect(formatNumber(undefined)).toBe("—")
    expect(formatNumber(null)).toBe("—")
    expect(formatNumber("")).toBe("—")
    expect(formatNumber(NaN)).toBe("—")
    expect(formatNumber(4.291, 2)).toBe("4.29")
    expect(formatNumber(4.296, 2)).toBe("4.30")
    expect(formatNumber(0, 1)).toBe("0.0")
    expect(formatNumber("3.14159", 4)).toBe("3.1416")
  })

  test('formatInteger formats integers safely using locale formatting', () => {
    expect(formatInteger(undefined)).toBe("—")
    expect(formatInteger(null)).toBe("—")
    expect(formatInteger("")).toBe("—")
    expect(formatInteger(NaN)).toBe("—")
    const result = formatInteger(12480);
    expect(typeof result).toBe('string');
    expect(result).toMatch(/12\D?480/);
    expect(formatInteger(4.6)).toMatch(/5/);
  })

  test('formatPercent appends % only to valid numbers', () => {
    expect(formatPercent(undefined)).toBe("—")
    expect(formatPercent(null)).toBe("—")
    expect(formatPercent("")).toBe("—")
    expect(formatPercent(NaN)).toBe("—")
    expect(formatPercent(57.123, 1)).toBe("57.1%")
    expect(formatPercent(0, 2)).toBe("0.00%")
  })

  test('distance, duration, and date formatters are safe for missing values', () => {
    expect(formatDistance(undefined)).toBe("—")
    expect(formatDistance("5800")).toBe("5.80 km")
    expect(formatDuration(NaN)).toBe("—")
    expect(formatDuration("600")).toBe("10 min")
    expect(formatDate(undefined)).toBe("—")
    expect(formatDate("not-a-date")).toBe("—")
    expect(formatDate("2020-03-12T00:00:00")).toContain("2020")
  })
})
