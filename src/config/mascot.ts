export const MASCOT = {
  src: '/mascot/calango.riv',
  artboard: 'Calango',
  stateMachine: 'Mascot',
} as const;

export const MOOD = { idle: 0, happy: 1, think: 2, reading: 3, cheer: 4 } as const;
export type Mood = keyof typeof MOOD;
