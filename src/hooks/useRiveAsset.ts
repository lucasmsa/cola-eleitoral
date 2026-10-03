import { Fit, Layout, Rive, RuntimeLoader } from '@rive-app/canvas';
import { useCallback, useEffect, useRef, useState } from 'react';
import { RIVE_WASM, type RiveAsset } from '@/config/rive';

export type RiveStatus = 'loading' | 'ready' | 'missing';

let wasmConfigured = false;
const availability = new Map<string, Promise<boolean>>();

function riveFileExists(src: string): Promise<boolean> {
  const cached = availability.get(src);
  if (cached) return cached;
  // Vite answers unknown paths with index.html, so a 200 alone does not prove the file exists.
  const probe = fetch(src, { method: 'HEAD' })
    .then((r) => r.ok && !(r.headers.get('content-type') ?? '').includes('text/html'))
    .catch(() => false);
  availability.set(src, probe);
  return probe;
}

export function prefersReducedMotion(): boolean {
  return typeof window !== 'undefined' && typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export interface RiveControls {
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  status: RiveStatus;
  fire: (name: string) => void;
  setNumber: (name: string, value: number) => void;
  setBoolean: (name: string, value: boolean) => void;
}

export function useRiveAsset(asset: RiveAsset, enabled = true): RiveControls {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const riveRef = useRef<Rive | null>(null);
  const smRef = useRef<string | null>(null);
  const [status, setStatus] = useState<RiveStatus>(import.meta.env.MODE === 'test' ? 'missing' : 'loading');

  useEffect(() => {
    if (!enabled || import.meta.env.MODE === 'test') return;
    let cancelled = false;
    let rive: Rive | null = null;
    void riveFileExists(asset.src).then((exists) => {
      const canvas = canvasRef.current;
      if (cancelled) return;
      if (!exists || !canvas) {
        setStatus('missing');
        return;
      }
      if (!wasmConfigured) {
        RuntimeLoader.setWasmUrl(RIVE_WASM);
        wasmConfigured = true;
      }
      rive = new Rive({
        src: asset.src,
        canvas,
        artboard: asset.artboard,
        stateMachine: asset.stateMachine,
        autoplay: true,
        autoBind: true,
        layout: new Layout({ fit: asset.cover ? Fit.Cover : Fit.Contain }),
        onLoad: () => {
          if (!rive || cancelled) return;
          rive.resizeDrawingSurfaceToCanvas();
          smRef.current = asset.stateMachine;
          const reduce = rive.viewModelInstance?.boolean('reduceMotion');
          if (reduce) reduce.value = prefersReducedMotion();
          setStatus('ready');
        },
        onLoadError: () => !cancelled && setStatus('missing'),
      });
      riveRef.current = rive;
    });
    return () => {
      cancelled = true;
      rive?.cleanup();
      riveRef.current = null;
    };
  }, [asset.src, asset.artboard, asset.stateMachine, asset.cover, enabled]);

  const input = useCallback((name: string) => {
    const rive = riveRef.current;
    const sm = smRef.current;
    if (!rive || !sm) return undefined;
    return rive.stateMachineInputs(sm)?.find((i) => i.name === name);
  }, []);

  const fire = useCallback(
    (name: string) => {
      const vmTrigger = riveRef.current?.viewModelInstance?.trigger(name);
      if (vmTrigger) {
        vmTrigger.trigger();
        return;
      }
      input(name)?.fire();
    },
    [input],
  );

  const setNumber = useCallback(
    (name: string, value: number) => {
      const vm = riveRef.current?.viewModelInstance?.number(name);
      if (vm) {
        vm.value = value;
        return;
      }
      const i = input(name);
      if (i) i.value = value;
    },
    [input],
  );

  const setBoolean = useCallback(
    (name: string, value: boolean) => {
      const vm = riveRef.current?.viewModelInstance?.boolean(name);
      if (vm) {
        vm.value = value;
        return;
      }
      const i = input(name);
      if (i) i.value = value;
    },
    [input],
  );

  return { canvasRef, status, fire, setNumber, setBoolean };
}
