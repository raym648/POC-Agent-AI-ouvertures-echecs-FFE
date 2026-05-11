// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/core/services/agent.service.ts

import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs';

import {
  AgentResponse,
  RagItem,
  Video,
} from '../models/agent.model';

import { environment } from '../../../environments/environment';


@Injectable({
  providedIn: 'root',
})
export class AgentService {

  // =====================================================
  // API
  // =====================================================

  private readonly API_URL = environment.apiUrl;


  constructor(
    private http: HttpClient
  ) {}


  // =====================================================
  // MOVES WORKFLOW
  // =====================================================

  getMoves(
    fen: string
  ): Observable<AgentResponse> {

    return this.http.get<AgentResponse>(
      `${this.API_URL}/moves/${encodeURIComponent(fen)}`
    );
  }


  // =====================================================
  // EVALUATION WORKFLOW
  // =====================================================

  getEvaluation(
    fen: string
  ): Observable<AgentResponse> {

    return this.http.get<AgentResponse>(
      `${this.API_URL}/evaluate/${encodeURIComponent(fen)}`
    );
  }


  // =====================================================
  // VECTOR SEARCH / RAG
  // =====================================================

  getRagContext(
    opening: string
  ): Observable<{
    opening: string;
    rag_context: RagItem[];
    source?: string;
  }> {

    return this.http.post<{
      opening: string;
      rag_context: RagItem[];
      source?: string;
    }>(
      `${this.API_URL}/vector-search`,
      {
        opening,
      }
    );
  }


  // =====================================================
  // VIDEOS WORKFLOW
  // =====================================================

  getVideos(
    opening: string
  ): Observable<{
    opening: string;
    count: number;
    videos: Video[];
  }> {

    return this.http.get<{
      opening: string;
      count: number;
      videos: Video[];
    }>(
      `${this.API_URL}/videos/${encodeURIComponent(opening)}`
    );
  }

}
