import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { Subscription } from 'rxjs';

type AuthMode = 'select' | 'register' | 'login';
type RegisterStep = 'username' | 'email' | 'password' | 'confirm' | 'submitting';
type LoginStep = 'email' | 'password' | 'submitting';

interface TerminalLine {
  text: string;
  type: 'system' | 'input' | 'error' | 'success';
}

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="crt-container crt-flicker">
      <div class="auth-screen">
        <div *ngFor="let line of lines" class="terminal-line" [ngClass]="'line-' + line.type">
          {{ line.text }}
        </div>

        <!-- Mode Selection -->
        <div *ngIf="mode === 'select'" class="auth-select">
          <div class="terminal-line line-system">&gt; AGENT IDENTIFICATION REQUIRED</div>
          <div class="terminal-line line-system">&gt; SELECT:</div>
          <div class="auth-buttons">
            <button class="terminal-btn" (click)="selectMode('register')">[ NEW AGENT REGISTRATION ]</button>
            <button class="terminal-btn" (click)="selectMode('login')">[ EXISTING AGENT LOGIN ]</button>
          </div>
        </div>

        <!-- Register Flow -->
        <div *ngIf="mode === 'register' && registerStep !== 'submitting'" class="auth-input-area">
          <div class="input-line">
            <span class="prompt">&gt; {{ getRegisterPrompt() }}</span>
            <input
              #inputField
              [type]="registerStep === 'password' || registerStep === 'confirm' ? 'password' : 'text'"
              [(ngModel)]="currentInput"
              (keydown.enter)="submitRegisterStep()"
              class="terminal-input"
              autocomplete="off"
              spellcheck="false"
            />
            <span class="blinking-cursor"></span>
          </div>
        </div>

        <!-- Login Flow -->
        <div *ngIf="mode === 'login' && loginStep !== 'submitting'" class="auth-input-area">
          <div class="input-line">
            <span class="prompt">&gt; {{ getLoginPrompt() }}</span>
            <input
              #inputField
              [type]="loginStep === 'password' ? 'password' : 'text'"
              [(ngModel)]="currentInput"
              (keydown.enter)="submitLoginStep()"
              class="terminal-input"
              autocomplete="off"
              spellcheck="false"
            />
            <span class="blinking-cursor"></span>
          </div>
        </div>

        <!-- Loading -->
        <div *ngIf="isSubmitting" class="terminal-line line-system">
          &gt; VERIFYING CREDENTIALS...
        </div>
      </div>
    </div>
  `,
  styles: [`
    .auth-screen {
      padding: 40px;
      height: 100vh;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .terminal-line {
      font-family: var(--terminal-font);
      font-size: 18px;
      margin-bottom: 8px;
      white-space: pre-wrap;
    }

    .line-system { color: var(--terminal-green); }
    .line-input { color: var(--terminal-dim); }
    .line-error { color: var(--terminal-red); }
    .line-success { color: var(--terminal-amber); }

    .auth-select {
      margin-top: 10px;
    }

    .auth-buttons {
      display: flex;
      gap: 20px;
      margin-top: 16px;
    }

    .terminal-btn {
      background: transparent;
      border: 1px solid var(--terminal-green);
      color: var(--terminal-green);
      font-family: var(--terminal-font);
      font-size: 16px;
      padding: 10px 20px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .terminal-btn:hover {
      background: var(--terminal-green);
      color: var(--terminal-bg);
    }

    .auth-input-area {
      margin-top: 10px;
    }

    .input-line {
      display: flex;
      align-items: center;
      font-family: var(--terminal-font);
      font-size: 18px;
      color: var(--terminal-green);
    }

    .prompt {
      white-space: nowrap;
      margin-right: 8px;
    }

    .terminal-input {
      flex: 1;
      background: transparent;
      border: none;
      color: var(--terminal-green);
      font-family: var(--terminal-font);
      font-size: 18px;
      outline: none;
      caret-color: transparent;
    }
  `]
})
export class AuthComponent implements OnInit, OnDestroy {
  mode: AuthMode = 'select';
  registerStep: RegisterStep = 'username';
  loginStep: LoginStep = 'email';
  currentInput = '';
  lines: TerminalLine[] = [];
  isSubmitting = false;

  private registerData = { username: '', email: '', password: '' };
  private loginData = { email: '', password: '' };
  private sub?: Subscription;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.addLine('COLD CASE DATABASE — AGENT AUTHENTICATION SYSTEM', 'system');
    this.addLine('═══════════════════════════════════════════════════', 'system');
  }

  ngOnDestroy(): void {
    this.sub?.unsubscribe();
  }

  selectMode(mode: 'register' | 'login'): void {
    this.mode = mode;
    if (mode === 'register') {
      this.addLine('> INITIATING NEW AGENT REGISTRATION...', 'system');
      this.registerStep = 'username';
    } else {
      this.addLine('> INITIATING AGENT LOGIN...', 'system');
      this.loginStep = 'email';
    }
  }

  getRegisterPrompt(): string {
    switch (this.registerStep) {
      case 'username': return 'ENTER AGENT CODENAME:';
      case 'email': return 'ENTER SECURE EMAIL:';
      case 'password': return 'ENTER ACCESS CODE:';
      case 'confirm': return 'CONFIRM ACCESS CODE:';
      default: return '';
    }
  }

  getLoginPrompt(): string {
    switch (this.loginStep) {
      case 'email': return 'ENTER SECURE EMAIL:';
      case 'password': return 'ENTER ACCESS CODE:';
      default: return '';
    }
  }

  submitRegisterStep(): void {
    const value = this.currentInput.trim();
    if (!value) return;

    switch (this.registerStep) {
      case 'username':
        this.registerData.username = value;
        this.addLine(`> AGENT CODENAME: ${value}`, 'input');
        this.currentInput = '';
        this.registerStep = 'email';
        break;

      case 'email':
        if (!value.includes('@')) {
          this.addLine('> ERROR: INVALID EMAIL FORMAT', 'error');
          this.currentInput = '';
          return;
        }
        this.registerData.email = value;
        this.addLine(`> SECURE EMAIL: ${value}`, 'input');
        this.currentInput = '';
        this.registerStep = 'password';
        break;

      case 'password':
        if (value.length < 6) {
          this.addLine('> ERROR: ACCESS CODE MUST BE AT LEAST 6 CHARACTERS', 'error');
          this.currentInput = '';
          return;
        }
        this.registerData.password = value;
        this.addLine('> ACCESS CODE: ********', 'input');
        this.currentInput = '';
        this.registerStep = 'confirm';
        break;

      case 'confirm':
        if (value !== this.registerData.password) {
          this.addLine('> ERROR: ACCESS CODES DO NOT MATCH', 'error');
          this.currentInput = '';
          return;
        }
        this.addLine('> ACCESS CODE CONFIRMED', 'input');
        this.currentInput = '';
        this.doRegister();
        break;
    }
  }

  submitLoginStep(): void {
    const value = this.currentInput.trim();
    if (!value) return;

    switch (this.loginStep) {
      case 'email':
        this.loginData.email = value;
        this.addLine(`> SECURE EMAIL: ${value}`, 'input');
        this.currentInput = '';
        this.loginStep = 'password';
        break;

      case 'password':
        this.loginData.password = value;
        this.addLine('> ACCESS CODE: ********', 'input');
        this.currentInput = '';
        this.doLogin();
        break;
    }
  }

  private doRegister(): void {
    this.isSubmitting = true;
    this.registerStep = 'submitting';
    this.addLine('> CREATING AGENT PROFILE...', 'system');

    this.sub = this.authService.register(this.registerData).subscribe({
      next: (res) => {
        this.isSubmitting = false;
        this.addLine(`> AGENT REGISTERED SUCCESSFULLY.`, 'success');
        this.addLine(`> IDENTITY VERIFIED. WELCOME, AGENT ${res.agent.username.toUpperCase()}. CLEARANCE LEVEL: ${res.agent.rank}`, 'success');
        setTimeout(() => this.router.navigate(['/terminal']), 1500);
      },
      error: (err) => {
        this.isSubmitting = false;
        const msg = err.error?.message || 'REGISTRATION FAILED. TRY AGAIN.';
        this.addLine(`> ERROR: ${msg.toUpperCase()}`, 'error');
        this.mode = 'select';
        this.registerStep = 'username';
        this.registerData = { username: '', email: '', password: '' };
      }
    });
  }

  private doLogin(): void {
    this.isSubmitting = true;
    this.loginStep = 'submitting';

    this.sub = this.authService.login(this.loginData).subscribe({
      next: (res) => {
        this.isSubmitting = false;
        this.addLine(`> IDENTITY VERIFIED. WELCOME BACK, AGENT ${res.agent.username.toUpperCase()}. CLEARANCE LEVEL: ${res.agent.rank}`, 'success');
        setTimeout(() => this.router.navigate(['/terminal']), 1500);
      },
      error: (err) => {
        this.isSubmitting = false;
        const msg = err.error?.message || 'INVALID CREDENTIALS.';
        this.addLine(`> ERROR: ${msg.toUpperCase()}`, 'error');
        this.mode = 'select';
        this.loginStep = 'email';
        this.loginData = { email: '', password: '' };
      }
    });
  }

  private addLine(text: string, type: TerminalLine['type']): void {
    this.lines.push({ text, type });
  }
}
