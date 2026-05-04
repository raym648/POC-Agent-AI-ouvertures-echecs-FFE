// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/core/models/agent.model.ts

// Contrat frontend aligné sur les réponses backend.
// Les champs optionnels reflètent les réponses partielles / dégradées.

export interface Move {
  san: string;
}

export interface Evaluation {
  score: number;
  best_move: string;
}

export interface RagItem {
  text: string;
}

export interface Video {
  title: string;
  url: string;
}

export interface AgentResponse {
  fen: string;

  source?: 'lichess' | 'stockfish' | null;
  type?: 'theory' | 'evaluation';

  moves?: Move[];
  evaluation?: Evaluation;

  rag?: RagItem[];
  videos?: Video[];
  explanation?: string;

  error?: string;
}
