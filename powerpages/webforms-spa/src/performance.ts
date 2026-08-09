const PREFIX = 'tacatdp';
const DEBUG_FLAG = 'TACATDP_DEBUG_PERF';

function canUsePerformance(): boolean {
  return typeof performance !== 'undefined' && typeof performance.mark === 'function';
}

function shouldLogTimings(): boolean {
  if (import.meta.env.DEV) return true;
  if (typeof window === 'undefined') return false;
  return window.localStorage.getItem(DEBUG_FLAG) === 'true';
}

export function markTiming(name: string): void {
  if (!canUsePerformance()) return;
  performance.mark(`${PREFIX}:${name}`);
}

export function measureTiming(name: string, start: number): number {
  const duration = performance.now() - start;
  if (shouldLogTimings()) {
    console.info(`[TACATDP perf] ${name}: ${duration.toFixed(1)}ms`);
  }
  return duration;
}

export async function measureAsync<T>(name: string, operation: () => Promise<T>): Promise<T> {
  const start = performance.now();
  try {
    return await operation();
  } finally {
    measureTiming(name, start);
  }
}

export function logTimingHint(): void {
  if (!shouldLogTimings()) return;
  console.info('[TACATDP perf] timing enabled. Set localStorage.TACATDP_DEBUG_PERF = "true" to enable in production sessions.');
}
