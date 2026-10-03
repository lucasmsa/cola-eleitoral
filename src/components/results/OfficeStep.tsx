import { COPY } from '@/config/copy';
import type { Office } from '@/data/schema';
import { useResults } from '@/hooks/useResults';
import { Disclosure } from '../shell/Disclosure';
import { Button } from '../shell/ui';
import { DetailDrawer } from './DetailDrawer';
import { LegendaPicker } from './LegendaPicker';
import { PollPanel } from './PollPanel';
import { ProfileCards } from './ProfileCards';
import { RankingList } from './RankingList';
import { WeightControl } from './WeightControl';

export function OfficeStep({ office }: { office: Office }) {
  const r = useResults(office);
  const rowProps = {
    colaSlotOf: r.colaSlotOf,
    slotsFull: r.slotsFull,
    onPut: r.putInCola,
    onRemove: r.removeFromCola,
    onDetails: r.openDetail,
  };
  return (
    <div className="grid min-w-0 grid-cols-[minmax(0,1fr)] gap-6">
      <Disclosure summary={COPY.results.howToRead}>
        <p className="max-w-[70ch] text-lg text-muted">{COPY.results.explain}</p>
      </Disclosure>
      {r.answeredTotal === 0 && <p className="rounded-md border-2 border-pen bg-pen-soft p-4 text-xl">{COPY.results.noAnswers}</p>}
      <WeightControl weights={r.weights} onChange={r.setRecordWeight} />

      {r.lists && r.listId === null && (
        <section className="grid gap-3" aria-labelledby={`lists-${office}`}>
          <h2 id={`lists-${office}`} className="text-3xl font-bold">
            {COPY.results.listsTitle}
          </h2>
          <p className="max-w-[70ch] text-lg text-muted">{COPY.results.listsExplain}</p>
          {r.colaLegenda && <p className="text-lg">Na cola: legenda {r.colaLegenda}.</p>}
          <RankingList rows={r.lists} {...rowProps} onOpenList={r.selectList} />
        </section>
      )}

      {r.people && (
        <section className="grid gap-3" aria-labelledby={`people-${office}`}>
          <div className="flex flex-wrap items-center gap-3">
            <h2 id={`people-${office}`} className="text-3xl font-bold">
              {r.listName ? COPY.results.peopleIn(r.listName) : COPY.results.ranking}
            </h2>
            {r.listName && (
              <Button variant="quiet" onClick={() => r.selectList(null)}>
                {COPY.results.backToLists}
              </Button>
            )}
          </div>
          <RankingList rows={r.people} {...rowProps} />
        </section>
      )}

      {(!r.lists || r.listId !== null) && (
        <ProfileCards
          title={r.listName ? COPY.profile.titleList(r.listName) : COPY.profile.title}
          items={r.profiles}
          statementOf={r.statementOf}
          listNameOf={r.listNameOf}
        />
      )}

      <PollPanel polls={r.polls} />

      {r.detail && <DetailDrawer subject={r.detail} office={office} onClose={r.closeDetail} />}
      {r.legendaFor && (
        <LegendaPicker listName={r.legendaFor} parties={r.legendaParties} onPick={r.pickLegenda} onCancel={r.cancelLegenda} />
      )}
    </div>
  );
}
