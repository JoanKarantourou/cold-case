import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService, Agent } from '../../core/services/auth.service';

@Component({
  selector: 'app-terminal-hub',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="crt-container crt-flicker">
      <div class="hub-screen">
        <div class="header-section">
          <div class="terminal-line system-line">COLD CASE DATABASE — MAIN TERMINAL</div>
          <div class="terminal-line system-line">═══════════════════════════════════════════════════</div>
        </div>

        <div *ngIf="agent" class="agent-info">
          <div class="terminal-line">&gt; AGENT: {{ agent.username.toUpperCase() }} | RANK: {{ agent.rank }} | CASES SOLVED: {{ agent.casesCompleted }}</div>
          <div class="terminal-line dim">&gt; SESSION ACTIVE — SECURE CONNECTION ESTABLISHED</div>
        </div>

        <div class="commands-section">
          <div class="terminal-line">&gt; AVAILABLE COMMANDS:</div>
          <div class="command-grid">
            <button class="terminal-btn" (click)="navigate('/terminal/cases')">
              <span class="btn-icon">📁</span>
              <span class="btn-label">BROWSE CASES</span>
              <span class="btn-desc">Access cold case database</span>
            </button>
            <button class="terminal-btn" disabled>
              <span class="btn-icon">🔍</span>
              <span class="btn-label">ACTIVE INVESTIGATIONS</span>
              <span class="btn-desc">View ongoing cases</span>
            </button>
            <button class="terminal-btn" (click)="navigate('/terminal/mood')">
              <span class="btn-icon">🎭</span>
              <span class="btn-label">MOOD MATCHER</span>
              <span class="btn-desc">Match cases by image or mood</span>
            </button>
            <button class="terminal-btn" disabled>
              <span class="btn-icon">👤</span>
              <span class="btn-label">AGENT PROFILE</span>
              <span class="btn-desc">View agent dossier</span>
            </button>
          </div>
        </div>

        <div class="footer-section">
          <div class="terminal-line dim">&gt; TYPE A COMMAND OR SELECT AN OPTION ABOVE</div>
          <div class="terminal-line dim">&gt; <span class="logout-link" (click)="logout()">[ DISCONNECT ]</span></div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .hub-screen {
      padding: 40px;
      height: 100vh;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    .terminal-line {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 18px;
      margin-bottom: 4px;
      white-space: pre-wrap;
    }

    .system-line {
      color: var(--terminal-amber);
    }

    .dim {
      color: var(--terminal-dim);
    }

    .commands-section {
      margin-top: 16px;
    }

    .command-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-top: 16px;
      max-width: 700px;
    }

    .terminal-btn {
      background: transparent;
      border: 1px solid var(--terminal-green);
      color: var(--terminal-green);
      font-family: var(--terminal-font);
      padding: 16px;
      cursor: pointer;
      text-align: left;
      transition: all 0.2s;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .terminal-btn:hover:not(:disabled) {
      background: var(--terminal-green);
      color: var(--terminal-bg);
    }

    .terminal-btn:disabled {
      border-color: var(--terminal-dim);
      color: var(--terminal-dim);
      cursor: not-allowed;
    }

    .btn-icon {
      font-size: 20px;
    }

    .btn-label {
      font-size: 16px;
      font-weight: bold;
    }

    .btn-desc {
      font-size: 12px;
      opacity: 0.7;
    }

    .footer-section {
      margin-top: auto;
    }

    .logout-link {
      cursor: pointer;
      color: var(--terminal-red);
    }

    .logout-link:hover {
      text-decoration: underline;
    }
  `]
})
export class TerminalHubComponent implements OnInit {
  agent: Agent | null = null;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.agent = this.authService.currentAgent;
    if (!this.agent) {
      this.authService.fetchCurrentAgent().subscribe({
        next: (agent) => this.agent = agent,
        error: () => this.router.navigate(['/login'])
      });
    }
  }

  navigate(path: string): void {
    this.router.navigate([path]);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
