export const RIVE_WASM = '/mascot/rive.wasm';

export interface RiveAsset {
  src: string;
  artboard: string;
  stateMachine: string;
  cover?: boolean;
}

export const PAGE_TURN: RiveAsset = { src: '/rive/pagina.riv', artboard: 'Pagina', stateMachine: 'Turn', cover: true };
export const STAMP: RiveAsset = { src: '/rive/carimbo.riv', artboard: 'Carimbo', stateMachine: 'Stamp' };
export const TRAIL_NODE: RiveAsset = { src: '/rive/trilha.riv', artboard: 'Node', stateMachine: 'Node' };

export const PAGE_TURN_SWAP_MS = 220;
export const PAGE_TURN_END_MS = 450;
export const RECORDED_MS = 1300;
export const RECORDED_REDUCED_MS = 500;
