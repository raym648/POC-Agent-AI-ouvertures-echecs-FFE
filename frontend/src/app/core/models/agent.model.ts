// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/core/models/agent.model.ts

// Interface représentant la réponse exacte du backend

export interface Move {
  san: string; // coup en notation algébrique
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
  source: 'lichess' | 'stockfish';
  type: 'theory' | 'evaluation';

  moves?: Move[];
  evaluation?: Evaluation;

  rag?: RagItem[];
  videos?: Video[];
  explanation?: string;

  error?: string;
}
