import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, map } from 'rxjs';

export interface Agent {
  id: string;
  username: string;
  email: string;
  rank: string;
  casesCompleted: number;
}

export interface AuthResponse {
  token: string;
  agent: Agent;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private tokenSubject = new BehaviorSubject<string | null>(null);
  private agentSubject = new BehaviorSubject<Agent | null>(null);

  isAuthenticated$ = this.tokenSubject.pipe(map(token => !!token));
  currentAgent$ = this.agentSubject.asObservable();

  constructor(private http: HttpClient) {}

  get token(): string | null {
    return this.tokenSubject.value;
  }

  get currentAgent(): Agent | null {
    return this.agentSubject.value;
  }

  register(request: RegisterRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/auth/register', request).pipe(
      tap(res => {
        this.tokenSubject.next(res.token);
        this.agentSubject.next(res.agent);
      })
    );
  }

  login(request: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/auth/login', request).pipe(
      tap(res => {
        this.tokenSubject.next(res.token);
        this.agentSubject.next(res.agent);
      })
    );
  }

  logout(): void {
    this.tokenSubject.next(null);
    this.agentSubject.next(null);
  }

  fetchCurrentAgent(): Observable<Agent> {
    return this.http.get<Agent>('/api/auth/me').pipe(
      tap(agent => this.agentSubject.next(agent))
    );
  }
}
