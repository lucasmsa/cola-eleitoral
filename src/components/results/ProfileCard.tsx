import { motion } from 'motion/react';
import { COPY } from '@/config/copy';
import type { Candidate, Controversy, Evidence, Profile } from '@/data/schema';
import { useProfileCard } from '@/hooks/useProfileCard';
import type { ProfileSection } from '@/lib/profiles';
import { POSITION_LABEL, positionTone } from '@/lib/positions';
import { evidenceBadge } from '@/lib/subjects';
import { titleCase } from '@/lib/text';
import { Portrait } from '../shell/Portrait';
import { Tag, ToneChip } from '../shell/ui';
import { ControversyList } from './ControversyList';
import { Fonte } from './Fonte';

interface Props {
  profile: Profile;
  candidate: Candidate | null;
  defends: Evidence[];
  statementOf: (questionId: string) => string;
  listName: string;
  controversies: Controversy[];
  portrait: string | null;
}

export const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  shown: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 220, damping: 26 } },
};

const SECTIONS: { id: ProfileSection; label: string }[] = [
  { id: 'presents', label: COPY.profile.presents },
  { id: 'experience', label: COPY.profile.experience },
  { id: 'proposals', label: COPY.profile.proposalsShort },
  { id: 'defends', label: COPY.profile.defendsShort },
  { id: 'controversies', label: COPY.profile.controversies },
];

export function ProfileCard({ profile, candidate, defends, statementOf, listName, controversies, portrait }: Props) {
  const c = useProfileCard(profile, defends, controversies);
  const name = candidate ? titleCase(candidate.ballotName) : profile.candidateId;
  const panelId = `panel-${profile.candidateId}`;
  return (
    <motion.article
      variants={cardVariants}
      className="grid w-[86vw] max-w-[34rem] shrink-0 snap-start content-start gap-4 rounded-md border-2 border-edge bg-paper p-5 shadow-[0_4px_0_#9aa6c2] lg:w-auto lg:max-w-none"
    >
      <header className="grid gap-2">
        <div className="flex items-start gap-4">
          <Portrait name={name} file={portrait} size="card" taped />
          <div className="grid min-w-0 gap-1 pt-1">
            {profile.pollRank !== null && <span className="font-hand text-2xl leading-none text-pen">{COPY.profile.rank(profile.pollRank)}</span>}
            <h3 className="text-[1.75rem] font-extrabold leading-tight">{name}</h3>
            {candidate && <span className="tabular text-2xl font-bold text-muted">{candidate.number}</span>}
            <p className="text-base text-muted">{listName}</p>
            {candidate?.notice && <Tag strong>{COPY.profile.notice}</Tag>}
          </div>
        </div>
        {c.vibe && (
          <p className="font-hand text-[1.6rem] leading-snug text-ink">
            {c.vibe.text}
            <Fonte url={c.vibe.source.url} label={c.vibe.source.label} />
          </p>
        )}
      </header>

      <div className="flex flex-wrap gap-1.5 md:gap-2" role="tablist" aria-label={COPY.profile.sectionsLabel(name)}>
        {SECTIONS.map((s) => {
          const on = c.section === s.id;
          return (
            <button
              key={s.id}
              type="button"
              role="tab"
              aria-selected={on}
              aria-controls={panelId}
              disabled={c.counts[s.id] === 0 && s.id !== 'controversies'}
              onClick={() => c.choose(s.id)}
              className={`inline-flex min-h-11 items-center rounded-full border-2 px-3 text-base font-semibold disabled:opacity-40 ${on ? 'border-ink bg-ink text-paper' : 'border-edge bg-paper text-ink hover:bg-fact'}`}
            >
              {s.label} <span className="tabular">({c.counts[s.id]})</span>
            </button>
          );
        })}
      </div>

      <div id={panelId} role="tabpanel" className="grid gap-3">
        <ul className="grid gap-3">
          {c.claims.map((cl) => (
            <li key={cl.checkId} className="border-l-2 border-line pl-3 text-lg leading-snug">
              {cl.text}
              <Fonte url={cl.source.url} label={cl.source.label} />
            </li>
          ))}
          {c.evidence.map((e) => {
            const tone = positionTone(e.position);
            return (
              <li key={e.id} className="grid gap-1 border-l-2 border-line pl-3">
                <p className="text-lg font-semibold leading-snug">{statementOf(e.questionId)}</p>
                <p className="flex flex-wrap items-center gap-2">
                  <ToneChip tone={tone}>{POSITION_LABEL[tone]}</ToneChip>
                  <Tag strong={e.kind === 'record'}>{evidenceBadge(e)}</Tag>
                </p>
                <p className="text-base text-muted">
                  {e.detail}
                  <Fonte url={e.source.url} label={e.source.label} />
                </p>
              </li>
            );
          })}
        </ul>
        {c.section === 'controversies' && <ControversyList items={c.controversies} />}
        {c.hidden > 0 && (
          <button type="button" onClick={c.expand} className="inline-flex min-h-11 items-center justify-self-start text-base font-bold text-ink underline decoration-pen underline-offset-4">
            {COPY.profile.more(c.hidden)}
          </button>
        )}
      </div>
    </motion.article>
  );
}
