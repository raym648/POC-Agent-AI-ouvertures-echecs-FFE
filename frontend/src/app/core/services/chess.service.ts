// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/core/services/chess.service.ts

import { Injectable } from '@angular/core';

import { Chess, Move } from 'chess.js';


@Injectable({
  providedIn: 'root',
})
export class ChessService {

  private readonly chess = new Chess();


  // =====================================================
  // CURRENT FEN
  // =====================================================

  getFen(): string {
    return this.chess.fen();
  }


  // =====================================================
  // LOAD POSITION
  // =====================================================

  loadFen(fen: string): boolean {

    try {

      this.chess.load(fen);

      return true;

    } catch {

      return false;
    }
  }


  // =====================================================
  // PLAY MOVE
  // =====================================================

  move(from: string, to: string): boolean {

    try {

      const result = this.chess.move({
        from,
        to,
      });

      return !!result;

    } catch {

      return false;
    }
  }


  // =====================================================
  // LEGAL MOVES
  // =====================================================

  getLegalMoves(square?: string): Move[] {

    return this.chess.moves({
      square: square as any,
      verbose: true,
    }) as Move[];
  }


  // =====================================================
  // GAME STATE
  // =====================================================

  isCheckmate(): boolean {
    return this.chess.isCheckmate();
  }

  isDraw(): boolean {
    return this.chess.isDraw();
  }

  turn(): 'w' | 'b' {
    return this.chess.turn();
  }


  // =====================================================
  // HISTORY
  // =====================================================

  history(): string[] {
    return this.chess.history();
  }


  // =====================================================
  // RESET
  // =====================================================

  reset(): void {
    this.chess.reset();
  }

}
