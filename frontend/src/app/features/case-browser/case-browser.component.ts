import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { CaseService, CaseSummary } from '../../core/services/case.service';

@Component({
  selector: 'app-case-browser',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="crt-container crt-flicker">
      <div class="browser-screen">
        <div class="header-section">
          <div class="terminal-line amber">> COLD CASE DATABASE — FILE BROWSER</div>
          <div class="terminal-line amber">═══════════════════════════════════════════════════</div>
        </div>

        <div class="boot-lines" *ngIf="bootLines.length > 0">
          <div *ngFor="let line of bootLines" class="terminal-line" [ngClass]="line.cls">
            {{ line.text }}
          </div>
        </div>

        <div *ngIf="bootComplete" class="filter-bar">
          <button class="filter-btn" [class.active]="activeFilter === 'all'" (click)="setFilter('all')">
            [ ALL CASES ]
          </button>
          <button class="filter-btn" [class.active]="activeFilter === 'difficulty'" (click)="setFilter('difficulty')">
            [ BY DIFFICULTY ]
          </button>
          <button class="filter-btn" [class.active]="activeFilter === 'era'" (click)="setFilter('era')">
            [ BY ERA ]
          </button>
        </div>

        <div *ngIf="bootComplete && cases.length > 0" class="case-grid">
          <div *ngFor="let c of filteredCases"
               class="case-card"
               (click)="openCase(c.id)">
            <div class="card-header">
              <span class="case-number">{{ c.caseNumber }}</span>
              <span class="classification">{{ c.classification }}</span>
            </div>
            <div class="card-title">{{ c.title.toUpperCase() }}</div>
            <div class="card-meta">
              <span>DIFFICULTY: {{ getDifficultyBar(c.difficulty) }}</span>
              <span>ERA: {{ c.era }}</span>
            </div>
            <div class="card-mood">MOOD: {{ c.moodTags.join(', ') }}</div>
            <div class="card-synopsis">"{{ c.synopsis }}"</div>
            <div class="card-action">[ OPEN CASE FILE ]</div>
          </div>
        </div>

        <div *ngIf="bootComplete && cases.length === 0 && !loading" class="terminal-line dim">
          > NO CASES FOUND IN DATABASE.
        </div>

        <div class="footer-section">
          <button class="back-btn" (click)="goBack()">&lt; RETURN TO TERMINAL</button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .browser-screen {
      padding: 40px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .terminal-line {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 16px;
      margin-bottom: 2px;
      white-space: pre-wrap;
    }

    .amber { color: var(--terminal-amber); }
    .dim { color: var(--terminal-dim); }
    .bright { color: var(--terminal-green); }

    .filter-bar {
      display: flex;
      gap: 12px;
      margin: 8px 0;
    }

    .filter-btn {
      background: transparent;
      border: none;
      color: var(--terminal-dim);
      font-family: var(--terminal-font);
      font-size: 14px;
      cursor: pointer;
      padding: 4px 8px;
    }

    .filter-btn:hover, .filter-btn.active {
      color: var(--terminal-green);
    }

    .case-grid {
      display: flex;
      flex-direction: column;
      gap: 16px;
      max-width: 750px;
    }

    .case-card {
      border: 1px solid var(--terminal-green);
      padding: 16px 20px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .case-card:hover {
      background: rgba(0, 255, 65, 0.05);
      border-color: var(--terminal-amber);
      box-shadow: 0 0 10px rgba(0, 255, 65, 0.1);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 4px;
    }

    .case-number {
      font-family: var(--terminal-font);
      color: var(--terminal-amber);
      font-size: 14px;
      font-weight: bold;
    }

    .classification {
      font-family: var(--terminal-font);
      color: var(--terminal-blue);
      font-size: 12px;
    }

    .card-title {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 8px;
    }

    .card-meta {
      font-family: var(--terminal-font);
      color: var(--terminal-dim);
      font-size: 13px;
      display: flex;
      gap: 20px;
      margin-bottom: 4px;
    }

    .card-mood {
      font-family: var(--terminal-font);
      color: var(--terminal-dim);
      font-size: 13px;
      margin-bottom: 8px;
    }

    .card-synopsis {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 14px;
      font-style: italic;
      margin-bottom: 8px;
      opacity: 0.8;
    }

    .card-action {
      font-family: var(--terminal-font);
      color: var(--terminal-amber);
      font-size: 13px;
    }

    .footer-section {
      margin-top: auto;
      padding-top: 20px;
    }

    .back-btn {
      background: transparent;
      border: 1px solid var(--terminal-dim);
      color: var(--terminal-dim);
      font-family: var(--terminal-font);
      font-size: 14px;
      padding: 8px 16px;
      cursor: pointer;
    }

    .back-btn:hover {
      border-color: var(--terminal-green);
      color: var(--terminal-green);
    }
  `]
})
export class CaseBrowserComponent implements OnInit, OnDestroy {
  cases: CaseSummary[] = [];
  filteredCases: CaseSummary[] = [];
  activeFilter = 'all';
  loading = true;
  bootComplete = false;
  bootLines: { text: string; cls: string }[] = [];
  private timeouts: ReturnType<typeof setTimeout>[] = [];

  constructor(
    private caseService: CaseService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.runBootSequence();
    this.caseService.listCases().subscribe({
      next: (cases) => {
        this.cases = cases;
        this.filteredCases = cases;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  ngOnDestroy(): void {
    this.timeouts.forEach(t => clearTimeout(t));
  }

  private runBootSequence(): void {
    const lines = [
      { text: '> ACCESSING COLD CASE DATABASE...', cls: 'dim', delay: 0 },
      { text: '> DECRYPTING CLASSIFIED FILES...', cls: 'dim', delay: 600 },
      { text: '> CONNECTION ESTABLISHED.', cls: 'bright', delay: 1200 },
      { text: `> ${this.cases.length || '...'} CASES FOUND. DISPLAYING RESULTS:`, cls: 'bright', delay: 1800 },
    ];

    lines.forEach(line => {
      const t = setTimeout(() => {
        this.bootLines.push({ text: line.text, cls: line.cls });
      }, line.delay);
      this.timeouts.push(t);
    });

    const t = setTimeout(() => {
      if (this.bootLines.length >= 4) {
        this.bootLines[3] = {
          text: `> ${this.cases.length} CASES FOUND. DISPLAYING RESULTS:`,
          cls: 'bright'
        };
      }
      this.bootComplete = true;
    }, 2200);
    this.timeouts.push(t);
  }

  setFilter(filter: string): void {
    this.activeFilter = filter;
    if (filter === 'all') {
      this.filteredCases = [...this.cases];
    } else if (filter === 'difficulty') {
      this.filteredCases = [...this.cases].sort((a, b) => a.difficulty - b.difficulty);
    } else if (filter === 'era') {
      this.filteredCases = [...this.cases].sort((a, b) => a.era.localeCompare(b.era));
    }
  }

  getDifficultyBar(difficulty: number): string {
    return '\u2588'.repeat(difficulty) + '\u2591'.repeat(5 - difficulty);
  }

  openCase(caseId: number): void {
    this.router.navigate(['/terminal/cases', caseId]);
  }

  goBack(): void {
    this.router.navigate(['/terminal']);
  }
}
