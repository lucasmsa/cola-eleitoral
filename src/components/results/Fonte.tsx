import { COPY } from '@/config/copy';

export function Fonte({ url, label }: { url: string; label: string }) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      title={label}
      aria-label={`${COPY.profile.source}: ${label}`}
      className="ml-1 whitespace-nowrap text-sm font-semibold text-muted underline decoration-line underline-offset-2 hover:text-pen"
    >
      {COPY.profile.source}
    </a>
  );
}
