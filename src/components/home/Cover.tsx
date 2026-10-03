import { motion } from 'motion/react';
import { COPY } from '@/config/copy';
import type { CoverState } from '@/hooks/useCover';

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
          className="absolute bottom-3 right-3 min-h-11 rounded-md border-2 border-ink bg-paper/95 px-3 font-hand text-lg font-bold text-ink hover:bg-fact"
        >
          {COPY.home.replayCover}
        </button>
      )}
    </motion.figure>
  );
}
