import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import {
  CaseService,
  Evidence,
  ForensicStatusResult,
} from '../../core/services/case.service';
import { NotificationService } from '../../core/services/notification.service';
import { Subscription, interval } from 'rxjs';

const ANALYSIS_TYPE_MAP: Record<string, string[]> = {
  PHYSICAL: ['FINGERPRINT', 'DNA', 'BALLISTIC'],
  FORENSIC: ['DNA', 'TOXICOLOGY', 'FINGERPRINT'],
  DOCUMENTARY: ['FINGERPRINT', 'DIGITAL'],
  TESTIMONIAL: ['DIGITAL'],
};

@Component({
  selector: 'app-forensics-lab',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="crt-container crt-flicker">
      <div class="forensics-screen">

        <div class="header-section">
          <div class="terminal-line amber">> FORENSICS LABORATORY — CASE #{{ caseId }}</div>
          <div class="terminal-line amber">═══════════════════════════════════════</div>
        </div>

        <!-- Available Evidence -->
        <div class="section" *ngIf="!viewingResult">
          <div class="terminal-line dim">> SELECT EVIDENCE FOR ANALYSIS:</div>
          <div class="evidence-list">
            <div *ngFor="let ev of discoveredEvidence; let i = index" class="evidence-row">
              <span class="ev-index">[{{ i + 1 }}]</span>
              <span class="ev-title">{{ ev.title }}</span>
              <span class="ev-type">({{ ev.type }})</span>
              <span class="ev-actions">
                — Available:
                <button *ngFor="let at of getAnalysisTypes(ev.type)"
                        class="analysis-btn"
                        [disabled]="isSubmitting"
                        (click)="submitAnalysis(ev, at)">
                  [{{ at }}]
                </button>
              </span>
            </div>
            <div *ngIf="discoveredEvidence.length === 0" class="terminal-line dim">
              > NO DISCOVERED EVIDENCE AVAILABLE FOR ANALYSIS
            </div>
          </div>
        </div>

        <!-- Pending & Complete Analyses -->
        <div class="section" *ngIf="!viewingResult">
          <div class="terminal-line dim">> ANALYSIS REQUESTS:</div>
          <div class="requests-list">
            <div *ngFor="let req of forensicRequests" class="request-row"
                 [class.complete]="req.status === 'COMPLETE'"
                 [class.processing]="req.status === 'PROCESSING'">
              <span class="req-id">Request #F-{{ req.requestId | number:'3.0-0' }}:</span>
              <span class="req-desc">{{ getEvidenceTitle(req.evidenceId) }} — {{ req.analysisType }}</span>
              <span class="req-status" *ngIf="req.status === 'PROCESSING'">
                [PROCESSING {{ getProgressBar(req) }}]
              </span>
              <span class="req-status complete" *ngIf="req.status === 'COMPLETE'">
                [COMPLETE]
                <button class="view-btn" (click)="viewResult(req)">[VIEW RESULTS]</button>
              </span>
            </div>
            <div *ngIf="forensicRequests.length === 0" class="terminal-line dim">
              > NO PENDING ANALYSES
            </div>
          </div>
        </div>

        <!-- Viewing Result -->
        <div class="section result-view" *ngIf="viewingResult">
          <div class="terminal-line amber">> FORENSIC REPORT — REQUEST #F-{{ viewingResult.requestId | number:'3.0-0' }}</div>
          <div class="report-content">{{ viewingResult.result }}</div>
          <button class="back-section-btn" (click)="viewingResult = null">[ CLOSE REPORT ]</button>
        </div>

        <!-- Footer -->
        <div class="footer-section">
          <button class="back-btn" (click)="goBack()">&lt; RETURN TO INVESTIGATION</button>
        </div>
      </div>

      <div *ngIf="loading" class="loading-screen">
        <div class="terminal-line dim">> INITIALIZING FORENSICS LABORATORY...</div>
      </div>
    </div>
  `,
  styles: [`
    .forensics-screen {
      padding: 40px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .loading-screen {
      padding: 40px;
      min-height: 100vh;
    }

    .terminal-line {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 14px;
      margin-bottom: 2px;
    }

    .amber { color: var(--terminal-amber); }
    .dim { color: var(--terminal-dim); }

    .section {
      margin-top: 8px;
    }

    .evidence-list, .requests-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-top: 8px;
    }

    .evidence-row {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 13px;
      padding: 8px 12px;
      border: 1px solid #222;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      max-width: 800px;
    }

    .ev-index {
      color: var(--terminal-blue, #00aaff);
      min-width: 30px;
    }

    .ev-title {
      color: var(--terminal-green);
      font-weight: bold;
    }

    .ev-type {
      color: var(--terminal-dim);
      font-size: 12px;
    }

    .ev-actions {
      color: var(--terminal-dim);
      font-size: 12px;
    }

    .analysis-btn {
      background: transparent;
      border: 1px solid var(--terminal-dim);
      color: var(--terminal-green);
      font-family: var(--terminal-font);
      font-size: 12px;
      padding: 2px 8px;
      margin-left: 4px;
      cursor: pointer;
    }

    .analysis-btn:hover:not(:disabled) {
      border-color: var(--terminal-amber);
      color: var(--terminal-amber);
    }

    .analysis-btn:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    .request-row {
      font-family: var(--terminal-font);
      font-size: 13px;
      padding: 8px 12px;
      border: 1px solid #222;
      max-width: 800px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }

    .request-row.processing {
      border-color: var(--terminal-amber);
    }

    .request-row.complete {
      border-color: var(--terminal-green);
    }

    .req-id {
      color: var(--terminal-blue, #00aaff);
      min-width: 120px;
    }

    .req-desc {
      color: var(--terminal-dim);
      flex: 1;
    }

    .req-status {
      color: var(--terminal-amber);
      font-size: 12px;
    }

    .req-status.complete {
      color: var(--terminal-green);
    }

    .view-btn {
      background: transparent;
      border: 1px solid var(--terminal-green);
      color: var(--terminal-green);
      font-family: var(--terminal-font);
      font-size: 12px;
      padding: 2px 8px;
      margin-left: 8px;
      cursor: pointer;
    }

    .view-btn:hover {
      background: var(--terminal-green);
      color: var(--terminal-bg);
    }

    .result-view {
      flex: 1;
    }

    .report-content {
      font-family: var(--terminal-font);
      color: #00cc33;
      font-size: 13px;
      line-height: 1.6;
      white-space: pre-wrap;
      padding: 16px;
      border: 1px solid var(--terminal-dim);
      margin-top: 12px;
      max-width: 800px;
    }

    .back-section-btn {
      background: transparent;
      border: 1px solid var(--terminal-dim);
      color: var(--terminal-dim);
      font-family: var(--terminal-font);
      font-size: 13px;
      padding: 6px 14px;
      cursor: pointer;
      margin-top: 12px;
    }

    .back-section-btn:hover {
      border-color: var(--terminal-green);
      color: var(--terminal-green);
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
export class ForensicsLabComponent implements OnInit, OnDestroy {
  caseId!: number;
  discoveredEvidence: Evidence[] = [];
  forensicRequests: ForensicStatusResult[] = [];
  viewingResult: ForensicStatusResult | null = null;
  loading = true;
  isSubmitting = false;

  private pollSub: Subscription | null = null;

  constructor(
    private caseService: CaseService,
    private notificationService: NotificationService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.caseId = Number(this.route.snapshot.paramMap.get('caseId'));
    this.loadData();

    // Poll every 5 seconds for forensic request updates
    this.pollSub = interval(5000).subscribe(() => {
      this.refreshRequests();
    });
  }

  ngOnDestroy(): void {
    this.pollSub?.unsubscribe();
  }

  private loadData(): void {
    this.caseService.getEvidence(this.caseId).subscribe({
      next: (evidence) => {
        this.discoveredEvidence = evidence.filter(e => e.discovered);
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });

    this.refreshRequests();
  }

  private refreshRequests(): void {
    this.caseService.getForensicRequests(this.caseId).subscribe({
      next: (requests) => {
        // Check for newly completed requests
        for (const req of requests) {
          const existing = this.forensicRequests.find(r => r.requestId === req.requestId);
          if (existing?.status === 'PROCESSING' && req.status === 'COMPLETE') {
            // Newly completed
          }
        }
        this.forensicRequests = requests;
      }
    });
  }

  getAnalysisTypes(evidenceType: string): string[] {
    return ANALYSIS_TYPE_MAP[evidenceType] || ['FINGERPRINT', 'DIGITAL'];
  }

  submitAnalysis(evidence: Evidence, analysisType: string): void {
    this.isSubmitting = true;
    this.caseService.submitForensics(this.caseId, evidence.id, analysisType).subscribe({
      next: (result) => {
        this.isSubmitting = false;
        this.forensicRequests.push({
          requestId: result.requestId,
          evidenceId: evidence.id,
          analysisType: result.analysisType,
          status: result.status,
          estimatedTimeSeconds: result.estimatedTimeSeconds,
          result: null,
          createdAt: new Date().toISOString(),
          completedAt: null,
        });
      },
      error: () => { this.isSubmitting = false; }
    });
  }

  getEvidenceTitle(evidenceId: number): string {
    const ev = this.discoveredEvidence.find(e => e.id === evidenceId);
    return ev?.title || `Evidence #${evidenceId}`;
  }

  getProgressBar(req: ForensicStatusResult): string {
    if (!req.createdAt) return '████░░░░';
    const elapsed = (Date.now() - new Date(req.createdAt).getTime()) / 1000;
    const ratio = Math.min(elapsed / req.estimatedTimeSeconds, 0.95);
    const filled = Math.round(ratio * 8);
    const empty = 8 - filled;
    const pct = Math.round(ratio * 100);
    return '█'.repeat(filled) + '░'.repeat(empty) + ` ${pct}%`;
  }

  viewResult(req: ForensicStatusResult): void {
    if (req.status === 'COMPLETE' && req.result) {
      this.viewingResult = req;
    }
  }

  goBack(): void {
    this.router.navigate(['/terminal/cases', this.caseId]);
  }
}
