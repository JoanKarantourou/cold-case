import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import {
  CaseService,
  CaseWithProgress,
  CaseFile,
  CaseFileDetail,
  Suspect,
  Evidence,
  Victim,
} from '../../core/services/case.service';

type InvestigationTab = 'files' | 'suspects' | 'evidence' | 'interrogate' | 'forensics' | 'report';

@Component({
  selector: 'app-investigation',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="crt-container crt-flicker">
      <div class="investigation-screen" *ngIf="caseData">
        <div class="header-section">
          <div class="terminal-line amber">
            > {{ caseData.case.caseNumber }} — {{ caseData.case.title.toUpperCase() }}
            — STATUS: {{ caseData.progress?.status || 'NOT STARTED' }}
          </div>
          <div class="terminal-line amber">═══════════════════════════════════════════════════</div>
        </div>

        <div class="tab-bar">
          <button *ngFor="let tab of tabs"
                  class="tab-btn"
                  [class.active]="activeTab === tab.id"
                  [class.disabled]="tab.disabled"
                  [disabled]="tab.disabled"
                  (click)="setTab(tab.id)">
            [ {{ tab.label }} ]
          </button>
        </div>

        <div *ngIf="!caseData.progress" class="start-section">
          <div class="terminal-line">> THIS CASE HAS NOT BEEN OPENED.</div>
          <button class="start-btn" (click)="startCase()">[ BEGIN INVESTIGATION ]</button>
        </div>

        <!-- CASE FILES TAB -->
        <div *ngIf="activeTab === 'files' && caseData.progress" class="tab-content">
          <div class="terminal-line dim">> CASE FILES — {{ caseFiles.length }} DOCUMENTS AVAILABLE</div>
          <div class="file-list">
            <div *ngFor="let file of caseFiles"
                 class="file-item"
                 (click)="openFile(file)">
              <span class="file-type">[{{ file.type }}]</span>
              <span class="file-title">{{ file.title }}</span>
              <span class="file-level">{{ file.classificationLevel }}</span>
            </div>
          </div>
          <div *ngIf="openedFile" class="document-view">
            <div class="doc-header">
              <span class="doc-title">{{ openedFile.title }}</span>
              <button class="close-btn" (click)="closeFile()">[ CLOSE ]</button>
            </div>
            <div class="doc-content">{{ openedFile.content }}</div>
          </div>
        </div>

        <!-- SUSPECTS TAB -->
        <div *ngIf="activeTab === 'suspects' && caseData.progress" class="tab-content">
          <div class="terminal-line dim">> PERSONS OF INTEREST — {{ suspects.length }} IDENTIFIED</div>
          <div class="suspect-list">
            <div *ngFor="let suspect of suspects" class="suspect-card">
              <div class="suspect-ascii">
                ┌─────────┐
                │  ◉   ◉  │
                │    ▽    │
                │  ╰───╯  │
                └─────────┘
              </div>
              <div class="suspect-info">
                <div class="suspect-name">{{ suspect.name.toUpperCase() }}</div>
                <div class="suspect-detail">AGE: {{ suspect.age }} | {{ suspect.occupation.toUpperCase() }}</div>
                <div class="suspect-detail">RELATION: {{ suspect.relationshipToVictim }}</div>
                <div class="suspect-detail">ALIBI: {{ suspect.alibi }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- EVIDENCE TAB -->
        <div *ngIf="activeTab === 'evidence' && caseData.progress" class="tab-content">
          <div class="terminal-line dim">> EVIDENCE LOCKER — {{ evidence.length }} ITEMS CATALOGUED</div>
          <div class="evidence-list">
            <div *ngFor="let item of evidence" class="evidence-item" [class.redacted]="!item.discovered">
              <span class="evidence-type">[{{ item.type }}]</span>
              <span class="evidence-title">{{ item.title }}</span>
              <div class="evidence-desc">{{ item.description }}</div>
            </div>
          </div>
        </div>

        <!-- DISABLED TABS -->
        <div *ngIf="(activeTab === 'interrogate' || activeTab === 'forensics' || activeTab === 'report') && caseData.progress"
             class="tab-content">
          <div class="terminal-line dim">> MODULE NOT YET AVAILABLE. CHECK BACK AFTER SYSTEM UPGRADE.</div>
        </div>

        <!-- VICTIMS INFO -->
        <div *ngIf="caseData.progress && activeTab === 'files' && victims.length > 0 && !openedFile" class="victim-section">
          <div class="terminal-line dim">> VICTIM PROFILE:</div>
          <div *ngFor="let victim of victims" class="victim-card">
            <div class="terminal-line">{{ victim.name.toUpperCase() }}, AGE {{ victim.age }}</div>
            <div class="terminal-line dim">OCCUPATION: {{ victim.occupation }}</div>
            <div class="terminal-line dim">CAUSE OF DEATH: {{ victim.causeOfDeath }}</div>
            <div class="terminal-line dim">{{ victim.background }}</div>
          </div>
        </div>

        <div class="footer-section">
          <button class="back-btn" (click)="goBack()">&lt; RETURN TO CASE BROWSER</button>
        </div>
      </div>

      <div *ngIf="!caseData && !loading" class="error-screen">
        <div class="terminal-line amber">> ERROR: CASE NOT FOUND IN DATABASE.</div>
        <button class="back-btn" (click)="goBack()">&lt; RETURN TO CASE BROWSER</button>
      </div>

      <div *ngIf="loading" class="loading-screen">
        <div class="terminal-line dim">> LOADING CASE FILE...</div>
      </div>
    </div>
  `,
  styles: [`
    .investigation-screen, .error-screen, .loading-screen {
      padding: 40px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .terminal-line {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 15px;
      margin-bottom: 2px;
      white-space: pre-wrap;
    }

    .amber { color: var(--terminal-amber); }
    .dim { color: var(--terminal-dim); }

    .tab-bar {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin: 8px 0;
    }

    .tab-btn {
      background: transparent;
      border: none;
      color: var(--terminal-dim);
      font-family: var(--terminal-font);
      font-size: 14px;
      cursor: pointer;
      padding: 4px 8px;
    }

    .tab-btn:hover:not(:disabled), .tab-btn.active {
      color: var(--terminal-green);
    }

    .tab-btn.disabled {
      color: #333;
      cursor: not-allowed;
    }

    .tab-content {
      flex: 1;
      overflow-y: auto;
    }

    .start-section {
      display: flex;
      flex-direction: column;
      gap: 12px;
      align-items: flex-start;
    }

    .start-btn {
      background: transparent;
      border: 1px solid var(--terminal-amber);
      color: var(--terminal-amber);
      font-family: var(--terminal-font);
      font-size: 16px;
      padding: 12px 24px;
      cursor: pointer;
    }

    .start-btn:hover {
      background: var(--terminal-amber);
      color: var(--terminal-bg);
    }

    /* Case Files */
    .file-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin: 8px 0;
    }

    .file-item {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 14px;
      cursor: pointer;
      padding: 6px 8px;
      display: flex;
      gap: 12px;
    }

    .file-item:hover {
      background: rgba(0, 255, 65, 0.05);
    }

    .file-type {
      color: var(--terminal-blue);
      min-width: 180px;
    }

    .file-title { flex: 1; }

    .file-level {
      color: var(--terminal-dim);
      font-size: 12px;
    }

    .document-view {
      border: 1px solid var(--terminal-dim);
      padding: 20px;
      margin-top: 16px;
      max-width: 750px;
    }

    .doc-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 16px;
    }

    .doc-title {
      font-family: var(--terminal-font);
      color: var(--terminal-amber);
      font-size: 14px;
      font-weight: bold;
    }

    .close-btn {
      background: transparent;
      border: none;
      color: var(--terminal-dim);
      font-family: var(--terminal-font);
      cursor: pointer;
      font-size: 12px;
    }

    .close-btn:hover { color: var(--terminal-red); }

    .doc-content {
      font-family: var(--terminal-font);
      color: #00cc33;
      font-size: 13px;
      line-height: 1.6;
      white-space: pre-wrap;
    }

    /* Suspects */
    .suspect-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin: 8px 0;
    }

    .suspect-card {
      display: flex;
      gap: 20px;
      border: 1px solid var(--terminal-dim);
      padding: 16px;
      max-width: 750px;
    }

    .suspect-ascii {
      font-family: var(--terminal-font);
      color: var(--terminal-dim);
      font-size: 12px;
      white-space: pre;
      line-height: 1.2;
    }

    .suspect-info {
      flex: 1;
    }

    .suspect-name {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 16px;
      font-weight: bold;
      margin-bottom: 4px;
    }

    .suspect-detail {
      font-family: var(--terminal-font);
      color: var(--terminal-dim);
      font-size: 13px;
      margin-bottom: 2px;
    }

    /* Evidence */
    .evidence-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin: 8px 0;
    }

    .evidence-item {
      border: 1px solid var(--terminal-dim);
      padding: 12px;
      max-width: 750px;
    }

    .evidence-item.redacted {
      opacity: 0.5;
    }

    .evidence-type {
      font-family: var(--terminal-font);
      color: var(--terminal-blue);
      font-size: 12px;
      margin-right: 8px;
    }

    .evidence-title {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 14px;
      font-weight: bold;
    }

    .evidence-desc {
      font-family: var(--terminal-font);
      color: var(--terminal-dim);
      font-size: 13px;
      margin-top: 4px;
    }

    /* Victims */
    .victim-section {
      margin-top: 16px;
      border-top: 1px solid var(--terminal-dim);
      padding-top: 12px;
    }

    .victim-card {
      margin: 4px 0;
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
export class InvestigationComponent implements OnInit {
  caseData: CaseWithProgress | null = null;
  caseFiles: CaseFile[] = [];
  suspects: Suspect[] = [];
  evidence: Evidence[] = [];
  victims: Victim[] = [];
  openedFile: CaseFileDetail | null = null;
  loading = true;
  activeTab: InvestigationTab = 'files';

  tabs = [
    { id: 'files' as InvestigationTab, label: 'CASE FILES', disabled: false },
    { id: 'suspects' as InvestigationTab, label: 'SUSPECTS', disabled: false },
    { id: 'evidence' as InvestigationTab, label: 'EVIDENCE', disabled: false },
    { id: 'interrogate' as InvestigationTab, label: 'INTERROGATE', disabled: true },
    { id: 'forensics' as InvestigationTab, label: 'FORENSICS LAB', disabled: true },
    { id: 'report' as InvestigationTab, label: 'FILE REPORT', disabled: true },
  ];

  private caseId!: number;

  constructor(
    private caseService: CaseService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.caseId = Number(this.route.snapshot.paramMap.get('caseId'));
    this.loadCase();
  }

  private loadCase(): void {
    this.caseService.getCase(this.caseId).subscribe({
      next: (data) => {
        this.caseData = data;
        this.loading = false;
        if (data.progress) {
          this.loadCaseDetails();
        }
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  private loadCaseDetails(): void {
    this.caseService.getCaseFiles(this.caseId).subscribe(files => this.caseFiles = files);
    this.caseService.getSuspects(this.caseId).subscribe(suspects => this.suspects = suspects);
    this.caseService.getEvidence(this.caseId).subscribe(evidence => this.evidence = evidence);
    this.caseService.getVictims(this.caseId).subscribe(victims => this.victims = victims);
  }

  startCase(): void {
    this.caseService.startCase(this.caseId).subscribe({
      next: (progress) => {
        if (this.caseData) {
          this.caseData.progress = progress;
          this.loadCaseDetails();
        }
      },
      error: () => {}
    });
  }

  setTab(tab: InvestigationTab): void {
    this.activeTab = tab;
    this.openedFile = null;
  }

  openFile(file: CaseFile): void {
    this.caseService.getCaseFile(this.caseId, file.id).subscribe({
      next: (detail) => this.openedFile = detail
    });
  }

  closeFile(): void {
    this.openedFile = null;
  }

  goBack(): void {
    this.router.navigate(['/terminal/cases']);
  }
}
