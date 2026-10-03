import { initials } from '@/lib/portraits';

type Size = 'card' | 'avatar' | 'chip';

const BOX: Record<Size, string> = {
  card: 'w-24 h-[7.5rem]',
  avatar: 'size-12',
  chip: 'size-10',
};

interface Props {
  name: string;
  file: string | null;
  size: Size;
  taped?: boolean;
}

export function Portrait({ name, file, size, taped = false }: Props) {
  const round = size !== 'card';
  return (
    <span className={`relative inline-block shrink-0 ${BOX[size]}`} aria-hidden="true">
      {file ? (
        <img
          src={file}
          alt=""
          loading="lazy"
          className={`size-full ${round ? 'rounded-full border-2 border-edge bg-paper object-cover object-top' : 'object-contain'}`}
        />
      ) : (
        <span
          className={`grid size-full place-items-center border-2 border-dashed border-ink bg-paper font-hand font-bold text-ink ${round ? 'rounded-full text-lg' : '-rotate-2 rounded-sm text-3xl'}`}
        >
          {initials(name)}
        </span>
      )}
      {taped && (
        <span className="absolute -top-2 left-1/2 h-4 w-14 -translate-x-1/2 rotate-[-4deg] bg-[#e9dfc4]/85 shadow-sm" />
      )}
    </span>
  );
}
