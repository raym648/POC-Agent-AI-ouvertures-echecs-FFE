// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/features/board/board.component.ts

import {
  AfterViewInit,
  Component,
  ElementRef,
  OnInit,
  ViewChild,
  effect
} from '@angular/core';

import { Chessground } from 'chessground';
import type { Api } from 'chessground/api';
import type { DrawShape } from 'chessground/draw';
import type { Key } from 'chessground/types';

import { Subject, debounceTime } from 'rxjs';
import { Chess } from 'chess.js';

import { ChessService } from '../../core/services/chess.service';
import { AgentService } from '../../core/services/agent.service';
import { GameStore } from '../../state/game.store';

@Component({
  selector: 'app-board',
  standalone: true,
  templateUrl: './board.component.html',
  styleUrls: ['./board.component.css']
})
export class BoardComponent implements OnInit, AfterViewInit {
  @ViewChild('board', { static: true })
  private boardRef!: ElementRef<HTMLElement>;

  private move$ = new Subject<void>();
  private cg?: Api;

  constructor(
    private chess: ChessService,
    private agent: AgentService,
    private store: GameStore
  ) {
    // Sync FEN -> Chessground
    effect(() => {
      if (!this.cg) return;

      const fen = this.store.fen();
      if (!fen) return;

      this.cg.set({
        fen: fen === 'start' ? undefined : fen
      });
    });

    // Sync best moves -> arrows
    effect(() => {
      if (!this.cg) return;

      const data = this.store.data();

      if (!data?.moves) {
        this.cg.set({
          drawable: {
            autoShapes: []
          }
        });
        return;
      }

      const chess = new Chess(this.store.fen());
      const shapes: DrawShape[] = [];

      data.moves.slice(0, 3).forEach((m: any) => {
        try {
          const move = chess.move(m.san, { strict: false });

          if (move) {
            shapes.push({
              orig: move.from as Key,
              dest: move.to as Key,
              brush: 'green'
            });

            chess.undo();
          }
        } catch {
          // Ignore invalid SAN
        }
      });

      this.cg.set({
        drawable: {
          autoShapes: shapes
        }
      });
    });
  }

  ngAfterViewInit(): void {
    this.cg = Chessground(this.boardRef.nativeElement, {
      fen: 'start',
      orientation: 'white',
      movable: {
        free: false,
        color: 'both',
        events: {
          after: (from: string, to: string) => this.onMove({ from, to })
        }
      },
      highlight: {
        lastMove: true,
        check: true
      },
      drawable: {
        enabled: true,
        visible: true,
        autoShapes: []
      }
    });
  }

  ngOnInit(): void {
    this.move$.pipe(debounceTime(400)).subscribe(() => {
      this.analyze();
    });
  }

  onMove(event: { from: string; to: string }): void {
    const { from, to } = event;

    if (!this.chess.move(from, to)) return;

    const fen = this.chess.getFen();
    this.store.fen.set(fen);
    this.move$.next();
  }

  analyze(): void {
    const fen = this.store.fen();

    this.store.loading.set(true);
    this.store.error.set(null);

    this.agent.analyze(fen).subscribe({
      next: (res) => {
        this.store.data.set(res);
        this.store.loading.set(false);
      },
      error: () => {
        this.store.error.set('Erreur API');
        this.store.loading.set(false);
      }
    });
  }

  reset(): void {
    this.chess.reset();
    this.store.fen.set('start');
    this.store.data.set(null);

    this.cg?.set({
      fen: undefined,
      drawable: {
        autoShapes: []
      }
    });
  }
}
