import { motion } from 'motion/react';
import { COPY } from '@/config/copy';
import type { Candidate, Controversy, Evidence, Profile } from '@/data/schema';
import { ProfileCard } from './ProfileCard';

interface Item {
  profile: Profile;
  candidate: Candidate | null;
  defends: Evidence[];
  controversies: Controversy[];
  portrait: string | null;
}

interface Props {
  title: string;
  items: Item[];
  statementOf: (questionId: string) => string;
  listNameOf: (candidate: Candidate | null) => string;
}

export function ProfileCards({ title, items, statementOf, listNameOf }: Props) {
  return (
    <section aria-label={title} className="grid min-w-0 gap-4">
      <h2 className="text-3xl font-bold">{title}</h2>
      {items.length === 0 ? (
        <p className="text-lg text-muted">{COPY.profile.none}</p>
      ) : (
        <>
          <p className="max-w-[70ch] text-lg text-muted">
            {items.some((i) => i.profile.pollRank !== null)
              ? COPY.profile.explain
              : COPY.profile.explainUnranked}
          </p>
          <motion.div
            initial="hidden"
            animate="shown"
            transition={{ staggerChildren: 0.08 }}
            className="-mx-4 flex snap-x snap-mandatory items-start gap-4 overflow-x-auto px-4 pb-3 lg:mx-0 lg:grid lg:grid-cols-2 lg:overflow-visible lg:px-0"
          >
            {items.map((i) => (
              <ProfileCard
                key={i.profile.candidateId}
                profile={i.profile}
                candidate={i.candidate}
                defends={i.defends}
                controversies={i.controversies}
                portrait={i.portrait}
                statementOf={statementOf}
                listName={listNameOf(i.candidate)}
              />
            ))}
          </motion.div>
        </>
      )}
    </section>
  );
}
