import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import {
  CaseService,
  CaseWithProgress,
  Suspect,
  Evidence,
  SolveResult,
} from '../../core/services/case.service';

const RANK_ASCII: Record<string, string> = {
  'ROOKIE': `
    ╔═══════════════╗
    ║    ☆          ║
    ║   ROOKIE      ║
    ╚═══════════════╝`,
  'DETECTIVE': `
    ╔═══════════════╗
    ║   ★ ☆         ║
    ║  DETECTIVE     ║
    ╚═══════════════╝`,
  'SENIOR DETECTIVE': `
    ╔═══════════════════╗
    ║  ★ ★ ☆            ║
    ║ SENIOR DETECTIVE   ║
    ╚═══════════════════╝`,
  'SPECIAL AGENT': `
    ╔═══════════════════╗
    ║  ★ ★ ★ ☆          ║
    ║  SPECIAL AGENT     ║
    ╚═══════════════════╝`,
  'CHIEF INVESTIGATOR': `
    ╔═══════════════════════╗
    ║  ★ ★ ★ ★ ★            ║
    ║  CHIEF INVESTIGATOR    ║
    ╚═══════════════════════╝`,
};

@Component({
  selector: 'app-case-report',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="crt-container crt-flicker">

      <!-- FORM VIEW -->
      <div class="report-screen" *ngIf="phase === 'form'">
        <div class="terminal-line amber">> FILING CASE REPORT — {{ caseData?.case?.caseNumber }}</div>
        <div class="terminal-line warning">> WARNING: This action is final. Ensure your investigation is complete.</div>
        <div class="terminal-line amber">═══════════════════════════════════════</div>

        <div class="form-section">
          <div class="form-group">
            <label class="form-label">> ACCUSED:</label>
            <select class="terminal-select" [(ngModel)]="accusedSuspectId">
              <option [ngValue]="0" disabled>-- SELECT SUSPECT --</option>
              <option *ngFor="let s of suspects" [ngValue]="s.id">{{ s.name }} ({{ s.occupation }})</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">> MOTIVE:</label>
            <textarea class="terminal-textarea" [(ngModel)]="motive"
                      placeholder="Describe the suspect's motive..." rows="3"></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">> METHOD:</label>
            <textarea class="terminal-textarea" [(ngModel)]="method"
                      placeholder="How was the crime committed..." rows="2"></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">> KEY EVIDENCE: (select from discovered evidence)</label>
            <div class="evidence-checklist">
              <label *ngFor="let ev of discoveredEvidence" class="evidence-check">
                <input type="checkbox" [checked]="selectedEvidenceIds.includes(ev.id)"
                       (change)="toggleEvidence(ev.id)" />
                <span>{{ ev.title }}</span>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">> TIMELINE OF EVENTS:</label>
            <textarea class="terminal-textarea" [(ngModel)]="timeline"
                      placeholder="Reconstruct the timeline of events..." rows="4"></textarea>
          </div>

          <div class="form-actions">
            <button class="submit-btn" (click)="submitReport()"
                    [disabled]="!canSubmit()">[ SUBMIT REPORT ]</button>
            <button class="cancel-btn" (click)="goBack()">[ CONTINUE INVESTIGATING ]</button>
          </div>
        </div>
      </div>

      <!-- PROCESSING ANIMATION -->
      <div class="report-screen processing-screen" *ngIf="phase === 'processing'">
        <div *ngFor="let line of processingLines; let i = index"
             class="terminal-line"
             [class.amber]="i === processingLines.length - 1"
             [class.dim]="i < processingLines.length - 1">
          > {{ line }}
        </div>
      </div>

      <!-- RESULTS REVEAL -->
      <div class="report-screen results-screen" *ngIf="phase === 'results' && result">
        <div class="terminal-line amber">> ═══════════════════════════════════════</div>
        <div class="terminal-line verdict" [class.solved]="result.correctKiller" [class.failed]="!result.correctKiller">
          > CASE VERDICT: {{ result.correctKiller ? 'SOLVED' : 'UNSOLVED' }}
        </div>
        <div class="terminal-line score-line">> ACCURACY RATING: {{ result.overallScore }}/100</div>
        <div class="rank-badge">{{ getRankAscii(result.rankEarned) }}</div>
        <div class="terminal-line amber">> RANK EARNED: {{ result.rankEarned }}</div>

        <div class="terminal-line amber" style="margin-top: 16px">> BREAKDOWN:</div>
        <div class="breakdown">
          <div class="breakdown-row">
            <span>Correct Killer:</span>
            <span [class.green]="result.correctKiller" [class.red]="!result.correctKiller">
              {{ result.correctKiller ? '✓ YES' : '✗ NO' }}
            </span>
          </div>
          <div class="breakdown-row">
            <span>Motive Accuracy:</span>
            <span>{{ (result.motiveAccuracy * 100) | number:'1.0-0' }}%</span>
          </div>
          <div class="breakdown-row">
            <span>Evidence Score:</span>
            <span>{{ (result.evidenceScore * 100) | number:'1.0-0' }}%</span>
          </div>
          <div class="breakdown-row" *ngIf="result.redHerringPenalty > 0">
            <span>Red Herring Penalty:</span>
            <span class="red">-{{ result.redHerringPenalty }}</span>
          </div>
          <div class="breakdown-row">
            <span>Discovery Rate:</span>
            <span>{{ (result.discoveryRate * 100) | number:'1.0-0' }}%</span>
          </div>
        </div>

        <div class="terminal-line dim" style="margin-top: 16px">> {{ result.feedback }}</div>

        <div class="solution-section" *ngIf="showSolution">
          <div class="terminal-line amber" style="margin-top: 16px">> FULL SOLUTION:</div>
          <div class="solution-text">{{ result.fullSolution }}</div>
        </div>
        <button *ngIf="!showSolution" class="reveal-btn" (click)="showSolution = true">
          [ REVEAL FULL SOLUTION ]
        </button>

        <div class="terminal-line dim" style="margin-top: 16px">> YOUR AGENT PROFILE HAS BEEN UPDATED.</div>

        <div class="result-actions">
          <button class="action-btn" (click)="returnToTerminal()">[ RETURN TO TERMINAL ]</button>
          <button class="action-btn" (click)="browseCases()">[ BROWSE MORE CASES ]</button>
        </div>
      </div>

      <!-- LOADING -->
      <div *ngIf="loading" class="report-screen">
        <div class="terminal-line dim">> LOADING CASE DATA...</div>
      </div>
    </div>
  `,
  styles: [`
    .report-screen {
      padding: 40px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .terminal-line {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 14px;
      white-space: pre-wrap;
    }

    .amber { color: var(--terminal-amber); }
    .dim { color: var(--terminal-dim); }
    .warning { color: #ff6600; }
    .green { color: #00ff41; }
    .red { color: #ff4444; }

    .form-section {
      display: flex;
      flex-direction: column;
      gap: 16px;
      max-width: 700px;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .form-label {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 14px;
    }

    .terminal-select, .terminal-textarea {
      background: #0a0a0a;
      border: 1px solid var(--terminal-dim);
      color: var(--terminal-green);
      font-family: var(--terminal-font);
      font-size: 13px;
      padding: 8px;
      outline: none;
    }

    .terminal-select option {
      background: #0a0a0a;
      color: var(--terminal-green);
    }

    .terminal-select:focus, .terminal-textarea:focus {
      border-color: var(--terminal-green);
    }

    .terminal-textarea::placeholder {
      color: #333;
    }

    .evidence-checklist {
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-left: 16px;
    }

    .evidence-check {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 13px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .evidence-check input[type="checkbox"] {
      accent-color: var(--terminal-green);
    }

    .form-actions {
      display: flex;
      gap: 12px;
      margin-top: 12px;
    }

    .submit-btn {
      background: transparent;
      border: 1px solid var(--terminal-amber);
      color: var(--terminal-amber);
      font-family: var(--terminal-font);
      font-size: 14px;
      padding: 10px 20px;
      cursor: pointer;
    }

    .submit-btn:hover:not(:disabled) {
      background: var(--terminal-amber);
      color: var(--terminal-bg);
    }

    .submit-btn:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    .cancel-btn {
      background: transparent;
      border: 1px solid var(--terminal-dim);
      color: var(--terminal-dim);
      font-family: var(--terminal-font);
      font-size: 14px;
      padding: 10px 20px;
      cursor: pointer;
    }

    .cancel-btn:hover {
      border-color: var(--terminal-green);
      color: var(--terminal-green);
    }

    /* Processing */
    .processing-screen {
      justify-content: center;
      align-items: center;
    }

    /* Results */
    .verdict {
      font-size: 22px;
      font-weight: bold;
    }

    .verdict.solved { color: #00ff41; }
    .verdict.failed { color: #ff4444; }

    .score-line {
      font-size: 18px;
      color: var(--terminal-amber);
    }

    .rank-badge {
      font-family: var(--terminal-font);
      color: var(--terminal-amber);
      font-size: 14px;
      white-space: pre;
      margin: 8px 0;
    }

    .breakdown {
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-left: 16px;
    }

    .breakdown-row {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 14px;
      display: flex;
      gap: 16px;
    }

    .breakdown-row span:first-child {
      min-width: 200px;
      color: var(--terminal-dim);
    }

    .solution-text {
      font-family: var(--terminal-font);
      color: #00cc33;
      font-size: 13px;
      line-height: 1.6;
      white-space: pre-wrap;
      padding: 16px;
      border: 1px solid var(--terminal-dim);
      margin-top: 8px;
      max-width: 750px;
    }

    .reveal-btn {
      background: transparent;
      border: 1px solid var(--terminal-dim);
      color: var(--terminal-dim);
      font-family: var(--terminal-font);
      font-size: 13px;
      padding: 6px 14px;
      cursor: pointer;
      align-self: flex-start;
      margin-top: 8px;
    }

    .reveal-btn:hover {
      border-color: var(--terminal-green);
      color: var(--terminal-green);
    }

    .result-actions {
      display: flex;
      gap: 12px;
      margin-top: 20px;
    }

    .action-btn {
      background: transparent;
      border: 1px solid var(--terminal-green);
      color: var(--terminal-green);
      font-family: var(--terminal-font);
      font-size: 14px;
      padding: 10px 20px;
      cursor: pointer;
    }

    .action-btn:hover {
      background: var(--terminal-green);
      color: var(--terminal-bg);
    }
  `]
})
export class CaseReportComponent implements OnInit {
  caseData: CaseWithProgress | null = null;
  suspects: Suspect[] = [];
  discoveredEvidence: Evidence[] = [];
  result: SolveResult | null = null;
  loading = true;
  phase: 'form' | 'processing' | 'results' = 'form';
  showSolution = false;

  // Form fields
  accusedSuspectId = 0;
  motive = '';
  method = '';
  selectedEvidenceIds: number[] = [];
  timeline = '';

  // Processing animation
  processingLines: string[] = [];
  private processingSteps = [
    'PROCESSING CASE REPORT...',
    'CROSS-REFERENCING EVIDENCE...',
    'ANALYZING SUSPECT PROFILE...',
    'VALIDATING TIMELINE...',
    'COMPUTING ACCURACY SCORE...',
    'GENERATING VERDICT...',
  ];

  private caseId!: number;

  constructor(
    private caseService: CaseService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.caseId = Number(this.route.snapshot.paramMap.get('caseId'));
    this.loadData();
  }

  private loadData(): void {
    this.caseService.getCase(this.caseId).subscribe({
      next: (data) => {
        this.caseData = data;
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });

    this.caseService.getSuspects(this.caseId).subscribe({
      next: (suspects) => this.suspects = suspects
    });

    this.caseService.getEvidence(this.caseId).subscribe({
      next: (evidence) => this.discoveredEvidence = evidence.filter(e => e.discovered)
    });
  }

  toggleEvidence(id: number): void {
    const idx = this.selectedEvidenceIds.indexOf(id);
    if (idx >= 0) {
      this.selectedEvidenceIds.splice(idx, 1);
    } else {
      this.selectedEvidenceIds.push(id);
    }
  }

  canSubmit(): boolean {
    return this.accusedSuspectId > 0 && this.motive.trim().length > 0 && this.method.trim().length > 0;
  }

  submitReport(): void {
    if (!this.canSubmit()) return;

    this.phase = 'processing';
    this.animateProcessing();
  }

  private animateProcessing(): void {
    let i = 0;
    const interval = setInterval(() => {
      if (i < this.processingSteps.length) {
        this.processingLines.push(this.processingSteps[i]);
        i++;
      } else {
        clearInterval(interval);
        this.doSubmit();
      }
    }, 800);
  }

  private doSubmit(): void {
    this.caseService.solveCase(this.caseId, {
      accusedSuspectId: this.accusedSuspectId,
      motive: this.motive,
      method: this.method,
      keyEvidenceIds: this.selectedEvidenceIds,
      timelineOfEvents: this.timeline,
    }).subscribe({
      next: (result) => {
        this.result = result;
        this.phase = 'results';
      },
      error: () => {
        this.processingLines.push('ERROR: SCORING SYSTEM UNAVAILABLE');
      }
    });
  }

  getRankAscii(rank: string): string {
    return RANK_ASCII[rank] || RANK_ASCII['ROOKIE'] || '';
  }

  returnToTerminal(): void {
    this.router.navigate(['/terminal']);
  }

  browseCases(): void {
    this.router.navigate(['/terminal/cases']);
  }

  goBack(): void {
    this.router.navigate(['/terminal/cases', this.caseId]);
  }
}
