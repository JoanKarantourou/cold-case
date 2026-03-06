import { Routes } from '@angular/router';
import { BootSequenceComponent } from './features/boot-sequence/boot-sequence.component';

export const routes: Routes = [
  { path: '', component: BootSequenceComponent },
  { path: 'terminal', loadComponent: () => import('./features/boot-sequence/boot-sequence.component').then(m => m.BootSequenceComponent) },
  { path: '**', redirectTo: '' }
];
