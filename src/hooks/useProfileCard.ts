import { useState } from 'react';
import type { Controversy, Evidence, Profile } from '@/data/schema';
import { firstFilledSection, sectionCounts, vibeLine, visibleSlice, type ProfileSection } from '@/lib/profiles';

export function useProfileCard(profile: Profile, defends: Evidence[], controversies: Controversy[]) {
  const counts = sectionCounts(profile, defends, controversies);
  const [section, setSection] = useState<ProfileSection>(() => firstFilledSection(counts));
  const [expanded, setExpanded] = useState(false);
  const lists = {
    presents: profile.presents.slice(1),
    experience: profile.experience,
    proposals: profile.proposals,
  };
  const claims = section === 'defends' || section === 'controversies' ? { shown: [], hidden: 0 } : visibleSlice(lists[section], expanded);
  const evidence = section === 'defends' ? visibleSlice(defends, expanded) : { shown: [], hidden: 0 };
  return {
    vibe: vibeLine(profile),
    counts,
    section,
    choose: (s: ProfileSection) => {
      setSection(s);
      setExpanded(false);
    },
    claims: claims.shown,
    evidence: evidence.shown,
    controversies,
    hidden: claims.hidden + evidence.hidden,
    expand: () => setExpanded(true),
  };
}
