import type { Candidate, Claim, Controversy, Evidence, Office, Profile } from '@/data/schema';

export const PROFILES_PER_OFFICE = 5;

function byPollRank(a: Profile, b: Profile): number {
  if (a.pollRank === null && b.pollRank === null) return 0;
  if (a.pollRank === null) return 1;
  if (b.pollRank === null) return -1;
  return a.pollRank - b.pollRank;
}

export function profilesFor(
  profiles: Profile[],
  office: Office,
  candidates: Map<string, Candidate>,
  listId?: string,
): Profile[] {
  return profiles
    .filter((p) => {
      const c = candidates.get(p.candidateId);
      if (!c || c.withdrawn || p.office !== office) return false;
      return listId === undefined || c.list === listId;
    })
    .sort(byPollRank)
    .slice(0, PROFILES_PER_OFFICE);
}

export function defendsEvidence(profile: Profile, evidence: Evidence[]): Evidence[] {
  const ids = new Set(profile.defends);
  return evidence.filter((e) => ids.has(e.id));
}

export type ProfileSection = 'presents' | 'experience' | 'proposals' | 'defends' | 'controversies';

export const PROFILE_SECTION_LIMIT = 3;

/** The first "presents" claim is the campaign's own line; the tab then shows the rest. */
export function vibeLine(profile: Profile): Claim | null {
  return profile.presents[0] ?? null;
}

export function sectionCounts(profile: Profile, defends: Evidence[], controversies: Controversy[] = []): Record<ProfileSection, number> {
  return {
    presents: Math.max(0, profile.presents.length - 1),
    experience: profile.experience.length,
    proposals: profile.proposals.length,
    defends: defends.length,
    controversies: controversies.length,
  };
}

export function firstFilledSection(counts: Record<ProfileSection, number>): ProfileSection {
  const order: ProfileSection[] = ['proposals', 'defends', 'experience', 'presents'];
  return order.find((s) => counts[s] > 0) ?? 'proposals';
}

export function visibleSlice<T>(items: T[], expanded: boolean, limit = PROFILE_SECTION_LIMIT): { shown: T[]; hidden: number } {
  if (expanded) return { shown: items, hidden: 0 };
  return { shown: items.slice(0, limit), hidden: Math.max(0, items.length - limit) };
}
