const DAY_MS = 86_400_000;

function localMidnight(iso: string): number {
  const [y, m, d] = iso.split('-').map(Number) as [number, number, number];
  return new Date(y, m - 1, d).getTime();
}

export function toIsoDate(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export function daysUntil(todayIso: string, targetIso: string): number {
  return Math.round((localMidnight(targetIso) - localMidnight(todayIso)) / DAY_MS);
}

export function countdownLabel(days: number): string {
  if (days > 1) return `Faltam ${days} dias`;
  if (days === 1) return 'Falta 1 dia';
  if (days === 0) return 'É hoje';
  return 'O 1º turno já passou';
}

const MONTHS = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];

export function longDate(iso: string): string {
  const [, m, d] = iso.split('-').map(Number) as [number, number, number];
  return `${d} de ${MONTHS[m - 1]}`;
}

export function electionHeadline(active: { round: 1 | 2; date: string; days: number }): { short: string; long: string } {
  const round = `${active.round}º turno`;
  if (active.days < 0) {
    const passed = `O ${round} já passou`;
    return { short: passed, long: passed };
  }
  if (active.days === 0) return { short: 'É hoje', long: `É hoje: ${round}, ${longDate(active.date)}` };
  const count = countdownLabel(active.days);
  return { short: count, long: `${count} para o ${round}, ${longDate(active.date)}` };
}
