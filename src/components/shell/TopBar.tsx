import { COPY } from '@/config/copy';
import type { Screen } from '@/stores/screen';
import { Hand } from './ui';
import { Mascot } from './Mascot';
import { GitHubMark } from './icons';
import { LINKS as EXTERNAL } from '@/config/links';

interface Props {
  countdown: string;
  screen: Screen['name'];
  onHome: () => void;
  onResults: () => void;
  onReview: () => void;
  onCola: () => void;
}

const LINKS: { key: Screen['name']; label: string; action: keyof Omit<Props, 'countdown' | 'screen'> }[] = [
  { key: 'home', label: 'Início', action: 'onHome' },
  { key: 'results', label: 'Resultado', action: 'onResults' },
  { key: 'review', label: 'Quiz', action: 'onReview' },
  { key: 'cola', label: 'Cola', action: 'onCola' },
];

export function TopBar(props: Props) {
  return (
    <header className="screen-only sticky top-0 z-20 border-b-2 border-rule bg-paper/95 backdrop-blur">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-x-6 gap-y-0 px-4 py-1 md:py-3">
        <button type="button" onClick={props.onHome} className="flex min-h-11 items-center gap-2" aria-label="Início">
          <Mascot mood="idle" size={32} />
          <span className="font-hand text-2xl font-bold leading-none text-ink md:text-3xl">{COPY.appName}</span>
        </button>
        <nav className="order-last -mx-2 flex w-full gap-0.5 md:order-none md:mx-0 md:w-auto md:gap-1" aria-label="Seções">
          {LINKS.map((l) => (
            <button
              key={l.key}
              type="button"
              onClick={props[l.action]}
              aria-current={props.screen === l.key ? 'page' : undefined}
              className={`inline-flex min-h-11 items-center rounded-md px-2 text-base font-semibold md:px-3 md:text-lg ${props.screen === l.key ? 'bg-ink text-paper' : 'text-ink hover:bg-fact'}`}
            >
              {l.label}
            </button>
          ))}
        </nav>
        <Hand className="ml-auto hidden text-xl sm:inline md:text-2xl">{props.countdown}</Hand>
        <a
          href={EXTERNAL.repo}
          target="_blank"
          rel="noreferrer"
          aria-label={COPY.credits.github}
          className="ml-auto inline-flex size-11 items-center justify-center text-muted hover:text-ink sm:ml-0"
        >
          <GitHubMark />
        </a>
      </div>
    </header>
  );
}
