import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface CaseSummary {
  id: number;
  title: string;
  caseNumber: string;
  classification: string;
  difficulty: number;
  moodTags: string[];
  era: string;
  synopsis: string;
}

export interface CaseDetail {
  id: number;
  title: string;
  caseNumber: string;
  classification: string;
  difficulty: number;
  settingDescription: string;
  era: string;
  moodTags: string[];
  crimeType: string;
  synopsis: string;
  createdAt: string;
}

export interface CaseWithProgress {
  case: CaseDetail;
  progress: CaseProgress | null;
}

export interface CaseProgress {
  id: string;
  agentId: string;
  caseId: number;
  status: string;
  discoveredEvidenceIds: number[];
  interrogationCount: number;
  startedAt: string | null;
  completedAt: string | null;
  score: number | null;
  rating: number | null;
}

export interface Suspect {
  id: number;
  caseId: number;
  name: string;
  age: number;
  occupation: string;
  relationshipToVictim: string;
  personalityTraits: string[];
  alibi: string;
}

export interface Evidence {
  id: number;
  caseId: number;
  type: string;
  title: string;
  description: string;
  discovered: boolean;
  isRedHerring: boolean;
}

export interface Victim {
  id: number;
  caseId: number;
  name: string;
  age: number;
  occupation: string;
  causeOfDeath: string;
  background: string;
}

export interface CaseFile {
  id: number;
  caseId: number;
  type: string;
  title: string;
  classificationLevel: string;
}

export interface CaseFileDetail extends CaseFile {
  content: string;
}

export interface InterrogationStartResult {
  sessionActive: boolean;
  emotionalState: string;
  messageCount: number;
  history: InterrogationEntry[];
  openingStatement: string | null;
}

export interface InterrogationEntry {
  role: 'agent' | 'suspect';
  content: string;
}

export interface InterrogationMessageResult {
  response: string;
  emotionalState: string;
  messageCount: number;
  evidenceDiscovered: DiscoveredEvidence[];
}

export interface DiscoveredEvidence {
  id: number;
  title: string;
}

@Injectable({ providedIn: 'root' })
export class CaseService {
  constructor(private http: HttpClient) {}

  listCases(mood?: string, difficulty?: number): Observable<CaseSummary[]> {
    let params = new HttpParams();
    if (mood) params = params.set('mood', mood);
    if (difficulty) params = params.set('difficulty', difficulty.toString());
    return this.http.get<CaseSummary[]>('/api/case', { params });
  }

  getCase(caseId: number): Observable<CaseWithProgress> {
    return this.http.get<CaseWithProgress>(`/api/case/${caseId}`);
  }

  startCase(caseId: number): Observable<CaseProgress> {
    return this.http.post<CaseProgress>(`/api/case/${caseId}/start`, {});
  }

  getMyProgress(): Observable<CaseProgress[]> {
    return this.http.get<CaseProgress[]>('/api/case/progress');
  }

  getCaseFiles(caseId: number): Observable<CaseFile[]> {
    return this.http.get<CaseFile[]>(`/api/ai/cases/${caseId}/files`);
  }

  getCaseFile(caseId: number, fileId: number): Observable<CaseFileDetail> {
    return this.http.get<CaseFileDetail>(`/api/ai/cases/${caseId}/files/${fileId}`);
  }

  getSuspects(caseId: number): Observable<Suspect[]> {
    return this.http.get<Suspect[]>(`/api/ai/cases/${caseId}/suspects`);
  }

  getEvidence(caseId: number): Observable<Evidence[]> {
    return this.http.get<Evidence[]>(`/api/ai/cases/${caseId}/evidence`);
  }

  getVictims(caseId: number): Observable<Victim[]> {
    return this.http.get<Victim[]>(`/api/ai/cases/${caseId}/victims`);
  }

  discoverEvidence(caseId: number, evidenceId: number): Observable<CaseProgress> {
    return this.http.put<CaseProgress>(`/api/case/${caseId}/evidence/${evidenceId}/discover`, {});
  }

  // Interrogation methods
  startInterrogation(caseId: number, suspectId: number): Observable<InterrogationStartResult> {
    return this.http.post<InterrogationStartResult>('/api/interrogation/start', { caseId, suspectId });
  }

  sendInterrogationMessage(
    caseId: number,
    suspectId: number,
    message: string,
    presentedEvidenceIds: number[] = []
  ): Observable<InterrogationMessageResult> {
    return this.http.post<InterrogationMessageResult>('/api/interrogation/message', {
      caseId, suspectId, message, presentedEvidenceIds
    });
  }

  getInterrogationHistory(caseId: number, suspectId: number): Observable<any> {
    return this.http.get(`/api/interrogation/history/${caseId}/${suspectId}`);
  }

  endInterrogation(caseId: number, suspectId: number): Observable<any> {
    return this.http.post('/api/interrogation/end', { caseId, suspectId });
  }
}
