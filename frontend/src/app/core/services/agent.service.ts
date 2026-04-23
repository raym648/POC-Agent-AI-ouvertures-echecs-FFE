// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/core/services/agent.service.ts


import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AgentResponse } from '../models/agent.model';

@Injectable({ providedIn: 'root' })
export class AgentService {

  // URL backend centralisée
  private API_URL = 'http://localhost:8000/api/v1';

  constructor(private http: HttpClient) {}

  // 🔥 Endpoint réel (GET avec FEN dans URL)
  analyze(fen: string): Observable<AgentResponse> {
    return this.http.get<AgentResponse>(
      `${this.API_URL}/agent/analyze/${encodeURIComponent(fen)}`
    );
  }
}
