// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/core/services/chess.service.ts,

import { Injectable } from '@angular/core';
import { Chess } from 'chess.js';

@Injectable({ providedIn: 'root' })
export class ChessService {

  private chess = new Chess();

  getFen(): string {
    return this.chess.fen();
  }

  move(from: string, to: string): boolean {
    const result = this.chess.move({ from, to });
    return !!result;
  }

  reset(): void {
    this.chess.reset();
  }
}
