import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-terminal-text',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="terminal-line">{{ displayedText }}</span>
    <span *ngIf="showCursor && isTyping" class="blinking-cursor"></span>
  `,
  styles: [`
    :host { display: inline; }
  `]
})
export class TerminalTextComponent implements OnInit, OnDestroy {
  @Input() text = '';
  @Input() speed = 40;
  @Input() showCursor = false;

  displayedText = '';
  isTyping = true;

  private charIndex = 0;
  private intervalId: any;

  ngOnInit(): void {
    this.startTyping();
  }

  ngOnDestroy(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }

  private startTyping(): void {
    this.intervalId = setInterval(() => {
      if (this.charIndex < this.text.length) {
        this.displayedText += this.text[this.charIndex];
        this.charIndex++;
      } else {
        this.isTyping = false;
        clearInterval(this.intervalId);
      }
    }, this.speed);
  }
}
