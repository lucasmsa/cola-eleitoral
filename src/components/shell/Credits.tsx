import { COPY } from '@/config/copy';
import { LINKS } from '@/config/links';
import { useCredits } from '@/hooks/useCredits';

const LINK = 'inline-flex min-h-11 items-center whitespace-nowrap font-semibold text-ink underline decoration-pen/60 decoration-2 underline-offset-4 hover:text-pen';

export function Credits() {
  const credits = useCredits();
  return (
    <footer className="screen-only mx-auto flex w-full max-w-5xl flex-wrap gap-x-6 gap-y-2 px-4 pb-10 pt-4 text-lg md:pl-24">
      <a href={LINKS.author} target="_blank" rel="author noreferrer" className={LINK}>
        {COPY.credits.madeBy}
      </a>
      <a href={LINKS.repo} target="_blank" rel="noreferrer" className={LINK}>
        {COPY.credits.source}
      </a>
      {credits.showCoffee && (
        <a href={LINKS.coffee} target="_blank" rel="noreferrer" className={LINK}>
          {COPY.credits.coffee}
        </a>
      )}
    </footer>
  );
}
