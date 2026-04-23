//  POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/app.component.ts

import { Component } from '@angular/core';
import { BoardComponent } from './features/board/board.component';
import { RecommendationsComponent } from './features/recommendations/recommendations.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [BoardComponent, RecommendationsComponent],
  template: `
    <div class="layout">

      <div class="left">
        <app-board></app-board>
      </div>

      <div class="right">
        <app-recommendations></app-recommendations>
      </div>

    </div>
  `,
  styles: [`
    .layout {
      display: flex;
      height: 100vh;
    }

    .left {
      flex: 1;
    }

    .right {
      width: 400px;
      overflow: auto;
      padding: 16px;
      border-left: 1px solid #ccc;
    }
  `]
})
export class AppComponent {}
