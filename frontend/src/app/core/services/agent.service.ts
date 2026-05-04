// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/core/services/agent.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { AgentResponse } from '../models/agent.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AgentService {
  private readonly API_URL = environment.apiUrl;

  constructor(private http: HttpClient) {}

  analyze(fen: string): Observable<AgentResponse> {
    return this.http.get<AgentResponse>(
      `${this.API_URL}/agent/analyze/${encodeURIComponent(fen)}`
    );
  }
}
