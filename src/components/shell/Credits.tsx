import { COPY } from '@/config/copy';
import { LINKS } from '@/config/links';

const LINK = 'inline-flex min-h-11 items-center whitespace-nowrap font-semibold text-ink underline decoration-pen/60 decoration-2 underline-offset-4 hover:text-pen';

export function Credits() {
  return (
    <footer className="screen-only mx-auto flex w-full max-w-5xl flex-wrap gap-x-6 gap-y-2 px-4 pb-10 pt-4 text-lg md:pl-24">
      <a href={LINKS.github} target="_blank" rel="noreferrer" className={LINK}>
        {COPY.credits.madeBy}
      </a>
      <a href={LINKS.repo} target="_blank" rel="noreferrer" className={LINK}>
        {COPY.credits.source}
      </a>
      <p className="w-full text-base text-ink/80">
        {COPY.credits.disclaimer} {COPY.credits.correction}{' '}
        <a href={`mailto:${COPY.credits.email}`} className={LINK}>
          {COPY.credits.email}
        </a>
        .
      </p>
    </footer>
  );
}
