// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/state/game.store.ts

import { Injectable, signal } from '@angular/core';
import { AgentResponse } from '../core/models/agent.model';

@Injectable({ providedIn: 'root' })
export class GameStore {

  fen = signal<string>('start');

  data = signal<AgentResponse | null>(null);

  loading = signal<boolean>(false);

  error = signal<string | null>(null);
}
