// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/features/recommendations/recommendations.component.ts

import { Component, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

import { GameStore } from '../../state/game.store';


@Component({
  selector: 'app-recommendations',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './recommendations.component.html',
})
export class RecommendationsComponent {

  constructor(public store: GameStore) {}

  readonly data = computed(() => this.store.data());

  readonly loading = computed(() => this.store.loading());

  readonly error = computed(() => this.store.error());

}
