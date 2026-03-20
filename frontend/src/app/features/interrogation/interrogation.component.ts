import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import {
  CaseService,
  Suspect,
  Evidence,
  InterrogationEntry,
  InterrogationMessageResult,
  DiscoveredEvidence,
} from '../../core/services/case.service';

@Component({
  selector: 'app-interrogation',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="crt-container crt-flicker">
      <div class="interrogation-screen" [class.glitch-effect]="showGlitch">

        <!-- Header -->
        <div class="interrogation-header">
          <div class="header-border">
            ╔══════════════════════════════════════════════════════════╗
          </div>
          <div class="header-content">
            ║  INTERROGATION ROOM — RECORDING IN PROGRESS
          </div>
          <div class="header-content">
            ║  SUSPECT: {{ suspectName.toUpperCase() }} | STATUS:
            <span [class]="'state-' + emotionalState.toLowerCase()">{{ emotionalState }}</span>
          </div>
          <div class="header-border">
            ╚══════════════════════════════════════════════════════════╝
          </div>
        </div>

        <!-- Evidence Alert -->
        <div *ngIf="newEvidence.length > 0" class="evidence-alert">
          <div *ngFor="let ev of newEvidence" class="alert-line">
            > ⚠ NEW EVIDENCE DISCOVERED: {{ ev.title }} — Check your evidence locker.
          </div>
        </div>

        <!-- Transcript -->
        <div class="transcript" #transcript>
          <div *ngFor="let entry of history; let i = index"
               class="transcript-entry"
               [class.agent-entry]="entry.role === 'agent'"
               [class.suspect-entry]="entry.role === 'suspect'">
            <span class="timestamp">[{{ getTimestamp(i) }}]</span>
            <span class="speaker">{{ entry.role === 'agent' ? 'AGENT' : suspectName.toUpperCase().split(' ')[1] || suspectName.toUpperCase() }}:</span>
            <span class="message" [class.typewriter]="i === history.length - 1 && entry.role === 'suspect'">{{ entry.content }}</span>
          </div>
          <div *ngIf="isWaiting" class="waiting-indicator">
            <span class="timestamp">[{{ getCurrentTimestamp() }}]</span>
            <span class="speaker">{{ suspectName.toUpperCase().split(' ')[1] || suspectName.toUpperCase() }}:</span>
            <span class="waiting-dots">...</span>
          </div>
        </div>

        <!-- Questioning Approaches -->
        <div class="approaches-section" *ngIf="!showEvidencePanel">
          <div class="approaches-label">> QUESTIONING APPROACHES:</div>
          <div class="approaches-grid">
            <button class="approach-btn" (click)="sendSuggested('Tell me about your alibi. Where exactly were you that night?')">
              [ ASK ABOUT ALIBI ]
            </button>
            <button class="approach-btn" (click)="sendSuggested('That doesn\\'t add up. You\\'re contradicting yourself.')">
              [ PRESS ON CONTRADICTION ]
            </button>
            <button class="approach-btn" (click)="toggleEvidencePanel()">
              [ SHOW EVIDENCE ]
            </button>
            <button class="approach-btn" (click)="sendSuggested('Let\\'s talk about something else. Tell me about your relationship with the victim.')">
              [ CHANGE SUBJECT ]
            </button>
            <button class="approach-btn end-btn" (click)="endInterrogation()">
              [ END INTERROGATION ]
            </button>
          </div>
        </div>

        <!-- Evidence Panel -->
        <div class="evidence-panel" *ngIf="showEvidencePanel">
          <div class="approaches-label">> SELECT EVIDENCE TO PRESENT:</div>
          <div class="evidence-select-list" *ngIf="discoveredEvidence.length > 0">
            <button *ngFor="let ev of discoveredEvidence"
                    class="evidence-select-btn"
                    (click)="presentEvidence(ev)">
              [{{ ev.type }}] {{ ev.title }}
            </button>
          </div>
          <div *ngIf="discoveredEvidence.length === 0" class="terminal-line dim">
            > NO EVIDENCE AVAILABLE TO PRESENT
          </div>
          <button class="approach-btn" (click)="toggleEvidencePanel()">[ CANCEL ]</button>
        </div>

        <!-- Free Text Input -->
        <div class="input-section">
          <span class="input-prompt">> AGENT: </span>
          <input
            #messageInput
            class="terminal-input"
            [(ngModel)]="userMessage"
            (keyup.enter)="sendMessage()"
            [disabled]="isWaiting"
            placeholder="Type your question..."
            autocomplete="off"
          />
        </div>

        <!-- Footer -->
        <div class="footer-section">
          <button class="back-btn" (click)="goBack()">
            &lt; RETURN TO INVESTIGATION
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div *ngIf="loading" class="loading-screen">
        <div class="terminal-line dim">> PREPARING INTERROGATION ROOM...</div>
      </div>
    </div>
  `,
  styles: [`
    .interrogation-screen {
      padding: 30px 40px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .loading-screen {
      padding: 40px;
      min-height: 100vh;
    }

    .terminal-line {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 14px;
    }

    .dim { color: var(--terminal-dim); }

    /* Header */
    .interrogation-header {
      font-family: var(--terminal-font);
      color: var(--terminal-amber);
      font-size: 14px;
      line-height: 1.4;
    }

    .header-border { color: var(--terminal-amber); }
    .header-content {
      color: var(--terminal-amber);
      padding-left: 2px;
    }

    .state-calm { color: #00ff41; }
    .state-nervous { color: #ffff00; }
    .state-agitated { color: #ff8800; }
    .state-defensive { color: #ff4400; }
    .state-breaking { color: #ff0000; font-weight: bold; }

    /* Evidence Alert */
    .evidence-alert {
      border: 1px solid #ff4400;
      padding: 8px 12px;
      background: rgba(255, 68, 0, 0.08);
      animation: alertFlash 0.5s ease-out;
    }

    .alert-line {
      font-family: var(--terminal-font);
      color: #ff8800;
      font-size: 13px;
    }

    @keyframes alertFlash {
      0%, 50% { background: rgba(255, 68, 0, 0.2); }
      100% { background: rgba(255, 68, 0, 0.08); }
    }

    /* Transcript */
    .transcript {
      flex: 1;
      overflow-y: auto;
      max-height: 50vh;
      padding: 12px 0;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .transcript-entry {
      font-family: var(--terminal-font);
      font-size: 14px;
      line-height: 1.5;
      white-space: pre-wrap;
    }

    .agent-entry .speaker { color: var(--terminal-blue, #00aaff); }
    .agent-entry .message { color: var(--terminal-green); }

    .suspect-entry .speaker { color: var(--terminal-amber); }
    .suspect-entry .message { color: #cccccc; }

    .timestamp {
      color: var(--terminal-dim);
      font-size: 12px;
      margin-right: 8px;
    }

    .speaker {
      font-weight: bold;
      margin-right: 8px;
    }

    .waiting-indicator {
      font-family: var(--terminal-font);
      font-size: 14px;
    }

    .waiting-dots {
      color: var(--terminal-dim);
      animation: blink 1s infinite;
    }

    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.3; }
    }

    /* Approaches */
    .approaches-section, .evidence-panel {
      border-top: 1px solid var(--terminal-dim);
      padding-top: 12px;
    }

    .approaches-label {
      font-family: var(--terminal-font);
      color: var(--terminal-dim);
      font-size: 13px;
      margin-bottom: 8px;
    }

    .approaches-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .approach-btn {
      background: transparent;
      border: 1px solid var(--terminal-dim);
      color: var(--terminal-green);
      font-family: var(--terminal-font);
      font-size: 13px;
      padding: 6px 12px;
      cursor: pointer;
    }

    .approach-btn:hover {
      border-color: var(--terminal-green);
      background: rgba(0, 255, 65, 0.05);
    }

    .approach-btn.end-btn {
      color: var(--terminal-amber);
      border-color: var(--terminal-amber);
    }

    .approach-btn.end-btn:hover {
      background: rgba(255, 170, 0, 0.1);
    }

    /* Evidence Select */
    .evidence-select-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-bottom: 12px;
    }

    .evidence-select-btn {
      background: transparent;
      border: 1px solid var(--terminal-dim);
      color: var(--terminal-green);
      font-family: var(--terminal-font);
      font-size: 13px;
      padding: 6px 12px;
      cursor: pointer;
      text-align: left;
    }

    .evidence-select-btn:hover {
      border-color: var(--terminal-blue, #00aaff);
      color: var(--terminal-blue, #00aaff);
    }

    /* Input */
    .input-section {
      display: flex;
      align-items: center;
      border-top: 1px solid var(--terminal-dim);
      padding-top: 12px;
    }

    .input-prompt {
      font-family: var(--terminal-font);
      color: var(--terminal-blue, #00aaff);
      font-size: 14px;
      font-weight: bold;
      white-space: nowrap;
    }

    .terminal-input {
      flex: 1;
      background: transparent;
      border: none;
      color: var(--terminal-green);
      font-family: var(--terminal-font);
      font-size: 14px;
      outline: none;
      caret-color: var(--terminal-green);
    }

    .terminal-input::placeholder {
      color: #333;
    }

    .terminal-input:disabled {
      opacity: 0.5;
    }

    /* Footer */
    .footer-section {
      padding-top: 12px;
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

    /* Glitch Effect */
    .glitch-effect {
      animation: glitch 0.3s ease-out;
    }

    @keyframes glitch {
      0% { transform: translate(2px, -1px) skewX(0.5deg); filter: hue-rotate(90deg); }
      25% { transform: translate(-2px, 1px) skewX(-0.5deg); }
      50% { transform: translate(1px, 0) skewX(0.3deg); filter: hue-rotate(0deg); }
      100% { transform: translate(0) skewX(0); }
    }
  `]
})
export class InterrogationComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('transcript') transcriptEl!: ElementRef;
  @ViewChild('messageInput') messageInput!: ElementRef;

  suspectName = '';
  emotionalState = 'CALM';
  history: InterrogationEntry[] = [];
  userMessage = '';
  isWaiting = false;
  loading = true;
  showEvidencePanel = false;
  showGlitch = false;
  newEvidence: DiscoveredEvidence[] = [];
  discoveredEvidence: Evidence[] = [];

  private caseId!: number;
  private suspectId!: number;
  private suspect: Suspect | null = null;
  private baseTime = new Date();
  private shouldScroll = false;

  constructor(
    private caseService: CaseService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.caseId = Number(this.route.snapshot.paramMap.get('caseId'));
    this.suspectId = Number(this.route.snapshot.paramMap.get('suspectId'));
    this.loadSuspectAndStart();
  }

  ngOnDestroy(): void {
    // Clear evidence alerts
    this.newEvidence = [];
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  private loadSuspectAndStart(): void {
    // Load suspect info
    this.caseService.getSuspects(this.caseId).subscribe({
      next: (suspects) => {
        this.suspect = suspects.find(s => s.id === this.suspectId) || null;
        this.suspectName = this.suspect?.name || 'UNKNOWN';
        this.startInterrogation();
      },
      error: () => {
        this.loading = false;
      }
    });

    // Load discovered evidence for presenting
    this.caseService.getEvidence(this.caseId).subscribe({
      next: (evidence) => {
        this.discoveredEvidence = evidence.filter(e => e.discovered);
      }
    });
  }

  private startInterrogation(): void {
    this.caseService.startInterrogation(this.caseId, this.suspectId).subscribe({
      next: (result) => {
        this.emotionalState = result.emotionalState;
        this.history = result.history || [];
        if (result.openingStatement && this.history.length === 0) {
          this.history.push({ role: 'suspect', content: result.openingStatement });
        }
        this.loading = false;
        this.shouldScroll = true;
        setTimeout(() => this.focusInput(), 100);
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  sendMessage(): void {
    if (!this.userMessage.trim() || this.isWaiting) return;

    const message = this.userMessage.trim();
    this.history.push({ role: 'agent', content: message });
    this.userMessage = '';
    this.isWaiting = true;
    this.shouldScroll = true;

    this.caseService.sendInterrogationMessage(this.caseId, this.suspectId, message).subscribe({
      next: (result) => this.handleResponse(result),
      error: () => {
        this.isWaiting = false;
        this.history.push({
          role: 'suspect',
          content: '[TRANSMISSION ERROR — SUSPECT RESPONSE NOT RECEIVED]'
        });
      }
    });
  }

  sendSuggested(message: string): void {
    if (this.isWaiting) return;
    this.userMessage = message;
    this.sendMessage();
  }

  presentEvidence(ev: Evidence): void {
    if (this.isWaiting) return;

    const message = `I'd like to show you something. Take a look at this: "${ev.title}". Care to explain?`;
    this.history.push({ role: 'agent', content: message });
    this.isWaiting = true;
    this.showEvidencePanel = false;
    this.shouldScroll = true;

    this.caseService.sendInterrogationMessage(
      this.caseId, this.suspectId, message, [ev.id]
    ).subscribe({
      next: (result) => this.handleResponse(result),
      error: () => {
        this.isWaiting = false;
      }
    });
  }

  private handleResponse(result: InterrogationMessageResult): void {
    this.isWaiting = false;
    this.emotionalState = result.emotionalState;
    this.history.push({ role: 'suspect', content: result.response });
    this.shouldScroll = true;

    if (result.evidenceDiscovered && result.evidenceDiscovered.length > 0) {
      this.newEvidence = result.evidenceDiscovered;
      this.triggerGlitch();
      // Refresh discovered evidence list
      this.caseService.getEvidence(this.caseId).subscribe({
        next: (evidence) => {
          this.discoveredEvidence = evidence.filter(e => e.discovered);
        }
      });
      // Clear alert after 8 seconds
      setTimeout(() => { this.newEvidence = []; }, 8000);
    }

    setTimeout(() => this.focusInput(), 100);
  }

  toggleEvidencePanel(): void {
    this.showEvidencePanel = !this.showEvidencePanel;
  }

  endInterrogation(): void {
    this.caseService.endInterrogation(this.caseId, this.suspectId).subscribe({
      next: () => this.goBack(),
      error: () => this.goBack()
    });
  }

  goBack(): void {
    this.router.navigate(['/terminal/cases', this.caseId]);
  }

  getTimestamp(index: number): string {
    const time = new Date(this.baseTime.getTime() + index * 15000);
    return time.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }

  getCurrentTimestamp(): string {
    return this.getTimestamp(this.history.length);
  }

  private scrollToBottom(): void {
    if (this.transcriptEl) {
      const el = this.transcriptEl.nativeElement;
      el.scrollTop = el.scrollHeight;
    }
  }

  private focusInput(): void {
    if (this.messageInput) {
      this.messageInput.nativeElement.focus();
    }
  }

  private triggerGlitch(): void {
    this.showGlitch = true;
    setTimeout(() => { this.showGlitch = false; }, 300);
  }
}
