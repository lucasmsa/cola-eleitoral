import { COPY } from '@/config/copy';
import type { NavAction, NavLink } from '@/config/nav';
import { LINKS as EXTERNAL } from '@/config/links';
import type { Screen } from '@/stores/screen';
import type { Turno } from '@/stores/turno';
import { GitHubMark } from './icons';
import { Mascot } from './Mascot';
import { TurnoSwitch } from './TurnoSwitch';
import { Hand } from './ui';

interface Props {
  countdown: string;
  screen: Screen['name'];
  turno: Turno;
  links: NavLink[];
  onTurno: (t: Turno) => void;
  actions: Record<NavAction, () => void>;
}

export function TopBar({ countdown, screen, turno, links, onTurno, actions }: Props) {
  return (
    <header className="screen-only sticky top-0 z-20 border-b-2 border-rule bg-paper/95 backdrop-blur">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-x-2 gap-y-0 px-4 py-1 sm:gap-x-3 xl:gap-x-6 md:py-3">
        <button type="button" onClick={actions.onHome} className="flex min-h-11 items-center gap-2" aria-label="Início">
          <span className="hidden sm:inline-flex">
            <Mascot mood="idle" size={32} />
          </span>
          <span className="font-hand text-xl font-bold leading-none text-ink sm:text-2xl md:text-3xl">{COPY.appName}</span>
        </button>
        <TurnoSwitch turno={turno} onChoose={onTurno} />
        <nav className="order-last -mx-2 flex w-full gap-0.5 xl:order-none xl:mx-0 xl:w-auto xl:gap-1" aria-label="Seções">
          {links.map((l) => (
            <button
              key={l.key}
              type="button"
              onClick={actions[l.action]}
              aria-current={screen === l.key ? 'page' : undefined}
              className={`${l.wideOnly ? 'hidden sm:inline-flex' : 'inline-flex'} min-h-11 items-center whitespace-nowrap rounded-md px-2 text-base font-semibold md:px-3 md:text-lg ${screen === l.key ? 'bg-ink text-paper' : 'text-ink hover:bg-fact'}`}
            >
              {l.label}
            </button>
          ))}
        </nav>
        {countdown && <Hand className="ml-auto hidden text-2xl xl:inline">{countdown}</Hand>}
        <a
          href={EXTERNAL.repo}
          target="_blank"
          rel="noreferrer"
          aria-label={COPY.credits.github}
          className="ml-auto inline-flex size-11 items-center justify-center text-muted hover:text-ink xl:ml-0"
        >
          <GitHubMark />
        </a>
      </div>
    </header>
  );
}
