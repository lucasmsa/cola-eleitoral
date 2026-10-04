import { motion } from 'motion/react';
import { COPY } from '@/config/copy';
import type { CoverState } from '@/hooks/useCover';
import { ReturnMark } from '../shell/icons';

export function Cover({ cover }: { cover: CoverState }) {
  const { poster, video, ended, attachVideo, onEnded, replay } = cover;
  if (!poster && !video) return null;
  return (
    <motion.figure
      initial={{ opacity: 0, y: 12, rotate: -0.6 }}
      animate={{ opacity: 1, y: 0, rotate: -0.6 }}
      transition={{ type: 'spring', stiffness: 160, damping: 22 }}
      className="relative overflow-hidden rounded-md border-2 border-edge bg-paper shadow-[0_6px_0_#9aa6c2]"
    >
      {video ? (
        <video
          ref={attachVideo}
          className="block aspect-[16/9] w-full object-cover"
          src={video}
          poster={poster ?? undefined}
          autoPlay
          muted
          playsInline
          onEnded={onEnded}
          aria-hidden="true"
        />
      ) : (
        <img className="block aspect-[16/9] w-full object-cover" src={poster ?? ''} alt="" />
      )}
      {video && ended && (
        <button
          type="button"
          onClick={replay}
          aria-label={COPY.home.replayCover}
          title={COPY.home.replayCover}
          className="absolute bottom-3 right-3 inline-flex size-11 items-center justify-center rounded-full border-2 border-ink bg-paper/95 text-xl font-bold text-ink shadow-[0_2px_0_#9aa6c2] hover:bg-fact"
        >
          <ReturnMark className="size-6" />
        </button>
      )}
    </motion.figure>
  );
}
