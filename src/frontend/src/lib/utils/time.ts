/**
 * Time formatting utilities for Mario Kart Central
 */

/**
 * Format milliseconds into MM:SS.mmm or SS.mmm format
 */
export function formatTime(timeMs: number): string {
  const minutes = Math.floor(timeMs / 60000);
  const seconds = Math.floor((timeMs % 60000) / 1000);
  const milliseconds = timeMs % 1000;

  if (minutes > 0) {
    return `${minutes}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
  } else {
    return `${seconds}.${milliseconds.toString().padStart(3, '0')}`;
  }
}

/**
 * Parse time string (MM:SS.mmm or SS.mmm) to milliseconds
 */
export function parseTimeToMs(timeStr: string): number {
  const parts = timeStr.split(':');
  let minutes = 0;
  let secondsPart = '';

  if (parts.length === 2) {
    minutes = parseInt(parts[0], 10);
    secondsPart = parts[1];
  } else {
    secondsPart = parts[0];
  }

  const [seconds, milliseconds] = secondsPart.split('.');
  const secondsNum = parseInt(seconds, 10);
  const millisecondsNum = parseInt(milliseconds?.padEnd(3, '0') || '0', 10);

  return (minutes * 60 + secondsNum) * 1000 + millisecondsNum;
}
