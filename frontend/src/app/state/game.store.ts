// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/state/game.store.ts

import { Injectable, signal } from '@angular/core';
import { AgentResponse } from '../core/models/agent.model';

@Injectable({ providedIn: 'root' })
export class GameStore {
  // FEN initial standard (équivalent à new Chess().fen())
  fen = signal<string>('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1');

  data = signal<AgentResponse | null>(null);

  loading = signal<boolean>(false);

  error = signal<string | null>(null);
}
