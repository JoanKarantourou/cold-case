import { Component, OnInit, OnDestroy, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-boot-sequence',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="crt-container crt-flicker">
      <div class="boot-screen">
        <div *ngFor="let line of displayedLines; let i = index" class="terminal-line">
          <span [class.dim-text]="line.dim">{{ line.text }}</span>
        </div>
        <div *ngIf="showPrompt" class="terminal-line enter-prompt">
          &gt; PRESS [ENTER] TO CONTINUE
          <span class="blinking-cursor"></span>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .boot-screen {
      padding: 40px;
      height: 100vh;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .terminal-line {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 18px;
      margin-bottom: 8px;
      white-space: pre-wrap;
    }

    .dim-text {
      color: var(--terminal-dim);
    }

    .enter-prompt {
      margin-top: 20px;
      animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
  `]
})
export class BootSequenceComponent implements OnInit, OnDestroy {
  private bootLines = [
    { text: 'ESTABLISHING SECURE CONNECTION...', delay: 0, dim: true },
    { text: 'ROUTING THROUGH ENCRYPTED CHANNELS...', delay: 800, dim: true },
    { text: 'CONNECTION ESTABLISHED.', delay: 1600, dim: false },
    { text: 'ACCESSING FEDERAL COLD CASE DATABASE...', delay: 2400, dim: true },
    { text: 'WARNING: UNAUTHORIZED ACCESS DETECTED', delay: 3200, dim: false },
    { text: '...PROCEEDING ANYWAY.', delay: 4000, dim: true },
    { text: '', delay: 4500, dim: false },
    { text: 'WELCOME, AGENT.', delay: 4800, dim: false },
  ];

  displayedLines: { text: string; dim: boolean }[] = [];
  showPrompt = false;

  private timeouts: any[] = [];

  constructor(private router: Router) {}

  ngOnInit(): void {
    this.bootLines.forEach((line, index) => {
      const timeout = setTimeout(() => {
        this.displayedLines.push({ text: line.text, dim: line.dim });
        if (index === this.bootLines.length - 1) {
          const promptTimeout = setTimeout(() => {
            this.showPrompt = true;
          }, 600);
          this.timeouts.push(promptTimeout);
        }
      }, line.delay);
      this.timeouts.push(timeout);
    });
  }

  ngOnDestroy(): void {
    this.timeouts.forEach(t => clearTimeout(t));
  }

  @HostListener('document:keydown.enter')
  onEnter(): void {
    if (this.showPrompt) {
      this.router.navigate(['/terminal']);
    }
  }

  @HostListener('document:click')
  onClick(): void {
    if (this.showPrompt) {
      this.router.navigate(['/terminal']);
    }
  }
}
