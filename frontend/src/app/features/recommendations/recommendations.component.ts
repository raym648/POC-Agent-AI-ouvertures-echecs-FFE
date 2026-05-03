// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/features/recommendations/recommendations.component.ts

import { Component, computed } from '@angular/core';
import { GameStore } from '../../state/game.store';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'app-recommendations',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './recommendations.component.html'
})
export class RecommendationsComponent {

  constructor(public store: GameStore) {}

  data = computed(() => this.store.data());
  loading = computed(() => this.store.loading());
  error = computed(() => this.store.error());
}
