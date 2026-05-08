// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/core/models/agent.model.ts

// Contrat frontend aligné sur les réponses backend.
// Les champs optionnels reflètent les réponses partielles / dégradées.

// =========================================================
// MOVES
// =========================================================

export interface MoveEvaluation {
  move: string;
  evaluation?: number | null;
}


// =========================================================
// STOCKFISH EVALUATION
// =========================================================

export interface StockfishEvaluation {
  type: string;
  value: number;
  best_move?: string | null;
  depth?: number | null;
}


// =========================================================
// RAG
// =========================================================

export interface RagItem {
  opening?: string;
  variation?: string;
  text: string;
  score?: number;
}


// =========================================================
// VIDEOS
// =========================================================

export interface Video {
  title: string;
  video_id?: string;
  url: string;
  thumbnail?: string;
  description?: string;
  channel?: string;
}


// =========================================================
// MAIN RESPONSE
// =========================================================

export interface AgentResponse {

  fen: string;

  source?: string | null;

  moves?: MoveEvaluation[];

  evaluation?: StockfishEvaluation | null;

  rag_context?: RagItem[];

  videos?: Video[];

  explanation?: string | null;

  opening?: string | null;

  message?: string;

  error?: string | null;

}
