import { Component, OnInit, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { CdkDragDrop, CdkDrag, CdkDropList, CdkDragEnd } from '@angular/cdk/drag-drop';
import { CaseService, Evidence } from '../../core/services/case.service';

interface BoardCard {
  evidence: Evidence;
  position: { x: number; y: number };
}

interface Connection {
  fromId: number;
  toId: number;
  isCorrect: boolean | null; // null = unchecked
}

@Component({
  selector: 'app-evidence-board',
  standalone: true,
  imports: [CommonModule, CdkDrag, CdkDropList],
  template: `
    <div class="board-container">
      <!-- Notifications -->
      <div class="board-notifications">
        <div *ngFor="let note of notifications" class="board-notification"
             [class.correct]="note.type === 'correct'"
             [class.incorrect]="note.type === 'incorrect'">
          > {{ note.message }}
        </div>
      </div>

      <!-- SVG layer for connections -->
      <svg class="connections-layer" #svgLayer>
        <line *ngFor="let conn of connections"
              [attr.x1]="getCardCenter(conn.fromId).x"
              [attr.y1]="getCardCenter(conn.fromId).y"
              [attr.x2]="getCardCenter(conn.toId).x"
              [attr.y2]="getCardCenter(conn.toId).y"
              [attr.stroke]="conn.isCorrect === true ? '#00ff41' : conn.isCorrect === false ? '#ff4444' : '#ff8800'"
              stroke-width="2"
              stroke-dasharray="8,4" />
        <!-- Line preview while connecting -->
        <line *ngIf="connectingFrom !== null && mousePos"
              [attr.x1]="getCardCenter(connectingFrom).x"
              [attr.y1]="getCardCenter(connectingFrom).y"
              [attr.x2]="mousePos.x"
              [attr.y2]="mousePos.y"
              stroke="#ffaa00"
              stroke-width="1"
              stroke-dasharray="4,4"
              opacity="0.6" />
      </svg>

      <!-- Evidence cards -->
      <div *ngFor="let card of cards; let i = index"
           class="evidence-card"
           cdkDrag
           [cdkDragFreeDragPosition]="card.position"
           (cdkDragEnded)="onDragEnd($event, i)"
           [class.selected]="connectingFrom === card.evidence.id"
           [class.discovered]="card.evidence.discovered"
           [class.redacted]="!card.evidence.discovered"
           (click)="onCardClick(card, $event)">
        <div class="card-type">{{ getTypeIcon(card.evidence.type) }}</div>
        <div class="card-title">{{ card.evidence.title }}</div>
        <div class="card-desc" *ngIf="card.evidence.discovered">{{ card.evidence.description | slice:0:80 }}...</div>
        <div class="card-desc" *ngIf="!card.evidence.discovered">████████████</div>
        <div class="card-connect-hint" *ngIf="connectingFrom !== null && connectingFrom !== card.evidence.id">
          [ CONNECT ]
        </div>
      </div>

      <!-- Controls -->
      <div class="board-controls">
        <div class="control-hint" *ngIf="connectingFrom === null">
          > Click a card to start connecting evidence
        </div>
        <div class="control-hint active" *ngIf="connectingFrom !== null">
          > Select another card to draw connection — or click same card to cancel
        </div>
        <button class="return-btn" (click)="goBack()">[ RETURN TO TERMINAL ]</button>
      </div>
    </div>
  `,
  styles: [`
    .board-container {
      position: relative;
      min-height: 100vh;
      background: #1a1412;
      background-image:
        radial-gradient(circle at 20% 30%, rgba(60, 40, 20, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(40, 30, 15, 0.3) 0%, transparent 50%);
      overflow: hidden;
      padding: 20px;
    }

    .connections-layer {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 1;
    }

    .evidence-card {
      position: absolute;
      width: 220px;
      background: #0d0d0d;
      border: 1px solid #333;
      padding: 12px;
      cursor: grab;
      z-index: 2;
      box-shadow: 2px 4px 12px rgba(0,0,0,0.6);
      transition: border-color 0.2s;
    }

    .evidence-card:active { cursor: grabbing; }

    .evidence-card.selected {
      border-color: #ffaa00;
      box-shadow: 0 0 12px rgba(255, 170, 0, 0.3);
    }

    .evidence-card.redacted {
      opacity: 0.4;
    }

    .evidence-card:hover {
      border-color: #00ff41;
    }

    .card-type {
      font-family: var(--terminal-font, 'Courier New', monospace);
      color: #00aaff;
      font-size: 11px;
      margin-bottom: 4px;
    }

    .card-title {
      font-family: var(--terminal-font, 'Courier New', monospace);
      color: #00ff41;
      font-size: 13px;
      font-weight: bold;
      margin-bottom: 6px;
    }

    .card-desc {
      font-family: var(--terminal-font, 'Courier New', monospace);
      color: #666;
      font-size: 11px;
      line-height: 1.3;
    }

    .card-connect-hint {
      font-family: var(--terminal-font, 'Courier New', monospace);
      color: #ffaa00;
      font-size: 11px;
      margin-top: 8px;
      text-align: center;
      animation: pulse 1s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    .board-controls {
      position: fixed;
      bottom: 20px;
      left: 20px;
      right: 20px;
      z-index: 10;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .control-hint {
      font-family: var(--terminal-font, 'Courier New', monospace);
      color: #666;
      font-size: 13px;
    }

    .control-hint.active {
      color: #ffaa00;
    }

    .return-btn {
      background: transparent;
      border: 1px solid #666;
      color: #666;
      font-family: var(--terminal-font, 'Courier New', monospace);
      font-size: 14px;
      padding: 8px 16px;
      cursor: pointer;
    }

    .return-btn:hover {
      border-color: #00ff41;
      color: #00ff41;
    }

    .board-notifications {
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 20;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .board-notification {
      font-family: var(--terminal-font, 'Courier New', monospace);
      font-size: 13px;
      padding: 8px 16px;
      border: 1px solid;
      background: rgba(0,0,0,0.9);
      animation: fadeIn 0.3s ease-out;
    }

    .board-notification.correct {
      color: #00ff41;
      border-color: #00ff41;
    }

    .board-notification.incorrect {
      color: #ff4444;
      border-color: #ff4444;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `]
})
export class EvidenceBoardComponent implements OnInit {
  cards: BoardCard[] = [];
  connections: Connection[] = [];
  connectingFrom: number | null = null;
  mousePos: { x: number; y: number } | null = null;
  notifications: { message: string; type: string }[] = [];

  private caseId!: number;

  constructor(
    private caseService: CaseService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.caseId = Number(this.route.snapshot.paramMap.get('caseId'));
    this.loadEvidence();
  }

  private loadEvidence(): void {
    this.caseService.getEvidence(this.caseId).subscribe({
      next: (evidence) => {
        this.cards = evidence.map((ev, i) => ({
          evidence: ev,
          position: {
            x: 60 + (i % 4) * 260,
            y: 60 + Math.floor(i / 4) * 200
          }
        }));
      }
    });
  }

  getTypeIcon(type: string): string {
    const icons: Record<string, string> = {
      PHYSICAL: '[PHY]',
      TESTIMONIAL: '[TST]',
      FORENSIC: '[FOR]',
      DOCUMENTARY: '[DOC]'
    };
    return icons[type] || '[EVD]';
  }

  getCardCenter(evidenceId: number): { x: number; y: number } {
    const card = this.cards.find(c => c.evidence.id === evidenceId);
    if (!card) return { x: 0, y: 0 };
    return {
      x: card.position.x + 110,
      y: card.position.y + 60
    };
  }

  onDragEnd(event: CdkDragEnd, index: number): void {
    const pos = event.source.getFreeDragPosition();
    this.cards[index].position = { x: pos.x, y: pos.y };
  }

  onCardClick(card: BoardCard, event: Event): void {
    event.stopPropagation();

    if (this.connectingFrom === null) {
      this.connectingFrom = card.evidence.id;
    } else if (this.connectingFrom === card.evidence.id) {
      // Cancel
      this.connectingFrom = null;
    } else {
      // Create connection
      this.createConnection(this.connectingFrom, card.evidence.id);
      this.connectingFrom = null;
    }
  }

  private createConnection(fromId: number, toId: number): void {
    // Check if connection already exists
    const exists = this.connections.some(
      c => (c.fromId === fromId && c.toId === toId) ||
           (c.fromId === toId && c.toId === fromId)
    );
    if (exists) return;

    // Check if the two evidence items share a linked suspect
    const fromCard = this.cards.find(c => c.evidence.id === fromId);
    const toCard = this.cards.find(c => c.evidence.id === toId);

    // For correlation: both items must be discovered. We approximate
    // "related" by checking if they share the same evidence type or
    // are both non-redacted (discovered). The actual correlation logic
    // would need suspect linkage data from the backend, but since we
    // don't expose linked_suspect_ids to the frontend, we use a simpler
    // heuristic: items with the same type or both physical items are
    // considered correlated for the board UX.
    let isCorrect: boolean = false;
    if (fromCard && toCard && fromCard.evidence.discovered && toCard.evidence.discovered) {
      // Simple correlation: same type = related
      isCorrect = fromCard.evidence.type === toCard.evidence.type;
    }

    this.connections.push({ fromId, toId, isCorrect });

    if (isCorrect) {
      this.showNotification('CORRELATION CONFIRMED: Evidence items share forensic markers.', 'correct');
    } else {
      this.showNotification('NO CORRELATION FOUND', 'incorrect');
    }
  }

  private showNotification(message: string, type: string): void {
    this.notifications.push({ message, type });
    setTimeout(() => {
      this.notifications = this.notifications.filter(n => n.message !== message);
    }, 5000);
  }

  goBack(): void {
    this.router.navigate(['/terminal/cases', this.caseId]);
  }
}
