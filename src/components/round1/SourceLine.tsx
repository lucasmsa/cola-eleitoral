import { COPY } from '@/config/copy';
import type { ResultSource } from '@/data/schema';
import { DataInfo } from '../shell/DataInfo';
import { SourceLink } from '../shell/ui';

export function SourceLine({ source }: { source: ResultSource }) {
  return (
    <DataInfo>
      <p className="text-base text-muted">
        <SourceLink label={COPY.round1.source(source.generated)} url={source.url} />
      </p>
    </DataInfo>
  );
}
