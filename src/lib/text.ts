const LOWER = new Set(['de', 'da', 'do', 'das', 'dos', 'e']);

export function titleCase(name: string): string {
  return name
    .toLocaleLowerCase('pt-BR')
    .split(/\s+/)
    .map((word, i) => {
      if (i > 0 && LOWER.has(word)) return word;
      return word.charAt(0).toLocaleUpperCase('pt-BR') + word.slice(1);
    })
    .join(' ');
}

export function brDate(iso: string): string {
  const [y, m, d] = iso.slice(0, 10).split('-');
  return `${d}/${m}/${y}`;
}

export function percent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function brNumber(n: number): string {
  return String(n).replace('.', ',');
}

export function pollValue(pct: number): string {
  return pct === 0 ? 'não pontuou' : `${brNumber(pct)}%`;
}

export function hostname(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}
