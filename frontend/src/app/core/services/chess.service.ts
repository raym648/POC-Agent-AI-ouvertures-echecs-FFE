// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/core/services/chess.service.ts

import { Injectable } from '@angular/core';

import {
  Chess,
  Move,
  Square,
} from 'chess.js';


@Injectable({
  providedIn: 'root',
})
export class ChessService {

  // =====================================================
  // SINGLE SOURCE OF TRUTH
  // =====================================================

  private chess =
    new Chess();


  // =====================================================
  // CURRENT FEN
  // =====================================================

  getFen(): string {

    return this.chess.fen();
  }


  // =====================================================
  // LOAD POSITION
  // =====================================================

  loadFen(
    fen: string
  ): boolean {

    try {

      this.chess.load(fen);

      return true;

    } catch (error) {

      console.error(
        'Invalid FEN:',
        error,
      );

      return false;
    }
  }


  // =====================================================
  // PLAY MOVE
  // =====================================================

  move(
    from: string,
    to: string,
    promotion: 'q' | 'r' | 'b' | 'n' = 'q',
  ): boolean {

    try {

      const result =
        this.chess.move({
          from,
          to,
          promotion,
        });

      return !!result;

    } catch (error) {

      console.error(
        'Illegal move:',
        {
          from,
          to,
          error,
        },
      );

      return false;
    }
  }


  // =====================================================
  // LEGAL MOVES
  // =====================================================

  getLegalMoves(
    square?: string,
  ): Move[] {

    try {

      if (square) {

        return this.chess.moves({

          square:
            square as Square,

          verbose: true,

        }) as Move[];
      }

      return this.chess.moves({

        verbose: true,

      }) as Move[];

    } catch (error) {

      console.error(
        'Legal moves error:',
        error,
      );

      return [];
    }
  }


  // =====================================================
  // TURN
  // =====================================================

  turn():
    'w' | 'b' {

    return this.chess.turn();
  }


  // =====================================================
  // GAME STATUS
  // =====================================================

  isCheckmate(): boolean {

    return this.chess.isCheckmate();
  }

  isDraw(): boolean {

    return this.chess.isDraw();
  }

  isGameOver(): boolean {

    return this.chess.isGameOver();
  }

  inCheck(): boolean {

    return this.chess.inCheck();
  }


  // =====================================================
  // HISTORY
  // =====================================================

  history(): string[] {

    return this.chess.history();
  }

  verboseHistory(): Move[] {

    return this.chess.history({
      verbose: true,
    }) as Move[];
  }


  // =====================================================
  // POSITION HELPERS
  // =====================================================

  ascii(): string {

    return this.chess.ascii();
  }

  pgn(): string {

    return this.chess.pgn();
  }


  // =====================================================
  // VALIDATION
  // =====================================================

  validateFen(
    fen: string
  ): boolean {

    try {

      const test =
        new Chess();

      test.load(fen);

      return true;

    } catch {

      return false;
    }
  }


  // =====================================================
  // RESET
  // =====================================================

  reset(): void {

    this.chess.reset();
  }


  // =====================================================
  // HARD RESET
  // =====================================================

  recreate(): void {

    this.chess =
      new Chess();
  }

}
