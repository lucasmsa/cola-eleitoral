import { AnimatePresence, MotionConfig, motion } from 'motion/react';
import { useCountdown } from '@/hooks/useCountdown';
import { useNav } from '@/hooks/useNav';
import { screenKey, usePageTurn } from '@/hooks/usePageTurn';
import type { Screen } from '@/stores/screen';
import { ColaScreen } from './cola/ColaScreen';
import { HomeScreen } from './home/HomeScreen';
import { LessonScreen } from './lesson/LessonScreen';
import { ResultScreen } from './results/ResultScreen';
import { ReviewScreen } from './review/ReviewScreen';
import { Round2Screen } from './round2/Round2Screen';
import { Round2ColaScreen } from './round2/Round2ColaScreen';
import { Round1Screen } from './round1/Round1Screen';
import { useTurno } from '@/hooks/useTurno';
import { TopBar } from './shell/TopBar';
import { Credits } from './shell/Credits';

function ScreenView({ screen }: { screen: Screen }) {
  switch (screen.name) {
    case 'lesson':
      return <LessonScreen key={screen.unitId} unitId={screen.unitId} />;
    case 'results':
      return <ResultScreen />;
    case 'review':
      return <ReviewScreen />;
    case 'cola':
      return <ColaScreen />;
    case 'round2':
      return <Round2Screen />;
    case 'round1':
      return <Round1Screen />;
    case 'cola2':
      return <Round2ColaScreen />;
    default:
      return <HomeScreen />;
  }
}

export function App() {
  const nav = useNav();
  const countdown = useCountdown();
  const turno = useTurno();
  const { canvasRef, displayed: shown, turning, ready } = usePageTurn(nav.screen);
  const topKey = shown.name === 'results' ? 'results' : screenKey(shown);
  return (
    <MotionConfig reducedMotion="user">
      <TopBar
        countdown={turno.turno === 2 ? countdown.short : ''}
        screen={shown.name === 'lesson' ? 'home' : shown.name}
        turno={turno.turno}
        links={turno.links}
        onTurno={turno.choose}
        actions={{
          onHome: nav.goHome,
          onResults: nav.goResults,
          onReview: nav.goReview,
          onCola: nav.goCola,
          onRound2: nav.goRound2,
          onRound1: nav.goRound1,
          onCola2: nav.goCola2,
        }}
      />
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={topKey}
          initial={ready ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          exit={ready ? { opacity: 1 } : { opacity: 0, y: -8, transition: { duration: 0.12 } }}
          transition={{ type: 'spring', stiffness: 260, damping: 30 }}
        >
          <ScreenView screen={shown} />
        </motion.div>
      </AnimatePresence>
      <Credits />
      <canvas
        ref={canvasRef}
        width={800}
        height={1600}
        aria-hidden="true"
        className={`screen-only pointer-events-none fixed inset-0 z-40 size-full ${ready && turning ? 'visible' : 'invisible'}`}
      />
    </MotionConfig>
  );
}
