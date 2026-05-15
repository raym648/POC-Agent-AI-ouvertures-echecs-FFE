// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/features/board/board.component.ts

import {
  AfterViewInit,
  Component,
  ElementRef,
  OnInit,
  ViewChild,
  effect,
} from '@angular/core';

import { CommonModule } from '@angular/common';

import { Chessground } from 'chessground';

import type { Api } from 'chessground/api';
import type { DrawShape } from 'chessground/draw';
import type { Key } from 'chessground/types';

import type { Square } from 'chess.js';

import { Chess } from 'chess.js';

import {
  Subject,
  debounceTime,
  forkJoin,
} from 'rxjs';

import { ChessService } from '../../core/services/chess.service';
import { AgentService } from '../../core/services/agent.service';
import { GameStore } from '../../state/game.store';

import {
  AgentResponse,
  MoveEvaluation,
} from '../../core/models/agent.model';


@Component({
  selector: 'app-board',
  standalone: true,

  imports: [
    CommonModule,
  ],

  templateUrl: './board.component.html',
  styleUrls: ['./board.component.css'],
})
export class BoardComponent
  implements OnInit, AfterViewInit {

  @ViewChild('board', { static: true })
  private boardRef!: ElementRef<HTMLElement>;

  private move$ = new Subject<void>();

  private cg?: Api;


  constructor(
    private chess: ChessService,
    private agent: AgentService,

    // IMPORTANT :
    // le template Angular accède à "store"
    // donc il ne peut pas être private
    public store: GameStore,
  ) {

    // =====================================================
    // SYNC FEN -> CHESSGROUND
    // =====================================================

    effect(() => {

      if (!this.cg) {
        return;
      }

      const fen = this.store.fen();

      this.cg.set({
        fen,

        movable: {
          color: 'both',
          dests: this.buildDests(),
        },
      });
    });


    // =====================================================
    // BEST MOVES -> ARROWS
    // =====================================================

    effect(() => {

      if (!this.cg) {
        return;
      }

      const data = this.store.data();

      if (!data?.moves?.length) {

        this.cg.set({
          drawable: {
            autoShapes: [],
          },
        });

        return;
      }

      const shapes: DrawShape[] = [];

      data.moves
        .slice(0, 3)
        .forEach((m: MoveEvaluation) => {

          if (!m.move || m.move.length < 4) {
            return;
          }

          const from = m.move.slice(0, 2);
          const to = m.move.slice(2, 4);

          shapes.push({
            orig: from as Key,
            dest: to as Key,
            brush: 'green',
          });
        });

      this.cg.set({
        drawable: {
          autoShapes: shapes,
        },
      });
    });
  }


  // =====================================================
  // INIT
  // =====================================================

  ngOnInit(): void {

    this.move$
      .pipe(
        debounceTime(400),
      )
      .subscribe(() => {
        this.analyze();
      });
  }


  // =====================================================
  // CHESSGROUND INIT
  // =====================================================

  ngAfterViewInit(): void {

    this.cg = Chessground(
      this.boardRef.nativeElement,
      {
        fen: this.store.fen(),

        orientation: 'white',

        movable: {
          free: false,

          color: 'both',

          dests: this.buildDests(),

          events: {
            after: (
              from: string,
              to: string,
            ) => this.onMove({ from, to }),
          },
        },

        highlight: {
          lastMove: true,
          check: true,
        },

        drawable: {
          enabled: true,
          visible: true,
          autoShapes: [],
        },
      },
    );
  }


  // =====================================================
  // MOVE HANDLER
  // =====================================================

  onMove(event: {
    from: string;
    to: string;
  }): void {

    const { from, to } = event;

    const success = this.chess.move(from, to);

    if (!success) {
      return;
    }

    const fen = this.chess.getFen();

    this.store.fen.set(fen);

    this.move$.next();
  }


  // =====================================================
  // ANALYSIS
  // =====================================================

  analyze(): void {

    const fen = this.store.fen();

    this.store.loading.set(true);

    this.store.error.set(null);

    forkJoin({

      moves: this.agent.getMoves(fen),

      evaluation: this.agent.getEvaluation(fen),

    }).subscribe({

      next: ({
        moves,
        evaluation,
      }) => {

        const response: AgentResponse = {

          fen,

          source:
            moves.source ??
            evaluation.source,

          moves:
            moves.moves ?? [],

          evaluation:
            evaluation.evaluation ?? null,

          opening:
            moves.opening ?? null,

          videos:
            moves.videos ?? [],

          rag_context:
            moves.rag_context ?? [],

          explanation:
            moves.explanation ?? null,

          error: null,
        };

        this.store.data.set(response);

        this.store.loading.set(false);
      },

      error: () => {

        this.store.error.set(
          'Erreur API',
        );

        this.store.loading.set(false);
      },
    });
  }


  // =====================================================
  // RESET
  // =====================================================

  reset(): void {

    this.chess.reset();

    const fen = this.chess.getFen();

    this.store.fen.set(fen);

    this.store.data.set(null);

    this.cg?.set({

      fen,

      movable: {
        color: 'both',
        dests: this.buildDests(),
      },

      drawable: {
        autoShapes: [],
      },
    });
  }


  // =====================================================
  // LEGAL MOVES
  // =====================================================

  private buildDests(): Map<Key, Key[]> {

    const chess = new Chess(
      this.store.fen(),
    );

    const dests =
      new Map<Key, Key[]>();

    const files = [
      'a', 'b', 'c', 'd',
      'e', 'f', 'g', 'h',
    ] as const;

    const ranks = [
      '1', '2', '3', '4',
      '5', '6', '7', '8',
    ] as const;

    for (const file of files) {

      for (const rank of ranks) {

        const square =
          `${file}${rank}` as Square;

        const moves = chess.moves({
          square,
          verbose: true,
        });

        if (!moves.length) {
          continue;
        }

        dests.set(
          square as Key,

          moves.map(
            move => move.to as Key,
          ),
        );
      }
    }

    return dests;
  }

}
