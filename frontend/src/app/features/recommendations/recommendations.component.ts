// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/features/recommendations/recommendations.component.ts

import {
  Component,
  computed,
} from '@angular/core';

import { CommonModule } from '@angular/common';

import { GameStore } from '../../state/game.store';

import {
  MoveEvaluation,
  RagItem,
  Video,
} from '../../core/models/agent.model';


@Component({
  selector: 'app-recommendations',

  standalone: true,

  imports: [
    CommonModule,
  ],

  templateUrl:
    './recommendations.component.html',
})
export class RecommendationsComponent {

  constructor(
    public store: GameStore
  ) {}

  // =====================================================
  // RAW DATA
  // =====================================================

  readonly data = computed(
    () => this.store.data()
  );

  readonly loading = computed(
    () => this.store.loading()
  );

  readonly error = computed(
    () => this.store.error()
  );

  // =====================================================
  // DERIVED STATE
  // =====================================================

  readonly moves = computed<MoveEvaluation[]>(
    () => this.data()?.moves ?? []
  );

  readonly evaluation = computed(
    () => this.data()?.evaluation ?? null
  );

  readonly opening = computed(
    () => this.data()?.opening ?? null
  );

  readonly ragContext = computed<RagItem[]>(
    () => this.data()?.rag_context ?? []
  );

  readonly videos = computed<Video[]>(
    () => this.data()?.videos ?? []
  );

  readonly explanation = computed(
    () => this.data()?.explanation ?? null
  );

  // =====================================================
  // HELPERS
  // =====================================================

  readonly hasMoves = computed(
    () => this.moves().length > 0
  );

  readonly hasVideos = computed(
    () => this.videos().length > 0
  );

  readonly hasRag = computed(
    () => this.ragContext().length > 0
  );

}
