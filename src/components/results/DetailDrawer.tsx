import { COPY } from '@/config/copy';
import type { Office } from '@/data/schema';
import { useSubjectDetail } from '@/hooks/useSubjectDetail';
import { EvidenceLine } from '../lesson/EvidenceItem';
import { ImportanceChips } from '../lesson/ImportanceChips';
import { Button, SourceLink, ToneChip } from '../shell/ui';

interface Props {
  subject: { type: 'candidate' | 'list'; id: string };
  office: Office;
  onClose: () => void;
}

export function DetailDrawer({ subject, office, onClose }: Props) {
  const d = useSubjectDetail(subject, office);
  return (
    <div className="fixed inset-0 z-30 flex justify-end bg-ink/40" role="dialog" aria-modal="true" aria-labelledby="detail-title">
      <div className="h-full w-full max-w-2xl overflow-y-auto bg-paper p-5 shadow-2xl">
        <div className="flex items-start justify-between gap-4">
          <div className="grid gap-1">
            <p className="text-base font-bold uppercase tracking-wider text-muted">{d.officeLabel}</p>
            <h2 id="detail-title" className="text-4xl font-extrabold">
              {d.info.name} {d.info.number && <span className="tabular text-muted">{d.info.number}</span>}
            </h2>
            {d.info.type === 'candidate' && <p className="text-lg text-muted">{d.info.listName}</p>}
          </div>
          <Button onClick={onClose}>{COPY.detail.close}</Button>
        </div>

        <dl className="mt-4 grid gap-2 text-lg">
          {d.runningMates.length > 0 && (
            <div>
              <dt className="inline font-semibold">{COPY.detail.mates}: </dt>
              <dd className="inline">{d.runningMates.join(', ')}</dd>
            </div>
          )}
          {d.status && (
            <div>
              <dt className="inline font-semibold">{COPY.detail.status}: </dt>
              <dd className="inline">{d.status.toLowerCase()}</dd>
            </div>
          )}
          {d.elected.length > 0 && (
            <div>
              <dt className="font-semibold">{COPY.detail.elected}</dt>
              <dd>
                <ul className="list-inside list-disc">
                  {d.elected.map((e) => (
                    <li key={`${e.year}-${e.office}`}>
                      {e.year}: {e.office} ({e.place}), pelo {e.party}
                    </li>
                  ))}
                </ul>
              </dd>
            </div>
          )}
          {d.planUrl && (
            <div>
              <SourceLink label={COPY.detail.plan} url={d.planUrl} />
            </div>
          )}
        </dl>

        <ol className="mt-6 grid gap-5">
          {d.rows.length === 0 && <p className="text-lg text-muted">{COPY.detail.noRows}</p>}
          {d.rows.map((row) => (
            <li key={row.questionId} className="grid gap-3 border-t-2 border-rule pt-4">
              <h3 className="text-2xl font-bold">{row.statement}</h3>
              <div className="grid gap-1 text-lg">
                <p>
                  <span className="text-muted">{COPY.detail.you}: </span>
                  <strong>{row.yourAnswer}</strong>
                </p>
                <p className="flex flex-wrap items-center gap-2">
                  <span className="text-muted">{COPY.detail.them}: </span>
                  {row.theirTone ? <ToneChip tone={row.theirTone}>{row.theirLabel}</ToneChip> : <span>{row.theirLabel}</span>}
                </p>
              </div>
              {row.importance !== null && (
                <ImportanceChips
                  compact
                  label={COPY.detail.weight}
                  options={d.importances}
                  selected={row.importance}
                  onSelect={(v) => d.setImportance(row.questionId, v)}
                />
              )}
              {row.evidence.length > 0 && (
                <ul className="grid gap-3">
                  {row.evidence.map(({ item }) => (
                    <EvidenceLine key={item.id} evidence={item} />
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
