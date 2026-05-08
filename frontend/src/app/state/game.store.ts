// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/state/game.store.ts

import { Injectable, signal } from '@angular/core';

import { AgentResponse } from '../core/models/agent.model';


@Injectable({
  providedIn: 'root',
})
export class GameStore {

  // =====================================================
  // DEFAULT FEN
  // =====================================================

  // Position initiale standard
  readonly fen = signal<string>(
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
  );


  // =====================================================
  // AGENT DATA
  // =====================================================

  readonly data = signal<AgentResponse | null>(null);

  readonly loading = signal<boolean>(false);

  readonly error = signal<string | null>(null);


  // =====================================================
  // STATE HELPERS
  // =====================================================

  setFen(fen: string): void {
    this.fen.set(fen);
  }

  setLoading(value: boolean): void {
    this.loading.set(value);
  }

  setError(message: string | null): void {
    this.error.set(message);
  }

  clearError(): void {
    this.error.set(null);
  }

  clearData(): void {
    this.data.set(null);
  }


  // =====================================================
  // MERGE PARTIAL RESPONSES
  // =====================================================

  updateData(partial: Partial<AgentResponse>): void {

    const current = this.data();

    this.data.set({
      ...(current ?? {}),
      ...partial,
    } as AgentResponse);
  }


  // =====================================================
  // RESET STORE
  // =====================================================

  reset(): void {

    this.data.set(null);

    this.loading.set(false);

    this.error.set(null);
  }

}
