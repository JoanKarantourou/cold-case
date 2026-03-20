import { Routes } from '@angular/router';
import { BootSequenceComponent } from './features/boot-sequence/boot-sequence.component';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', component: BootSequenceComponent },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/auth.component').then(m => m.AuthComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/auth.component').then(m => m.AuthComponent)
  },
  {
    path: 'terminal',
    canActivate: [authGuard],
    loadComponent: () => import('./features/terminal-hub/terminal-hub.component').then(m => m.TerminalHubComponent)
  },
  {
    path: 'terminal/cases',
    canActivate: [authGuard],
    loadComponent: () => import('./features/case-browser/case-browser.component').then(m => m.CaseBrowserComponent)
  },
  {
    path: 'terminal/cases/:caseId',
    canActivate: [authGuard],
    loadComponent: () => import('./features/investigation/investigation.component').then(m => m.InvestigationComponent)
  },
  { path: '**', redirectTo: '' }
];
