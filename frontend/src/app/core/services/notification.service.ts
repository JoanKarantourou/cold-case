import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import * as signalR from '@microsoft/signalr';
import { AuthService } from './auth.service';

export interface Notification {
  id: number;
  type: 'evidence' | 'forensics' | 'system';
  message: string;
  data?: any;
  timestamp: Date;
}

@Injectable({ providedIn: 'root' })
export class NotificationService implements OnDestroy {
  private connection: signalR.HubConnection | null = null;
  private notificationsSubject = new BehaviorSubject<Notification[]>([]);
  private newNotification$ = new Subject<Notification>();
  private nextId = 1;

  notifications$ = this.notificationsSubject.asObservable();
  onNotification$ = this.newNotification$.asObservable();

  constructor(private authService: AuthService) {
    this.authService.isAuthenticated$.subscribe(isAuth => {
      if (isAuth) {
        this.connect();
      } else {
        this.disconnect();
      }
    });
  }

  ngOnDestroy(): void {
    this.disconnect();
  }

  private connect(): void {
    if (this.connection) return;

    const token = this.authService.token;
    if (!token) return;

    this.connection = new signalR.HubConnectionBuilder()
      .withUrl('/hubs/investigation', {
        accessTokenFactory: () => token
      })
      .withAutomaticReconnect()
      .build();

    this.connection.on('EvidenceDiscovered', (data: any) => {
      this.addNotification({
        type: 'evidence',
        message: `NEW EVIDENCE DISCOVERED: ${data.title} — Check your evidence locker.`,
        data,
      });
    });

    this.connection.on('ForensicsComplete', (data: any) => {
      this.addNotification({
        type: 'forensics',
        message: `Forensic analysis complete for EVIDENCE #${data.evidenceId}. [VIEW RESULTS]`,
        data,
      });
    });

    this.connection.on('SystemAlert', (data: any) => {
      this.addNotification({
        type: 'system',
        message: data.message,
        data,
      });
    });

    this.connection.start().catch(err => {
      console.warn('SignalR connection failed (non-critical):', err);
      this.connection = null;
    });
  }

  private disconnect(): void {
    if (this.connection) {
      this.connection.stop();
      this.connection = null;
    }
  }

  private addNotification(partial: Omit<Notification, 'id' | 'timestamp'>): void {
    const notification: Notification = {
      ...partial,
      id: this.nextId++,
      timestamp: new Date(),
    };
    const current = this.notificationsSubject.value;
    this.notificationsSubject.next([notification, ...current].slice(0, 50));
    this.newNotification$.next(notification);
  }

  dismissNotification(id: number): void {
    const current = this.notificationsSubject.value;
    this.notificationsSubject.next(current.filter(n => n.id !== id));
  }

  clearAll(): void {
    this.notificationsSubject.next([]);
  }
}
