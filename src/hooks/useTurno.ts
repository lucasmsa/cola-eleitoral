import { NAV_BY_TURNO } from '@/config/nav';
import { useScreenStore } from '@/stores/screen';
import { useTurnoStore, type Turno } from '@/stores/turno';

const SHARED = new Set(['home', 'lesson']);

export function useTurno() {
  const turno = useTurnoStore((s) => s.turno);
  const setTurno = useTurnoStore((s) => s.setTurno);
  const screen = useScreenStore((s) => s.screen);
  const go = useScreenStore((s) => s.go);
  const choose = (next: Turno) => {
    if (next === turno) return;
    setTurno(next);
    const valid = SHARED.has(screen.name) || NAV_BY_TURNO[next].some((l) => l.key === screen.name);
    if (!valid) go({ name: 'home' });
  };
  return { turno, links: NAV_BY_TURNO[turno], choose };
}
