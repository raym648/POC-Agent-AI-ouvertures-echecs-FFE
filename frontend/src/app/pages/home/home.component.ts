// POC-Agent-AI-ouvertures-echecs-FFE/frontend/src/app/pages/home/home.component.ts

import { Component } from '@angular/core';

import { CommonModule } from '@angular/common';

import { BoardComponent } from '../../features/board/board.component';
import { RecommendationsComponent } from '../../features/recommendations/recommendations.component';


@Component({
  selector: 'app-home',

  standalone: true,

  imports: [
    CommonModule,
    BoardComponent,
    RecommendationsComponent,
  ],

  template: `
    <div class="layout">

      <!-- BOARD -->
      <section class="left-panel">

        <app-board />

      </section>


      <!-- RECOMMENDATIONS -->
      <aside class="right-panel">

        <app-recommendations />

      </aside>

    </div>
  `,

  styles: [`

    :host {
      display: block;
      width: 100%;
      min-height: 100vh;
    }


    /* =====================================================
       MAIN LAYOUT
    ===================================================== */

    .layout {

      display: flex;

      align-items: flex-start;

      justify-content: space-between;

      gap: 24px;

      padding: 24px;

      box-sizing: border-box;

      min-height: 100vh;
    }


    /* =====================================================
       LEFT PANEL
    ===================================================== */

    .left-panel {

      flex: 1;

      min-width: 0;
    }


    /* =====================================================
       RIGHT PANEL
    ===================================================== */

    .right-panel {

      width: 420px;

      max-width: 420px;

      overflow-y: auto;

      border-left: 1px solid #dcdcdc;

      padding-left: 24px;

      box-sizing: border-box;
    }


    /* =====================================================
       RESPONSIVE
    ===================================================== */

    @media (max-width: 1200px) {

      .layout {

        flex-direction: column;
      }

      .right-panel {

        width: 100%;

        max-width: 100%;

        border-left: none;

        border-top: 1px solid #dcdcdc;

        padding-left: 0;

        padding-top: 24px;
      }
    }

  `],
})
export class HomeComponent {}
