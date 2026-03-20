import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

interface MoodAnalysisResult {
  dominant_moods: string[];
  color_palette: string[];
  setting_type: string[];
  time_of_day: string;
  atmospheric_keywords: string[];
  caption: string;
  recommendations: CaseRecommendation[];
}

interface CaseRecommendation {
  case_id: number;
  title: string;
  case_number: string;
  classification: string;
  difficulty: number;
  mood_tags: string[];
  era: string;
  synopsis: string;
  mood_match_percentage: number;
  matched_moods: string[];
}

@Component({
  selector: 'app-mood-matcher',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="crt-container crt-flicker">
      <div class="mood-screen">
        <div class="header-section">
          <div class="terminal-line system-line">MOOD-BASED CASE MATCHING SYSTEM</div>
          <div class="terminal-line system-line">═══════════════════════════════════════════════════</div>
          <div class="terminal-line dim">&gt; Upload an image. We'll find a case that matches the vibe.</div>
        </div>

        <!-- Input Mode Selection -->
        <div *ngIf="!analyzing && !result" class="input-section">
          <div class="terminal-line">&gt; SELECT INPUT MODE:</div>
          <div class="mode-buttons">
            <button class="terminal-btn" [class.active]="mode === 'image'" (click)="mode = 'image'">
              [UPLOAD IMAGE]
            </button>
            <button class="terminal-btn" [class.active]="mode === 'text'" (click)="mode = 'text'">
              [DESCRIBE A MOOD]
            </button>
          </div>

          <!-- Image Upload -->
          <div *ngIf="mode === 'image'" class="upload-section">
            <div class="terminal-line dim">&gt; SELECT AN IMAGE FILE FOR ANALYSIS:</div>
            <label class="upload-area" [class.has-file]="selectedFile">
              <input type="file" accept="image/*" (change)="onFileSelected($event)" hidden />
              <div *ngIf="!selectedFile" class="upload-placeholder">
                <div class="upload-icon">[IMG]</div>
                <div>CLICK TO SELECT IMAGE</div>
                <div class="dim small">JPEG, PNG, WEBP — MAX 10 MB</div>
              </div>
              <div *ngIf="selectedFile" class="file-info">
                <div>&gt; FILE LOADED: {{ selectedFile.name }}</div>
                <div class="dim">&gt; SIZE: {{ formatFileSize(selectedFile.size) }}</div>
              </div>
            </label>
            <div *ngIf="imagePreview" class="preview-container">
              <img [src]="imagePreview" class="image-preview" alt="Preview" />
            </div>
            <button class="terminal-btn submit-btn" [disabled]="!selectedFile" (click)="analyzeImage()">
              [ANALYZE IMAGE]
            </button>
          </div>

          <!-- Text Description -->
          <div *ngIf="mode === 'text'" class="text-section">
            <div class="terminal-line dim">&gt; DESCRIBE THE MOOD OR ATMOSPHERE YOU'RE LOOKING FOR:</div>
            <textarea
              class="terminal-input"
              [(ngModel)]="textDescription"
              rows="4"
              placeholder="e.g., dark foggy lakeside at night, isolated and melancholic..."
            ></textarea>
            <button class="terminal-btn submit-btn" [disabled]="!textDescription.trim()" (click)="analyzeText()">
              [ANALYZE MOOD]
            </button>
          </div>
        </div>

        <!-- Analyzing Animation -->
        <div *ngIf="analyzing" class="analyzing-section">
          <div class="terminal-line" *ngFor="let line of analysisLines">
            <span [class.blink]="line === analysisLines[analysisLines.length - 1] && analyzing">{{ line }}</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" [style.width.%]="analysisProgress"></div>
          </div>
        </div>

        <!-- Results -->
        <div *ngIf="result && !analyzing" class="results-section">
          <div class="terminal-line system-line">&gt; ANALYSIS COMPLETE</div>
          <div class="terminal-line">&gt; DOMINANT MOOD: {{ result.dominant_moods.join(', ') }}</div>
          <div class="terminal-line">&gt; SETTING: {{ result.setting_type.join(', ') }}, {{ result.time_of_day }}</div>
          <div class="terminal-line">&gt; ATMOSPHERE: {{ result.atmospheric_keywords.join(', ') || 'unknown' }}</div>
          <div *ngIf="result.color_palette.length > 0" class="terminal-line">&gt; COLOR PALETTE: {{ result.color_palette.join(', ') }}</div>

          <div class="separator">═══════════════════════════════════════════════════</div>

          <div *ngIf="result.recommendations.length > 0" class="recommendations">
            <div class="terminal-line system-line">&gt; MATCHING CASES FOUND:</div>
            <div *ngFor="let rec of result.recommendations; let i = index" class="case-card">
              <div class="case-header">
                <span class="case-number">[{{ i + 1 }}]</span>
                <span class="case-title">{{ rec.case_number }} "{{ rec.title }}"</span>
                <span class="match-pct" [class.high-match]="rec.mood_match_percentage >= 70">
                  — {{ rec.mood_match_percentage }}% mood match
                </span>
              </div>
              <div class="case-detail dim">
                DIFFICULTY: {{ getDifficultyBar(rec.difficulty) }} | ERA: {{ rec.era }} | MOOD: {{ rec.mood_tags.join(', ') }}
              </div>
              <div class="case-detail dim">{{ rec.synopsis }}</div>
              <div class="case-detail dim">MATCHED ON: {{ rec.matched_moods.join(', ') }}</div>
              <button class="terminal-btn open-btn" (click)="openCase(rec.case_id)">
                [OPEN CASE FILE]
              </button>
            </div>
          </div>

          <div *ngIf="result.recommendations.length === 0" class="no-match">
            <div class="terminal-line dim">&gt; NO MATCHING CASES FOUND FOR THIS MOOD PROFILE.</div>
            <div class="terminal-line dim">&gt; TRY A DIFFERENT IMAGE OR DESCRIPTION.</div>
          </div>

          <div class="action-buttons">
            <button class="terminal-btn" (click)="reset()">[TRY ANOTHER]</button>
            <button class="terminal-btn" (click)="navigate('/terminal')">[RETURN TO TERMINAL]</button>
          </div>
        </div>

        <!-- Error -->
        <div *ngIf="error" class="error-section">
          <div class="terminal-line error-line">&gt; ERROR: {{ error }}</div>
          <button class="terminal-btn" (click)="reset()">[TRY AGAIN]</button>
        </div>

        <!-- Navigation -->
        <div class="footer-section">
          <div class="terminal-line dim">
            <span class="back-link" (click)="navigate('/terminal')">&gt; [ RETURN TO TERMINAL ]</span>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .mood-screen {
      padding: 40px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .terminal-line {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 16px;
      margin-bottom: 4px;
      white-space: pre-wrap;
    }

    .system-line { color: var(--terminal-amber); }
    .dim { color: var(--terminal-dim); }
    .small { font-size: 12px; }
    .error-line { color: var(--terminal-red); }

    .separator {
      color: var(--terminal-amber);
      font-family: var(--terminal-font);
      margin: 12px 0;
    }

    .mode-buttons {
      display: flex;
      gap: 16px;
      margin-top: 12px;
    }

    .terminal-btn {
      background: transparent;
      border: 1px solid var(--terminal-green);
      color: var(--terminal-green);
      font-family: var(--terminal-font);
      font-size: 14px;
      padding: 10px 20px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .terminal-btn:hover:not(:disabled) {
      background: var(--terminal-green);
      color: var(--terminal-bg);
    }

    .terminal-btn:disabled {
      border-color: var(--terminal-dim);
      color: var(--terminal-dim);
      cursor: not-allowed;
    }

    .terminal-btn.active {
      background: var(--terminal-green);
      color: var(--terminal-bg);
    }

    .upload-section, .text-section {
      margin-top: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .upload-area {
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px dashed var(--terminal-dim);
      padding: 30px;
      cursor: pointer;
      font-family: var(--terminal-font);
      color: var(--terminal-dim);
      transition: all 0.2s;
      max-width: 500px;
    }

    .upload-area:hover {
      border-color: var(--terminal-green);
      color: var(--terminal-green);
    }

    .upload-area.has-file {
      border-color: var(--terminal-green);
      border-style: solid;
    }

    .upload-placeholder {
      text-align: center;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .upload-icon {
      font-size: 24px;
      color: var(--terminal-green);
    }

    .file-info {
      color: var(--terminal-green);
    }

    .preview-container {
      max-width: 300px;
      border: 1px solid var(--terminal-dim);
      padding: 4px;
    }

    .image-preview {
      max-width: 100%;
      max-height: 200px;
      filter: grayscale(50%) brightness(0.8) sepia(30%);
    }

    .terminal-input {
      background: transparent;
      border: 1px solid var(--terminal-green);
      color: var(--terminal-green);
      font-family: var(--terminal-font);
      font-size: 14px;
      padding: 12px;
      resize: vertical;
      max-width: 600px;
      outline: none;
    }

    .terminal-input::placeholder {
      color: var(--terminal-dim);
    }

    .terminal-input:focus {
      box-shadow: 0 0 8px rgba(0, 255, 65, 0.3);
    }

    .submit-btn {
      align-self: flex-start;
      margin-top: 8px;
    }

    .analyzing-section {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .progress-bar {
      width: 400px;
      height: 12px;
      border: 1px solid var(--terminal-green);
      margin-top: 8px;
    }

    .progress-fill {
      height: 100%;
      background: var(--terminal-green);
      transition: width 0.3s ease;
    }

    .blink {
      animation: terminal-blink 1s step-end infinite;
    }

    @keyframes terminal-blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0; }
    }

    .results-section {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .recommendations {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .case-card {
      border: 1px solid var(--terminal-dim);
      padding: 16px;
      max-width: 700px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .case-header {
      font-family: var(--terminal-font);
      color: var(--terminal-green);
      font-size: 16px;
    }

    .case-number {
      color: var(--terminal-amber);
      margin-right: 8px;
    }

    .case-title {
      font-weight: bold;
    }

    .match-pct {
      color: var(--terminal-dim);
    }

    .match-pct.high-match {
      color: var(--terminal-green);
    }

    .case-detail {
      font-family: var(--terminal-font);
      font-size: 13px;
    }

    .open-btn {
      align-self: flex-start;
      margin-top: 8px;
      font-size: 13px;
      padding: 6px 16px;
    }

    .no-match {
      margin: 16px 0;
    }

    .action-buttons {
      display: flex;
      gap: 16px;
      margin-top: 20px;
    }

    .footer-section {
      margin-top: auto;
      padding-top: 20px;
    }

    .back-link {
      cursor: pointer;
      color: var(--terminal-dim);
    }

    .back-link:hover {
      color: var(--terminal-green);
    }
  `]
})
export class MoodMatcherComponent {
  mode: 'image' | 'text' = 'image';
  selectedFile: File | null = null;
  imagePreview: string | null = null;
  textDescription = '';
  analyzing = false;
  analysisProgress = 0;
  analysisLines: string[] = [];
  result: MoodAnalysisResult | null = null;
  error: string | null = null;

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.selectedFile = input.files[0];
      this.error = null;

      const reader = new FileReader();
      reader.onload = (e) => {
        this.imagePreview = e.target?.result as string;
      };
      reader.readAsDataURL(this.selectedFile);
    }
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  getDifficultyBar(difficulty: number): string {
    return '\u2588'.repeat(difficulty) + '\u2591'.repeat(5 - difficulty);
  }

  analyzeImage(): void {
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('image', this.selectedFile);

    this.startAnalysis();

    this.http.post<MoodAnalysisResult>('/api/ai/mood/analyze', formData).subscribe({
      next: (result) => this.completeAnalysis(result),
      error: (err) => this.handleError(err),
    });
  }

  analyzeText(): void {
    if (!this.textDescription.trim()) return;

    this.startAnalysis();

    this.http.post<MoodAnalysisResult>('/api/ai/mood/analyze-text', {
      description: this.textDescription.trim()
    }).subscribe({
      next: (result) => this.completeAnalysis(result),
      error: (err) => this.handleError(err),
    });
  }

  private startAnalysis(): void {
    this.analyzing = true;
    this.error = null;
    this.result = null;
    this.analysisProgress = 0;
    this.analysisLines = [];

    const lines = [
      '> ANALYZING INPUT...',
      '> EXTRACTING VISUAL FEATURES...',
      '> IDENTIFYING DOMINANT MOOD...',
      '> MAPPING ATMOSPHERIC PROFILE...',
      '> CROSS-REFERENCING CASE DATABASE...',
    ];

    let i = 0;
    const interval = setInterval(() => {
      if (i < lines.length) {
        this.analysisLines.push(lines[i]);
        this.analysisProgress = ((i + 1) / lines.length) * 80;
        i++;
      } else {
        clearInterval(interval);
      }
    }, 500);
  }

  private completeAnalysis(result: MoodAnalysisResult): void {
    this.analysisProgress = 100;
    this.analysisLines.push('> ANALYSIS COMPLETE.');

    setTimeout(() => {
      this.analyzing = false;
      this.result = result;
    }, 600);
  }

  private handleError(err: any): void {
    this.analyzing = false;
    this.error = err.error?.detail || 'System malfunction. Please try again. [ERROR CODE: 5XX]';
  }

  reset(): void {
    this.selectedFile = null;
    this.imagePreview = null;
    this.textDescription = '';
    this.analyzing = false;
    this.analysisProgress = 0;
    this.analysisLines = [];
    this.result = null;
    this.error = null;
  }

  openCase(caseId: number): void {
    this.router.navigate(['/terminal/cases', caseId]);
  }

  navigate(path: string): void {
    this.router.navigate([path]);
  }
}
