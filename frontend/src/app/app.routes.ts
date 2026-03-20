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
  {
    path: 'terminal/cases/:caseId/interrogate/:suspectId',
    canActivate: [authGuard],
    loadComponent: () => import('./features/interrogation/interrogation.component').then(m => m.InterrogationComponent)
  },
  {
    path: 'terminal/cases/:caseId/evidence-board',
    canActivate: [authGuard],
    loadComponent: () => import('./features/evidence-board/evidence-board.component').then(m => m.EvidenceBoardComponent)
  },
  {
    path: 'terminal/cases/:caseId/forensics',
    canActivate: [authGuard],
    loadComponent: () => import('./features/forensics-lab/forensics-lab.component').then(m => m.ForensicsLabComponent)
  },
  {
    path: 'terminal/cases/:caseId/report',
    canActivate: [authGuard],
    loadComponent: () => import('./features/case-report/case-report.component').then(m => m.CaseReportComponent)
  },
  { path: '**', redirectTo: '' }
];
