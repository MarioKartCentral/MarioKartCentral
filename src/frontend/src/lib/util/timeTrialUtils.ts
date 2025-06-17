/**
 * Time trial utility functions following established patterns.
 */

import type { ProofRequestData } from '$lib/types/time-trials';

export interface ParsedTime {
  minutes: number;
  seconds: number;
  milliseconds: number;
  totalMs: number;
}

export interface TimeValidationError {
  message: string;
  code: string;
}

/**
 * Parse time string into components following established validation patterns.
 * @param timeString - Time in format "M:SS.mmm" or "SS.mmm"
 * @returns Parsed time components or throws error
 */
export function parseTimeString(timeString: string): ParsedTime {
  if (!timeString?.trim()) {
    throw new Error('Time is required');
  }

  const trimmed = timeString.trim();
  const timeParts = trimmed.match(/^(?:(\d{1,2}):)?(\d{1,2})\.(\d{3})$/);

  if (!timeParts) {
    throw new Error('Invalid time format. Please use M:SS.mmm or SS.mmm (e.g., 1:23.456 or 58.789)');
  }

  const minutes = timeParts[1] ? parseInt(timeParts[1]) : 0;
  const seconds = parseInt(timeParts[2]);
  const milliseconds = parseInt(timeParts[3]);

  // Validate ranges following established patterns
  if (minutes < 0 || minutes > 59) {
    throw new Error('Minutes must be between 0 and 59');
  }

  if (seconds < 0 || seconds >= 60) {
    throw new Error('Seconds must be between 0 and 59');
  }

  if (milliseconds < 0 || milliseconds >= 1000) {
    throw new Error('Milliseconds must be between 0 and 999');
  }

  const totalMs = minutes * 60 * 1000 + seconds * 1000 + milliseconds;

  if (totalMs <= 0) {
    throw new Error('Time must be greater than 0');
  }

  return {
    minutes,
    seconds,
    milliseconds,
    totalMs,
  };
}

/**
 * Format milliseconds back to time string for display.
 * @param totalMs - Total milliseconds
 * @returns Formatted time string
 */
export function formatTimeMs(totalMs: number): string {
  if (totalMs <= 0) return '0:00.000';

  const minutes = Math.floor(totalMs / 60000);
  const seconds = Math.floor((totalMs % 60000) / 1000);
  const milliseconds = totalMs % 1000;

  if (minutes > 0) {
    return `${minutes}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
  } else {
    return `${seconds}.${milliseconds.toString().padStart(3, '0')}`;
  }
}

/**
 * Validate proof data following established patterns.
 * @param proofs - Array of proof objects
 * @returns Validation errors or empty array if valid
 */
export function validateProofs(proofs: Array<ProofRequestData>): string[] {
  const errors: string[] = [];

  // Proofs are optional, so empty array is valid
  if (proofs.length === 0) {
    return errors;
  }

  proofs.forEach((proof, index) => {
    const proofNum = index + 1;

    if (!proof.url?.trim()) {
      errors.push(`Proof ${proofNum}: URL is required`);
    } else {
      // Basic URL validation
      try {
        new URL(proof.url.trim());
      } catch {
        errors.push(`Proof ${proofNum}: Invalid URL format`);
      }
    }

    if (!proof.type?.trim()) {
      errors.push(`Proof ${proofNum}: Type is required`);
    }
  });

  return errors;
}
