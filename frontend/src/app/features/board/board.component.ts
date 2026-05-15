// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/features/board/board.component.ts

import {
  AfterViewInit,
  Component,
  ElementRef,
  OnDestroy,
  OnInit,
  ViewChild,
  computed,
  effect,
  signal,
} from '@angular/core';

import { CommonModule } from '@angular/common';

import { Chessground } from 'chessground';

import type { Api } from 'chessground/api';
import type { DrawShape } from 'chessground/draw';
import type { Key } from 'chessground/types';

import {
  Subject,
  Subscription,
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


type GameMode =
  | 'human-vs-human'
  | 'human-vs-ai';


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
  implements
    OnInit,
    AfterViewInit,
    OnDestroy {

  // =====================================================
  // VIEW
  // =====================================================

  @ViewChild('board', { static: true })
  private boardRef!: ElementRef<HTMLElement>;

  // =====================================================
  // RXJS
  // =====================================================

  private move$ =
    new Subject<void>();

  private moveSubscription?:
    Subscription;

  // =====================================================
  // CHESSGROUND
  // =====================================================

  private cg?: Api;

  // =====================================================
  // AI CONTROL
  // =====================================================

  private engineMoveTimeout?:
    ReturnType<typeof setTimeout>;

  private isApplyingEngineMove =
    false;

  private isResetting =
    false;

  // =====================================================
  // GAME MODE
  // =====================================================

  readonly gameMode =
    signal<GameMode>(
      'human-vs-human'
    );

  readonly whitePlayerLabel =
    computed(() => {

      return this.gameMode() === 'human-vs-ai'
        ? 'Humain'
        : 'Blancs';
    });

  readonly blackPlayerLabel =
    computed(() => {

      return this.gameMode() === 'human-vs-ai'
        ? 'AI'
        : 'Noirs';
    });


  constructor(
    private chess: ChessService,
    private agent: AgentService,
    public store: GameStore,
  ) {

    // ===================================================
    // STORE -> BOARD SYNC
    // ===================================================

    effect(() => {

      if (!this.cg) {
        return;
      }

      if (
        this.isApplyingEngineMove ||
        this.isResetting
      ) {
        return;
      }

      this.syncBoard(
        this.store.fen()
      );
    });

    // ===================================================
    // ENGINE LINES
    // ===================================================

    effect(() => {

      if (!this.cg) {
        return;
      }

      const data =
        this.store.data();

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

    this.moveSubscription =
      this.move$
        .pipe(
          debounceTime(250),
        )
        .subscribe(() => {

          if (
            this.isResetting ||
            this.isApplyingEngineMove
          ) {
            return;
          }

          this.analyze();
        });
  }


  // =====================================================
  // DESTROY
  // =====================================================

  ngOnDestroy(): void {

    this.moveSubscription
      ?.unsubscribe();

    if (
      this.engineMoveTimeout
    ) {

      clearTimeout(
        this.engineMoveTimeout
      );
    }
  }


  // =====================================================
  // CHESSGROUND INIT
  // =====================================================

  ngAfterViewInit(): void {

    this.cg = Chessground(
      this.boardRef.nativeElement,
      {
        fen:
          this.chess.getFen(),

        orientation: 'white',

        movable: {

          free: false,

          color:
            this.getMovableColor(),

          dests:
            this.buildDests(),

          events: {

            after: (
              from: string,
              to: string,
            ) => {

              if (
                this.isApplyingEngineMove ||
                this.isResetting
              ) {
                return;
              }

              this.onMove({
                from,
                to,
              });
            },
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

        animation: {
          enabled: true,
          duration: 180,
        },
      },
    );

    this.syncBoard(
      this.chess.getFen()
    );
  }


  // =====================================================
  // GAME MODE
  // =====================================================

  setGameMode(
    mode: GameMode
  ): void {

    if (
      this.gameMode() === mode
    ) {
      return;
    }

    this.gameMode.set(mode);

    this.reset();
  }


  // =====================================================
  // MOVE HANDLER
  // =====================================================

  onMove(event: {
    from: string;
    to: string;
  }): void {

    console.log(
      '[HUMAN MOVE START]',
      {
        from: event.from,
        to: event.to,
        turnBefore:
          this.chess.turn(),
      },
    );

    if (
      this.isApplyingEngineMove ||
      this.isResetting
    ) {

      console.log(
        '[HUMAN MOVE BLOCKED]',
        {
          isApplyingEngineMove:
            this.isApplyingEngineMove,

          isResetting:
            this.isResetting,
        },
      );

      return;
    }

    // ===================================================
    // HUMAN VS AI
    // ===================================================

    if (
      this.gameMode() ===
        'human-vs-ai' &&
      this.chess.turn() !== 'w'
    ) {

      console.log(
        '[HUMAN MOVE REFUSED]',
        {
          reason:
            'Not white turn',
          currentTurn:
            this.chess.turn(),
        },
      );

      this.syncBoard(
        this.chess.getFen()
      );

      return;
    }

    const success =
      this.chess.move(
        event.from,
        event.to,
      );

    console.log(
      '[HUMAN MOVE RESULT]',
      {
        success,
        turnAfter:
          this.chess.turn(),
        fen:
          this.chess.getFen(),
      },
    );

    if (!success) {

      this.syncBoard(
        this.chess.getFen()
      );

      return;
    }

    const fen =
      this.chess.getFen();

    this.store.setFen(fen);

    this.syncBoard(fen);

    this.move$.next();
  }


  // =====================================================
  // ANALYSIS
  // =====================================================

  analyze(): void {

    console.log(
      '[ANALYZE START]',
      {
        turn:
          this.chess.turn(),
        fen:
          this.chess.getFen(),
      },
    );

    if (
      this.isResetting ||
      this.isApplyingEngineMove
    ) {

      console.log(
        '[ANALYZE BLOCKED]',
        {
          isResetting:
            this.isResetting,

          isApplyingEngineMove:
            this.isApplyingEngineMove,
        },
      );

      return;
    }

    const fen =
      this.chess.getFen();

    this.store.setLoading(true);

    this.store.clearError();

    forkJoin({

      moves:
        this.agent.getMoves(fen),

      evaluation:
        this.agent.getEvaluation(fen),

    })
      .pipe(

        switchMap(({
          moves,
          evaluation,
        }) => {

          const opening =
            moves.opening ?? '';

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

        next: ({
          moves,
          evaluation,
          videos,
          vector,
        }) => {

          console.log(
            '[ANALYZE RESULT]',
            {
              turn:
                this.chess.turn(),

              bestMove:
                evaluation
                  ?.evaluation
                  ?.best_move,
            },
          );

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

          this.playEngineMoveIfNeeded(
            response
          );
        },

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
  // AI MOVE
  // =====================================================

  private playEngineMoveIfNeeded(
    response: AgentResponse
  ): void {

    console.log(
      '[AI CHECK]',
      {
        mode:
          this.gameMode(),
        turn:
          this.chess.turn(),
        isApplyingEngineMove:
          this.isApplyingEngineMove,
      },
    );

    if (
      this.gameMode() !==
      'human-vs-ai'
    ) {
      return;
    }

    if (
      this.chess.turn() !== 'b'
    ) {
      return;
    }

    if (
      this.isApplyingEngineMove
    ) {
      return;
    }

    const bestMove =
      response.evaluation?.best_move;

    console.log(
      '[AI BEST MOVE]',
      {
        bestMove,
      },
    );

    if (
      !bestMove ||
      bestMove.length < 4
    ) {
      return;
    }

    const from =
      bestMove.slice(0, 2);

    const to =
      bestMove.slice(2, 4);

    this.isApplyingEngineMove =
      true;

    if (
      this.engineMoveTimeout
    ) {

      clearTimeout(
        this.engineMoveTimeout
      );
    }

    this.engineMoveTimeout =
      setTimeout(() => {

        console.log(
          '[AI MOVE START]',
          {
            from,
            to,
            turnBefore:
              this.chess.turn(),
          },
        );

        if (
          this.isResetting
        ) {

          this.isApplyingEngineMove =
            false;

          return;
        }

        const success =
          this.chess.move(
            from,
            to,
          );

        console.log(
          '[AI MOVE RESULT]',
          {
            success,
            turnAfter:
              this.chess.turn(),
            fen:
              this.chess.getFen(),
          },
        );

        if (!success) {

          this.isApplyingEngineMove =
            false;

          this.syncBoard(
            this.chess.getFen()
          );

          return;
        }

        const fen =
          this.chess.getFen();

        this.store.setFen(fen);

        this.syncBoard(fen);

        // IMPORTANT:
        // release engine lock
        // AFTER board sync

        setTimeout(() => {

          this.isApplyingEngineMove =
            false;

          // =========================================
          // RE-ANALYZE NEW POSITION
          // =========================================

          this.move$.next();

        }, 0);

      }, 500);
  }


  // =====================================================
  // RESET
  // =====================================================

  reset(): void {

    console.log(
      '[RESET START]',
    );

    this.isResetting = true;

    this.isApplyingEngineMove =
      false;

    if (
      this.engineMoveTimeout
    ) {

      clearTimeout(
        this.engineMoveTimeout
      );
    }

    this.chess.reset();

    const fen =
      this.chess.getFen();

    this.store.reset();

    this.store.setFen(fen);

    this.syncBoard(fen);

    setTimeout(() => {

      this.isResetting =
        false;

      console.log(
        '[RESET END]',
      );

    }, 150);
  }


  // =====================================================
  // BOARD SYNC
  // =====================================================

  private syncBoard(
    fen: string,
  ): void {

    if (!this.cg) {
      return;
    }

    const turn =
      this.chess.turn();

    const dests =
      this.buildDests();

    const movableColor =
      this.getMovableColor();

    console.log(
      '[SYNC BOARD]',
      {
        fen,
        turn,
        movableColor,
        destsSize:
          dests.size,
      },
    );

    this.cg.set({

      fen,

      turnColor:
        turn === 'w'
          ? 'white'
          : 'black',

      movable: {

        free: false,

        color:
          movableColor,

        dests,

        events: {

          after: (
            from: string,
            to: string,
          ) => {

            if (
              this.isApplyingEngineMove ||
              this.isResetting
            ) {
              return;
            }

            this.onMove({
              from,
              to,
            });
          },
        },
      },

      highlight: {
        lastMove: true,
        check: true,
      },

      drawable: {
        enabled: true,
        visible: true,
      },

      animation: {
        enabled: true,
        duration: 180,
      },
    });

    this.cg.redrawAll();
  }


  // =====================================================
  // MOVABLE COLOR
  // =====================================================

  private getMovableColor():
    'white'
    | 'black'
    | 'both'
    | undefined {

    if (
      this.gameMode() ===
      'human-vs-human'
    ) {
      return 'both';
    }

    return this.chess.turn() === 'w'
      ? 'white'
      : undefined;
  }


  // =====================================================
  // LEGAL MOVES
  // =====================================================

  private buildDests():
    Map<Key, Key[]> {

    const dests =
      new Map<Key, Key[]>();

    const legalMoves =
      this.chess.getLegalMoves();

    console.log(
      '[BUILD DESTS]',
      {
        turn:
          this.chess.turn(),

        legalMovesCount:
          legalMoves.length,

        legalMoves,
      },
    );

    for (const move of legalMoves) {

      const from =
        move.from as Key;

      const to =
        move.to as Key;

      const existing =
        dests.get(from);

      if (existing) {

        existing.push(to);

      } else {

        dests.set(from, [to]);
      }
    }

    return dests;
  }

}
