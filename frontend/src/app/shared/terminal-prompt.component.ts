import { Component } from '@angular/core';

@Component({
  selector: 'app-terminal-prompt',
  standalone: true,
  template: `
    <span class="prompt">&gt; </span><span class="blinking-cursor"></span>
  `,
  styles: [`
    :host {
      display: inline-flex;
      align-items: center;
    }
    .prompt {
      color: var(--terminal-green);
      font-family: var(--terminal-font);
    }
  `]
})
export class TerminalPromptComponent {}
