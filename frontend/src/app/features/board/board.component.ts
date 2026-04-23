// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/features/board/board.component.ts

import { Component, OnInit, effect } from '@angular/core';
// import { NgxChessgroundModule } from 'ngx-chessground';
import { NgxChessgroundComponent } from 'ngx-chessground';
import { ChessService } from '../../core/services/chess.service';
import { AgentService } from '../../core/services/agent.service';
import { GameStore } from '../../state/game.store';
import { Subject, debounceTime } from 'rxjs';

// chess.js (important pour convertir SAN → coordonnées)
import { Chess } from 'chess.js';

@Component({
  selector: 'app-board',
  standalone: true,
  // imports: [NgxChessgroundModule],
  imports: [NgxChessgroundComponent],
  templateUrl: './board.component.html',
  styleUrls: ['./board.component.css']
})
export class BoardComponent implements OnInit {

  // ================================
  // Debounce API
  // ================================
  private move$ = new Subject<void>();

  // ================================
  // Configuration Chessground
  // ================================
  boardConfig: any = {
    fen: 'start',
    orientation: 'white',

    // Interaction utilisateur
    movable: {
      free: false,
      color: 'both'
    },

    // Highlight du dernier coup
    highlight: {
      lastMove: true,
      check: true
    },

    // 🔥 Flèches (best moves)
    drawable: {
      enabled: true,
      visible: true,
      autoShapes: []
    }
  };

  constructor(
    private chess: ChessService,
    private agent: AgentService,
    private store: GameStore
  ) {

    // ================================
    // 🔥 Sync FEN → UI
    // ================================
    effect(() => {
      const fen = this.store.fen();

      if (!fen) return;

      this.boardConfig = {
        ...this.boardConfig,
        fen: fen === 'start' ? undefined : fen
      };
    });

    // ================================
    // 🔥 Sync recommandations → flèches
    // ================================
    effect(() => {
      const data = this.store.data();

      if (!data || !data.moves) {
        this.boardConfig.drawable.autoShapes = [];
        return;
      }

      const chess = new Chess(this.store.fen());

      const shapes: any[] = [];

      data.moves.slice(0, 3).forEach((m: any) => {
        try {
          // const move = chess.move(m.san, { sloppy: true });
          const move = chess.move(m.san, { strict: false });

          if (move) {
            shapes.push({
              orig: move.from,
              dest: move.to,
              brush: 'green'
            });

            chess.undo(); // ⚠️ critique pour éviter dérive
          }
        } catch {
          // ignore erreurs SAN
        }
      });

      this.boardConfig.drawable.autoShapes = shapes;
    });
  }

  // ================================
  // Init
  // ================================
  ngOnInit(): void {
    this.move$.pipe(debounceTime(400)).subscribe(() => {
      this.analyze();
    });
  }

  // ================================
  // Move utilisateur
  // ================================
  onMove(event: any) {
    const { from, to } = event;

    // validation via chess.js backend wrapper
    if (!this.chess.move(from, to)) return;

    const fen = this.chess.getFen();

    // 🔥 update store global
    this.store.fen.set(fen);

    // 🔁 déclenche analyse (debounced)
    this.move$.next();
  }

  // ================================
  // Appel backend
  // ================================
  analyze() {
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

  // ================================
  // Reset
  // ================================
  reset() {
    this.chess.reset();

    this.store.fen.set('start');
    this.store.data.set(null);

    // reset visuel
    this.boardConfig.drawable.autoShapes = [];
  }
}
