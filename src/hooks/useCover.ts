import { useCallback, useEffect, useRef, useState } from 'react';
import { COVER } from '@/config/cover';
import { prefersReducedMotion } from './useRiveAsset';

async function exists(src: string): Promise<boolean> {
  try {
    const r = await fetch(src, { method: 'HEAD' });
    return r.ok && !(r.headers.get('content-type') ?? '').includes('text/html');
  } catch {
    return false;
  }
}

export interface CoverState {
  poster: string | null;
  video: string | null;
  ended: boolean;
  attachVideo: (el: HTMLVideoElement | null) => void;
  onEnded: () => void;
  replay: () => void;
}

/** Shows the cover only once its files exist; plays the film once and holds its last frame. Reduced motion gets the poster. */
export function useCover(): CoverState {
  const [files, setFiles] = useState<{ poster: string | null; video: string | null }>({ poster: null, video: null });
  const [ended, setEnded] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    if (import.meta.env.MODE === 'test') return;
    let cancelled = false;
    void Promise.all([exists(COVER.poster), exists(COVER.video)]).then(([hasPoster, hasVideo]) => {
      if (cancelled) return;
      setFiles({
        poster: hasPoster ? COVER.poster : null,
        video: hasVideo && !prefersReducedMotion() ? COVER.video : null,
      });
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const attachVideo = useCallback((el: HTMLVideoElement | null) => {
    videoRef.current = el;
  }, []);
  const onEnded = useCallback(() => setEnded(true), []);
  const replay = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    video.currentTime = 0;
    setEnded(false);
    void video.play().catch(() => setEnded(true));
  }, []);

  return { ...files, ended, attachVideo, onEnded, replay };
}
