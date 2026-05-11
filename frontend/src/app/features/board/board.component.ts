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
  of,
  switchMap,
  catchError,
} from 'rxjs';

import { ChessService } from '../../core/services/chess.service';
import { AgentService } from '../../core/services/agent.service';
import { GameStore } from '../../state/game.store';

import {
  AgentResponse,
  MoveEvaluation,
  RagItem,
  Video,
} from '../../core/models/agent.model';


@Component({
  selector: 'app-board',
  standalone: true,

  imports: [
    CommonModule,
  ],

  templateUrl: './board.component.html',

  styleUrls: [
    './board.component.css',
  ],
})
export class BoardComponent
  implements OnInit, AfterViewInit {

  // =====================================================
  // VIEW
  // =====================================================

  @ViewChild('board', { static: true })
  private boardRef!: ElementRef<HTMLElement>;

  // =====================================================
  // RXJS
  // =====================================================

  private move$ = new Subject<void>();

  // =====================================================
  // CHESSGROUND
  // =====================================================

  private cg?: Api;


  constructor(
    private chess: ChessService,

    private agent: AgentService,

    public store: GameStore,
  ) {

    // ===================================================
    // SYNC FEN -> CHESSGROUND
    // ===================================================

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

    // ===================================================
    // BEST MOVES -> ARROWS
    // ===================================================

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
        .forEach((move: MoveEvaluation) => {

          if (
            !move.move ||
            move.move.length < 4
          ) {
            return;
          }

          const from =
            move.move.slice(0, 2);

          const to =
            move.move.slice(2, 4);

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
            ) => this.onMove({
              from,
              to,
            }),
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

    const {
      from,
      to,
    } = event;

    const success =
      this.chess.move(from, to);

    if (!success) {
      return;
    }

    const fen =
      this.chess.getFen();

    this.store.setFen(fen);

    this.move$.next();
  }


  // =====================================================
  // ANALYSIS
  // =====================================================

  analyze(): void {

    const fen =
      this.store.fen();

    this.store.setLoading(true);

    this.store.clearError();

    // ===================================================
    // INITIAL WORKFLOWS
    // ===================================================

    forkJoin({

      moves:
        this.agent.getMoves(fen),

      evaluation:
        this.agent.getEvaluation(fen),

    })
      .pipe(

        // ===============================================
        // SECONDARY WORKFLOWS
        // ===============================================

        switchMap(({
          moves,
          evaluation,
        }) => {

          const opening =
            moves.opening ?? '';

          // =============================================
          // NO OPENING DETECTED
          // =============================================

          if (!opening) {

            return of({

              moves,
              evaluation,

              videos: {
                opening: '',
                count: 0,
                videos: [] as Video[],
              },

              vector: {
                opening: '',
                rag_context: [] as RagItem[],
                source: null,
              },
            });
          }

          // =============================================
          // RAG + VIDEOS
          // =============================================

          return forkJoin({

            videos:
              this.agent.getVideos(
                opening
              ),

            vector:
              this.agent.getRagContext(
                opening
              ),

          }).pipe(

            catchError((error) => {

              console.error(
                'RAG/Videos error:',
                error,
              );

              return of({

                videos: {
                  opening,
                  count: 0,
                  videos: [] as Video[],
                },

                vector: {
                  opening,
                  rag_context: [] as RagItem[],
                  source: null,
                },
              });
            }),

            switchMap(({
              videos,
              vector,
            }) => {

              return of({

                moves,
                evaluation,
                videos,
                vector,
              });
            }),
          );
        }),
      )
      .subscribe({

        // =================================================
        // SUCCESS
        // =================================================

        next: ({
          moves,
          evaluation,
          videos,
          vector,
        }) => {

          const response: AgentResponse = {

            fen,

            source:
              moves.source ??
              evaluation.source ??
              vector.source ??
              null,

            moves:
              moves.moves ?? [],

            evaluation:
              evaluation.evaluation ?? null,

            opening:
              moves.opening ?? null,

            videos:
              videos.videos ?? [],

            rag_context:
              vector.rag_context ?? [],

            explanation:
              moves.explanation ?? null,

            error: null,
          };

          this.store.updateData(
            response
          );

          this.store.setLoading(
            false
          );
        },

        // =================================================
        // ERROR
        // =================================================

        error: (error) => {

          console.error(
            'Analysis error:',
            error,
          );

          this.store.setError(
            'Erreur API'
          );

          this.store.setLoading(
            false
          );
        },
      });
  }


  // =====================================================
  // RESET
  // =====================================================

  reset(): void {

    this.chess.reset();

    const fen =
      this.chess.getFen();

    this.store.setFen(fen);

    this.store.clearData();

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
