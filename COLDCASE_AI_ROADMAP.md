# ColdCase AI — Full Project Roadmap & Specification

## For use with Claude Code — follow phases sequentially, complete each task before moving to the next

---

## Project Overview

**ColdCase AI** is an AI-powered interactive mystery investigation platform styled as a retro FBI terminal. Users connect to a "classified cold case database," pick cases, interrogate AI-driven suspects, collect and connect evidence, and solve mysteries. The platform features image-based mood matching (upload a photo, get a mystery that *feels* like it), community-created cases, and book/media recommendations after solving.

### Core Aesthetic

Retro CRT terminal — black background, green/amber/blue monospace text, scanline effects, typewriter text animations, blinking cursors, and "system glitch" effects. The UI is NOT a real command line — it's a hybrid of clickable interactive elements wrapped in terminal aesthetics.

### Architecture

Polyglot microservices monorepo:

- **Gateway Service** — .NET 8 (C#) — API Gateway, authentication, request orchestration
- **User Service** — Java 21 / Spring Boot 3 — User management, profiles, case progress, leaderboards
- **AI Service** — Python 3.12 / FastAPI — LangChain, HuggingFace, case generation, suspect interrogation, mood analysis, book recommendations
- **Frontend App** — Angular 17+ — Main terminal investigation UI
- **Public Site** — Vue.js 3 — Public landing page, featured cases, community showcase
- **Infrastructure** — Docker Compose, PostgreSQL 16, RabbitMQ, Redis

### Monorepo Structure

```
coldcase-ai/
├── README.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── .github/
│   └── workflows/
│       ├── gateway-ci.yml
│       ├── user-service-ci.yml
│       ├── ai-service-ci.yml
│       ├── frontend-ci.yml
│       └── public-site-ci.yml
├── gateway/                    # .NET 8
│   ├── src/
│   │   ├── ColdCase.Gateway/
│   │   │   ├── Program.cs
│   │   │   ├── appsettings.json
│   │   │   ├── Controllers/
│   │   │   ├── Services/
│   │   │   ├── Models/
│   │   │   ├── Middleware/
│   │   │   └── Configuration/
│   │   └── ColdCase.Gateway.Tests/
│   └── Dockerfile
├── user-service/               # Java / Spring Boot
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/coldcase/userservice/
│   │   │   │   ├── UserServiceApplication.java
│   │   │   │   ├── controller/
│   │   │   │   ├── service/
│   │   │   │   ├── repository/
│   │   │   │   ├── model/
│   │   │   │   ├── dto/
│   │   │   │   └── config/
│   │   │   └── resources/
│   │   │       └── application.yml
│   │   └── test/
│   ├── build.gradle
│   └── Dockerfile
├── ai-service/                 # Python / FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── cases.py
│   │   │   ├── interrogation.py
│   │   │   ├── mood.py
│   │   │   └── recommendations.py
│   │   ├── services/
│   │   │   ├── case_generator.py
│   │   │   ├── interrogation_engine.py
│   │   │   ├── mood_analyzer.py
│   │   │   └── recommendation_engine.py
│   │   ├── models/
│   │   ├── chains/              # LangChain chain definitions
│   │   └── config.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Angular
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/            # Guards, interceptors, auth
│   │   │   ├── shared/          # Terminal components, pipes
│   │   │   ├── features/
│   │   │   │   ├── boot-sequence/
│   │   │   │   ├── case-browser/
│   │   │   │   ├── investigation/
│   │   │   │   │   ├── dossier/
│   │   │   │   │   ├── interrogation/
│   │   │   │   │   ├── evidence-board/
│   │   │   │   │   ├── forensics-lab/
│   │   │   │   │   └── case-report/
│   │   │   │   ├── agent-profile/
│   │   │   │   └── mood-matcher/
│   │   │   └── app.component.ts
│   │   ├── assets/
│   │   │   ├── fonts/           # Monospace terminal fonts
│   │   │   └── audio/           # Ambient sounds (optional)
│   │   └── styles/
│   │       ├── _terminal.scss
│   │       ├── _crt-effects.scss
│   │       ├── _typewriter.scss
│   │       └── styles.scss
│   ├── angular.json
│   └── Dockerfile
├── public-site/                # Vue.js 3
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── composables/
│   │   ├── router/
│   │   └── App.vue
│   ├── vite.config.ts
│   └── Dockerfile
└── infrastructure/
    ├── postgres/
    │   └── init.sql
    ├── rabbitmq/
    │   └── definitions.json
    └── nginx/
        └── nginx.conf
```

---

## PHASE 0 — Project Scaffolding & Infrastructure

**Goal:** Get the monorepo set up with all service skeletons, Docker Compose running, and inter-service communication verified.

### Task 0.1 — Initialize Monorepo

- Create the root `coldcase-ai/` directory with the folder structure shown above
- Initialize a root `README.md` with project name, description, architecture diagram (ASCII art is fine), and a "Getting Started" section placeholder
- Add a root `.gitignore` covering .NET, Java, Python, Node.js, and IDE files
- Initialize git

**Acceptance:** `git status` shows clean repo with folder structure.

### Task 0.2 — PostgreSQL & Infrastructure Setup

- Create `docker-compose.dev.yml` with:
  - PostgreSQL 16 container (port 5432, database: `coldcase`, user: `coldcase`, password: `coldcase_dev`)
  - RabbitMQ container with management UI (ports 5672, 15672)
  - Redis container (port 6379)
- Create `infrastructure/postgres/init.sql` that creates three schemas: `gateway`, `users`, `ai_service`
- Verify all containers start with `docker compose -f docker-compose.dev.yml up`

**Acceptance:** All three infrastructure containers running, PostgreSQL accessible with schemas created.

### Task 0.3 — .NET Gateway Service Scaffold

- Create a new .NET 8 Web API project in `gateway/src/ColdCase.Gateway/`
- Add packages: `Yarp.ReverseProxy`, `Microsoft.AspNetCore.Authentication.JwtBearer`, `Npgsql.EntityFrameworkCore.PostgreSQL`, `Swashbuckle.AspNetCore`
- Configure YARP reverse proxy in `appsettings.json` with route stubs for `/api/users/**` → user-service, `/api/ai/**` → ai-service
- Add a health check endpoint at `GET /health`
- Add JWT authentication configuration (issuer: `coldcase-ai`, audience: `coldcase-api`) with a dev signing key
- Add CORS policy allowing `http://localhost:4200` (Angular) and `http://localhost:5173` (Vue)
- Create `gateway/Dockerfile` (multi-stage build)
- Add xUnit test project in `gateway/src/ColdCase.Gateway.Tests/` with one health check test

**Acceptance:** Gateway starts on port 5000, `/health` returns 200, Swagger UI accessible at `/swagger`, YARP proxy configured (routes will 502 until other services exist — that's fine).

### Task 0.4 — Java User Service Scaffold

- Create a Spring Boot 3 project in `user-service/` using Gradle
- Java 21, Spring Web, Spring Data JPA, PostgreSQL driver, Spring Validation, Spring Boot Actuator
- Configure `application.yml` for PostgreSQL connection (host: `localhost`, port: 5432, database: `coldcase`, schema: `users`)
- Create a basic `Agent` entity (id UUID, username, email, passwordHash, rank, casesCompleted, createdAt, updatedAt)
- Create `AgentRepository` extending JpaRepository
- Create `AgentController` with `GET /api/users/health` returning 200
- Create `user-service/Dockerfile`
- Add one integration test verifying the health endpoint

**Acceptance:** User service starts on port 8080, `/api/users/health` returns 200, `Agent` table created in PostgreSQL on startup.

### Task 0.5 — Python AI Service Scaffold

- Create FastAPI project in `ai-service/`
- `requirements.txt` with: `fastapi`, `uvicorn[standard]`, `langchain`, `langchain-community`, `langchain-huggingface`, `huggingface-hub`, `transformers`, `pydantic`, `python-dotenv`, `httpx`, `pytest`, `redis`
- Create `app/main.py` with FastAPI app, CORS middleware, and a health endpoint at `GET /api/ai/health`
- Create stub routers in `app/routers/` — `cases.py`, `interrogation.py`, `mood.py`, `recommendations.py` — each with a placeholder GET endpoint
- Create `app/config.py` with Pydantic Settings for env vars (HuggingFace API token, Redis URL, database URL)
- Create `ai-service/Dockerfile`
- Add one pytest test for the health endpoint

**Acceptance:** AI service starts on port 8000, `/api/ai/health` returns 200, all stub router endpoints return placeholder responses.

### Task 0.6 — Angular Frontend Scaffold

- Create Angular 17+ project in `frontend/` using standalone components (no NgModules)
- Install dependencies: `@angular/cdk` (for drag-drop on evidence board later)
- Set up SCSS as the style preprocessor
- Create the global terminal styles in `styles/`:
  - `_terminal.scss`: Black background (#0a0a0a), green text (#00ff41), monospace font (use `'Courier New', 'Lucida Console', monospace` for now), full viewport height
  - `_crt-effects.scss`: CSS scanline overlay using a repeating-linear-gradient, subtle screen flicker animation using keyframes, slight border-radius on the main container to mimic CRT curve, optional vignette effect using box-shadow inset
  - `_typewriter.scss`: CSS animation for character-by-character reveal using `steps()` and `ch` units
- Create a shared `TerminalTextComponent` (standalone) that accepts a string input and renders it with the typewriter animation
- Create a shared `TerminalPromptComponent` that shows `> ` with a blinking cursor
- Create a `BootSequenceComponent` as the landing page — on load, it types out the FBI connection sequence text line by line:
  ```
  ESTABLISHING SECURE CONNECTION...
  ROUTING THROUGH ENCRYPTED CHANNELS...
  CONNECTION ESTABLISHED.
  ACCESSING FEDERAL COLD CASE DATABASE...
  WARNING: UNAUTHORIZED ACCESS DETECTED
  ...PROCEEDING ANYWAY.
  WELCOME, AGENT.
  > PRESS [ENTER] TO CONTINUE
  ```
- Set up Angular routing: `/` → BootSequenceComponent
- Configure the Angular proxy (`proxy.conf.json`) to forward `/api/**` to `http://localhost:5000` (the gateway)
- Create `frontend/Dockerfile` (multi-stage with nginx)

**Acceptance:** Angular app runs on port 4200, shows the boot sequence with typewriter animation, CRT scanline effect visible, blinking cursor works.

### Task 0.7 — Vue.js Public Site Scaffold

- Create Vue 3 project in `public-site/` using Vite + TypeScript + Vue Router
- Create a minimal landing page at `/` with:
  - Dark theme matching the terminal aesthetic (but cleaner, more "marketing site")
  - A hero section: "ColdCase AI — Can You Solve What They Couldn't?" with a CTA button "Access the Terminal"
  - A "Featured Cases" section (placeholder cards for now)
  - A "How It Works" section with 3 steps (placeholder)
- Configure Vite proxy to forward `/api/**` to `http://localhost:5000`
- Create `public-site/Dockerfile`

**Acceptance:** Vue site runs on port 5173, landing page renders with dark theme.

### Task 0.8 — Docker Compose Full Stack

- Create the main `docker-compose.yml` that orchestrates ALL services:
  - PostgreSQL, RabbitMQ, Redis (same as dev)
  - Gateway (.NET) on port 5000
  - User Service (Java) on port 8080
  - AI Service (Python) on port 8000
  - Frontend (Angular + nginx) on port 4200
  - Public Site (Vue + nginx) on port 5173
  - Nginx reverse proxy on port 80 that routes:
    - `/` → frontend
    - `/public` → public-site
    - `/api/**` → gateway
- Add health check dependencies so services start in order
- Test that `docker compose up --build` brings everything up

**Acceptance:** All services accessible through their ports, gateway successfully proxies to user-service and ai-service health endpoints.

### Task 0.9 — GitHub Actions CI Stubs

- Create CI workflow files in `.github/workflows/` for each service:
  - `gateway-ci.yml`: Restore, build, test the .NET project. Trigger on changes to `gateway/**`
  - `user-service-ci.yml`: Gradle build + test. Trigger on changes to `user-service/**`
  - `ai-service-ci.yml`: pip install + pytest. Trigger on changes to `ai-service/**`
  - `frontend-ci.yml`: npm install + `ng build` + `ng test`. Trigger on changes to `frontend/**`
  - `public-site-ci.yml`: npm install + `vite build`. Trigger on changes to `public-site/**`
- Each workflow runs on `push` and `pull_request` to `main`

**Acceptance:** All 5 workflow files exist with correct triggers and build steps.

---

## PHASE 1 — Authentication & Core User Flow

**Goal:** Users can register, log in, and see a persistent agent profile. The full auth flow goes through the gateway.

### Task 1.1 — Gateway Auth Endpoints

- In the gateway, create `AuthController` with:
  - `POST /api/auth/register` — accepts `{ username, email, password }`, validates input, hashes password with BCrypt, calls user-service internally to create the agent, returns JWT token
  - `POST /api/auth/login` — accepts `{ email, password }`, validates credentials via user-service, returns JWT token
  - `GET /api/auth/me` — requires JWT, returns current agent info
- JWT should include claims: `sub` (agent ID), `username`, `rank`
- Token expiry: 24 hours
- Create a `JwtService` in `Services/` that handles token generation and validation
- Write unit tests for token generation and password hashing

**Acceptance:** Can register a new agent via Postman, receive a JWT, and use it to call `/api/auth/me`.

### Task 1.2 — User Service CRUD

- In the Java user-service, expand `AgentController`:
  - `POST /api/users/agents` — create agent (called by gateway internally)
  - `GET /api/users/agents/{id}` — get agent by ID
  - `PUT /api/users/agents/{id}` — update agent profile
  - `GET /api/users/agents/by-email/{email}` — get agent by email (for login lookup)
  - `GET /api/users/agents/{id}/stats` — return agent statistics (cases completed, rank, etc.)
- Add `AgentService` layer between controller and repository with business logic
- Add proper exception handling with `@ControllerAdvice` and custom exceptions (AgentNotFoundException, DuplicateEmailException)
- Add input validation with Jakarta Validation annotations
- Write unit tests for the service layer

**Acceptance:** Full CRUD operations work through the gateway auth flow.

### Task 1.3 — Angular Auth Integration

- Create an `AuthService` in Angular (`core/services/auth.service.ts`) that:
  - Stores JWT in memory (NOT localStorage — use a BehaviorSubject)
  - Provides `login()`, `register()`, `logout()`, `getCurrentAgent()`, `isAuthenticated$` observable
- Create an `AuthInterceptor` that attaches the JWT to all `/api` requests
- Create an `AuthGuard` for protected routes
- After the boot sequence, show a terminal-styled login/register flow:
  ```
  > AGENT IDENTIFICATION REQUIRED
  > SELECT: [NEW AGENT REGISTRATION] [EXISTING AGENT LOGIN]
  ```
  - Registration shows terminal prompts for username, email, password (styled as terminal input fields with the green cursor)
  - Login shows terminal prompts for email and password
  - On success: `> IDENTITY VERIFIED. WELCOME BACK, AGENT {username}. CLEARANCE LEVEL: {rank}`
- Add routes: `/login`, `/register`, `/terminal` (protected main hub)
- After auth, route to `/terminal` which shows the main command hub:
  ```
  > AGENT: {username} | RANK: {rank} | CASES SOLVED: {count}
  > AVAILABLE COMMANDS:
    [BROWSE CASES]  [ACTIVE INVESTIGATIONS]  [EVIDENCE LOCKER]  [AGENT PROFILE]
  ```

**Acceptance:** Full register → login → see main terminal hub flow works end-to-end.

---

## PHASE 2 — Case System (The Core Loop)

**Goal:** Cases exist in the database, users can browse and open them, and the investigation dossier view works.

### Task 2.1 — Case Data Model

- In the AI service, create Pydantic models in `app/models/`:
  - `Case`: id, title, case_number (formatted like "CASE #1977-B"), classification (COLD, ACTIVE, CLASSIFIED), difficulty (1-5), setting_description, era (decade), mood_tags (list), crime_type, synopsis, created_at
  - `Suspect`: id, case_id, name, age, occupation, relationship_to_victim, personality_traits, hidden_knowledge (what they know but won't easily reveal), is_guilty, alibi
  - `Evidence`: id, case_id, type (PHYSICAL, TESTIMONIAL, FORENSIC, DOCUMENTARY), title, description, discovered (bool — starts false, revealed during investigation), linked_suspect_ids, is_red_herring
  - `Victim`: id, case_id, name, age, occupation, cause_of_death, background
  - `CaseFile`: id, case_id, type (CRIME_SCENE_REPORT, WITNESS_STATEMENT, FORENSIC_ANALYSIS, NEWSPAPER_CLIPPING, POLICE_NOTES), title, content (the actual text), classification_level
- In the user-service, create:
  - `CaseProgress` entity: id, agent_id, case_id, status (NOT_STARTED, IN_PROGRESS, SOLVED, FAILED), discovered_evidence_ids (JSON array), interrogation_count, started_at, completed_at, score, rating

### Task 2.2 — Seed Cases (Hardcoded Starter Cases)

- Create a seed data file `ai-service/app/seed/starter_cases.py` with **3 fully written cases**:
  - **Case #1977-B "The Lake House"** — Classic noir. A body found in a lake near a wealthy family's estate. 3 suspects, 8 evidence items (2 red herrings). Era: 1970s. Mood: dark, foggy, melancholic.
  - **Case #2003-K "Digital Ghost"** — Cybercrime gone wrong. A programmer found dead in their apartment, laptop wiped clean. 4 suspects, 10 evidence items (3 red herrings). Era: 2000s. Mood: sterile, neon, paranoid.
  - **Case #1992-R "The Last Broadcast"** — A radio host vanishes mid-show. The recording holds clues. 3 suspects, 9 evidence items (2 red herrings). Era: 1990s. Mood: eerie, nostalgic, small-town.
- Each case should have complete suspects with personalities, all evidence items, victim details, and 4-5 case files with full written content
- Create a FastAPI startup event or management command that seeds these cases into PostgreSQL if they don't exist
- Create SQLAlchemy models mapping to the Pydantic models above, using the `ai_service` schema

**Acceptance:** On AI service startup, 3 cases with all associated data exist in the database.

### Task 2.3 — Case Browsing API

- In the AI service, implement in `routers/cases.py`:
  - `GET /api/ai/cases` — list all cases (returns summary: id, title, case_number, classification, difficulty, mood_tags, era, synopsis). Supports `?mood=` and `?difficulty=` query filters
  - `GET /api/ai/cases/{case_id}` — full case detail (but NOT hidden suspect knowledge or guilty flag — that's server-side only)
  - `GET /api/ai/cases/{case_id}/files` — list case files for a case
  - `GET /api/ai/cases/{case_id}/files/{file_id}` — get a specific case file's content
  - `GET /api/ai/cases/{case_id}/suspects` — list suspects (public info only: name, age, occupation, relationship)
  - `GET /api/ai/cases/{case_id}/evidence` — list only DISCOVERED evidence for the requesting agent (requires agent_id as query param)
- Add corresponding `CaseService` in `app/services/case_generator.py`

**Acceptance:** All endpoints return correct data. Suspects don't leak hidden knowledge. Evidence respects discovery state.

### Task 2.4 — Case Progress Tracking

- In the user-service, implement:
  - `POST /api/users/agents/{id}/cases/{caseId}/start` — create CaseProgress with IN_PROGRESS status
  - `GET /api/users/agents/{id}/cases` — list all case progress for an agent
  - `GET /api/users/agents/{id}/cases/{caseId}` — get specific case progress
  - `PUT /api/users/agents/{id}/cases/{caseId}/evidence/{evidenceId}/discover` — mark evidence as discovered
- The gateway should orchestrate: when the Angular app requests case data, the gateway calls BOTH the AI service (for case content) and user service (for progress) and merges the response

**Acceptance:** Can start a case, track progress, discover evidence, and see it reflected in subsequent requests.

### Task 2.5 — Angular Case Browser

- Create the `CaseBrowserComponent` at route `/terminal/cases`
- Display cases in terminal style:
  ```
  > ACCESSING COLD CASE DATABASE...
  > 3 CASES FOUND. DISPLAYING RESULTS:

  ┌─────────────────────────────────────────────┐
  │ CASE #1977-B — THE LAKE HOUSE               │
  │ CLASSIFICATION: COLD | DIFFICULTY: ███░░     │
  │ ERA: 1970s | MOOD: dark, foggy, melancholic  │
  │ "Three witnesses. Three stories. One body."  │
  │ [OPEN CASE FILE]                             │
  └─────────────────────────────────────────────┘
  ```
- Each case card is clickable
- Add filter "commands": `[ALL CASES]  [BY DIFFICULTY]  [BY ERA]`
- Use typewriter animation when the case list first loads

**Acceptance:** Cases display in terminal style, clicking opens case detail route.

### Task 2.6 — Angular Investigation Dossier View

- Create the `InvestigationComponent` at route `/terminal/cases/:caseId`
- This is the main investigation hub. Show a terminal tab system:
  ```
  > CASE #1977-B — THE LAKE HOUSE — STATUS: IN PROGRESS
  > [CASE FILES]  [SUSPECTS]  [EVIDENCE]  [INTERROGATE]  [FORENSICS LAB]  [FILE REPORT]
  ```
- **CASE FILES tab**: Lists case files with typewriter text. Clicking a file "downloads" it with a progress bar animation, then displays the content in a styled document view (green-tinted, slightly different font styling to feel like reading a document)
- **SUSPECTS tab**: Lists suspects with their public info. Each suspect shows a small ASCII art portrait placeholder and their details
- **EVIDENCE tab**: Shows only discovered evidence. Initially mostly empty — evidence gets revealed through interrogation and forensics. Undiscovered evidence shows as `[REDACTED]` or `[████████████]`
- Use Angular animations for tab transitions (terminal screen clear effect)

**Acceptance:** Full investigation view works with tabs, case files readable, suspects listed, evidence shows discovered/redacted state.

---

## PHASE 3 — AI-Powered Interrogation

**Goal:** Users can interrogate suspects in a chat-like interface powered by LangChain. The AI maintains suspect personalities and reveals information based on questioning strategy.

### Task 3.1 — LangChain Interrogation Engine

- In the AI service, implement `services/interrogation_engine.py`:
  - Use LangChain with a free HuggingFace model (Mistral-7B-Instruct or similar via HuggingFace Inference API)
  - Create a prompt template for suspect interrogation that includes:
    - Suspect's personality, background, relationship to victim
    - Their hidden knowledge (what they know but resist revealing)
    - Whether they're guilty (affects evasion patterns)
    - Their alibi and any contradictions in it
    - Current conversation history
    - Emotional state tracker (calm → nervous → agitated → defensive → breaking)
  - The system prompt should instruct the LLM to:
    - Stay in character as the suspect
    - Not volunteer hidden information easily
    - Show emotional state changes in brackets like `[SUSPECT SHIFTS UNCOMFORTABLY]`
    - Gradually reveal more when pressed on contradictions
    - React differently based on presented evidence
    - Occasionally lie or deflect if guilty
  - Create a `ConversationMemory` using LangChain's memory module per agent-suspect pair, stored in Redis
  - Implement evidence presentation: when the user "shows" evidence to a suspect, include it in the prompt context
- In `routers/interrogation.py`:
  - `POST /api/ai/interrogation/start` — body: `{ case_id, suspect_id, agent_id }` — initializes conversation, returns opening statement from suspect
  - `POST /api/ai/interrogation/message` — body: `{ case_id, suspect_id, agent_id, message, presented_evidence_ids? }` — sends message, returns suspect response with emotional state
  - `GET /api/ai/interrogation/history/{case_id}/{suspect_id}/{agent_id}` — returns full conversation history
  - `POST /api/ai/interrogation/end` — ends interrogation session

**Acceptance:** Can start an interrogation, send messages, receive in-character responses. Suspect's emotional state changes over conversation. Presenting evidence triggers different reactions.

### Task 3.2 — Evidence Discovery Through Interrogation

- When a suspect reveals certain information (tracked by keywords/flags in their hidden knowledge), the system should automatically mark related evidence as "discovered" for that agent
- Create a post-processing step after each interrogation response that:
  - Checks if the response content triggers any evidence discovery
  - If so, calls the user-service to mark that evidence as discovered
  - Returns a special flag in the response: `evidence_discovered: [{ id, title }]`
- In the terminal UI, this should trigger a notification: `> ⚠ NEW EVIDENCE DISCOVERED: {title} — Check your evidence locker.`

**Acceptance:** Interrogating suspects about the right topics reveals new evidence items.

### Task 3.3 — Angular Interrogation UI

- Create the `InterrogationComponent` at route `/terminal/cases/:caseId/interrogate/:suspectId`
- Style as an interrogation transcript:
  ```
  ╔══════════════════════════════════════════════════╗
  ║  INTERROGATION ROOM — RECORDING IN PROGRESS     ║
  ║  SUSPECT: MARCUS WELLS | STATUS: CALM            ║
  ╚══════════════════════════════════════════════════╝

  [14:32:07] AGENT: Where were you on the night of March 15th?
  [14:32:12] WELLS: I was at home. Alone. Watching TV.
             [SUSPECT AVOIDS EYE CONTACT]
  [14:32:45] AGENT: _
  ```
- The user input area shows suggested questioning approaches as clickable terminal commands:
  ```
  > QUESTIONING APPROACHES:
    [ASK ABOUT ALIBI]  [PRESS ON CONTRADICTION]
    [SHOW EVIDENCE]  [CHANGE SUBJECT]  [END INTERROGATION]
  ```
- Clicking [SHOW EVIDENCE] opens a sub-menu listing discovered evidence to present
- Suspect responses type out with the typewriter effect
- Emotional state indicator updates in the header: CALM → NERVOUS → AGITATED → DEFENSIVE
- When evidence is discovered, flash a terminal alert with a screen glitch effect
- The user can also type freely in a terminal input field (not just use suggestions)

**Acceptance:** Full interrogation flow works — both free-text and suggested approaches. Emotional states update. Evidence discovery triggers alerts.

---

## PHASE 4 — Evidence Board & Forensics Lab

**Goal:** Interactive evidence board where users connect clues visually, and a forensics lab that processes evidence asynchronously.

### Task 4.1 — Evidence Board (Angular)

- Create the `EvidenceBoardComponent` at route `/terminal/cases/:caseId/evidence-board`
- Dark corkboard aesthetic layered on top of the terminal (slightly different visual mode):
  - Dark brown/charcoal background with subtle texture
  - Evidence items appear as "pinned cards" — dark cards with green terminal text
  - Cards can be dragged around the board (use Angular CDK DragDrop)
  - Users can draw connections between cards by clicking one then clicking another — a red line connects them
  - When two actually-related evidence items are connected, the line turns green and a terminal notification appears: `> CORRELATION CONFIRMED: {description}`
  - Wrong connections stay red with: `> NO CORRELATION FOUND`
- Each evidence card shows: type icon (use ASCII characters like `[DOC]`, `[PHY]`, `[FOR]`), title, and a brief description
- Store board layout (card positions, connections) in the component state and persist via user-service API
- Add a `[RETURN TO TERMINAL]` button that transitions back to the main investigation view with a screen effect

**Acceptance:** Evidence cards are draggable, connections can be drawn, correct correlations turn green, layout persists.

### Task 4.2 — Forensics Lab

- In the AI service, create endpoints in `routers/cases.py`:
  - `POST /api/ai/cases/{case_id}/forensics/submit` — body: `{ evidence_id, analysis_type }` where analysis_type is FINGERPRINT, DNA, TOXICOLOGY, DIGITAL, BALLISTIC. Returns `{ request_id, estimated_time_seconds }`
  - `GET /api/ai/cases/{case_id}/forensics/{request_id}` — returns status (PROCESSING, COMPLETE) and results when complete
- Use RabbitMQ: when forensics is submitted, publish a message. A background worker (in the AI service) consumes it, waits 10-30 seconds (simulated processing), generates results using LangChain (or returns pre-written results for seed cases), and updates the database
- Results should be detailed forensic reports in terminal style

### Task 4.3 — Forensics Lab UI (Angular)

- Create the `ForensicsLabComponent` at route `/terminal/cases/:caseId/forensics`
- Terminal styled:
  ```
  > FORENSICS LABORATORY — CASE #1977-B
  > SELECT EVIDENCE FOR ANALYSIS:

  [1] Knife found near lake — Available: [FINGERPRINT] [DNA] [BALLISTIC]
  [2] Victim's phone — Available: [DIGITAL]
  [3] Hair sample — Available: [DNA]

  > PENDING ANALYSES:
    Request #F-001: Knife fingerprint analysis — [PROCESSING ████░░░░ 67%]
  ```
- Submitting evidence shows a processing animation
- Use polling (or SignalR later) to check for completed results
- When results arrive, display a terminal notification and the full forensic report in styled terminal text

**Acceptance:** Can submit evidence for forensic analysis, see processing animation, receive results after delay.

### Task 4.4 — SignalR Real-Time Notifications

- In the .NET gateway, add SignalR hub: `InvestigationHub`
  - Methods: `EvidenceDiscovered`, `ForensicsComplete`, `SystemAlert`
  - Hub requires JWT authentication
- When the AI service completes forensics analysis, it publishes a RabbitMQ message. The gateway consumes it and pushes a SignalR notification to the connected agent
- In Angular, create a `NotificationService` that connects to the SignalR hub
- Show notifications as terminal alerts at the top of the screen:
  ```
  > ⚠ INCOMING TRANSMISSION: Forensic analysis complete for EVIDENCE #4. [VIEW RESULTS]
  ```
- The notification should briefly cause a "screen glitch" CSS effect

**Acceptance:** Real-time notifications work — submit forensics, receive push notification when complete without polling.

---

## PHASE 5 — Case Solving & Scoring

**Goal:** Users can file their case report, get scored by the AI, receive a rank, and see their results.

### Task 5.1 — Case Report Submission API

- In the AI service, create in `routers/cases.py`:
  - `POST /api/ai/cases/{case_id}/solve` — body:
    ```json
    {
      "agent_id": "uuid",
      "accused_suspect_id": "uuid",
      "motive": "string (free text)",
      "method": "string (free text)",
      "key_evidence_ids": ["uuid", "uuid"],
      "timeline_of_events": "string (free text narrative)"
    }
    ```
  - The endpoint evaluates the submission:
    - Correct killer? (yes/no — primary scoring factor)
    - Motive accuracy? (use LangChain to compare submitted motive with actual motive — semantic similarity)
    - Evidence quality? (what % of key non-red-herring evidence was cited?)
    - Red herrings avoided? (did they cite red herrings as key evidence?)
    - Evidence discovery rate? (what % of total evidence did they find?)
  - Returns a detailed scoring object:
    ```json
    {
      "correct_killer": true,
      "motive_accuracy": 0.85,
      "evidence_score": 0.7,
      "red_herring_penalty": 0,
      "discovery_rate": 0.8,
      "overall_score": 87,
      "rank_earned": "SENIOR DETECTIVE",
      "feedback": "You correctly identified... However you missed...",
      "full_solution": { ... the actual full solution narrative }
    }
    ```
  - Rank tiers: ROOKIE (0-30), DETECTIVE (31-50), SENIOR DETECTIVE (51-70), SPECIAL AGENT (71-85), CHIEF INVESTIGATOR (86-100)
- Update the agent's stats in user-service (cases completed, rank update if applicable)

### Task 5.2 — Case Report UI (Angular)

- Create the `CaseReportComponent` at route `/terminal/cases/:caseId/report`
- Terminal styled form:
  ```
  > FILING CASE REPORT — CASE #1977-B
  > WARNING: This action is final. Ensure your investigation is complete.

  > ACCUSED: [SELECT SUSPECT ▼]
  > MOTIVE: [________________________]
  > METHOD: [________________________]
  > KEY EVIDENCE: (select from discovered evidence)
    [x] Knife with fingerprints
    [ ] Victim's phone records
    [x] Witness testimony — Sarah Mills
  > TIMELINE OF EVENTS:
    [___________________________________________]
    [___________________________________________]

  > [SUBMIT REPORT]  [CONTINUE INVESTIGATING]
  ```
- After submission, dramatic reveal sequence:
  ```
  > PROCESSING CASE REPORT...
  > CROSS-REFERENCING EVIDENCE...
  > ANALYZING SUSPECT PROFILE...
  > VALIDATING TIMELINE...
  > ═══════════════════════════════════════
  > CASE VERDICT: SOLVED
  > ACCURACY RATING: 87/100
  > RANK EARNED: ★★★ SENIOR DETECTIVE ★★★
  >
  > BREAKDOWN:
  > Correct Killer: ✓ YES
  > Motive Accuracy: 85%
  > Evidence Score: 70% (7/10 key items found)
  > Red Herrings Avoided: ✓ CLEAN
  >
  > FULL SOLUTION:
  > [typewriter reveals the full story of what actually happened]
  >
  > YOUR AGENT PROFILE HAS BEEN UPDATED.
  > [RETURN TO TERMINAL]  [BROWSE MORE CASES]
  ```
- Show ASCII art for the rank badge

**Acceptance:** Complete solve flow works — fill report, submit, see dramatic scoring reveal, agent profile updates.

---

## PHASE 6 — Mood Matching & Image Analysis

**Goal:** Users can upload an image and receive a mystery case recommendation based on the image's mood and atmosphere.

### Task 6.1 — Mood Analysis Engine (Python)

- In `services/mood_analyzer.py`:
  - Use HuggingFace's free Inference API with a CLIP or BLIP model for image analysis
  - Accept an image (base64 or file upload)
  - Analyze the image and extract: dominant mood (from a predefined set: dark, foggy, melancholic, neon, sterile, paranoid, eerie, nostalgic, warm, cold, urban, rural, industrial, coastal), color palette description, setting type (indoor/outdoor, urban/rural, modern/vintage), time of day estimation, atmospheric keywords
  - Return mood tags that map to existing case mood tags
  - Match these against cases in the database and return ranked recommendations with a "mood match percentage"
- In `routers/mood.py`:
  - `POST /api/ai/mood/analyze` — accepts image upload, returns mood analysis + case recommendations

### Task 6.2 — Mood Matcher UI (Angular)

- Create the `MoodMatcherComponent` at route `/terminal/mood`
- Terminal styled:
  ```
  > MOOD-BASED CASE MATCHING SYSTEM
  > Upload an image. We'll find a case that matches the vibe.

  > [UPLOAD IMAGE]  or  [DESCRIBE A MOOD]

  (after upload, show image analysis animation)

  > ANALYZING IMAGE...
  > DOMINANT MOOD: dark, foggy, melancholic
  > SETTING: outdoor, rural, lakeside, evening
  > ATMOSPHERE: isolation, grief, hidden secrets
  >
  > MATCHING CASES FOUND:
  > [1] CASE #1977-B "The Lake House" — 94% mood match
  > [2] CASE #1992-R "The Last Broadcast" — 67% mood match
  >
  > [OPEN CASE]  [TRY ANOTHER IMAGE]
  ```
- The "DESCRIBE A MOOD" option lets users type a text description instead of uploading — the AI service uses text-based matching in this case

**Acceptance:** Image upload works, mood analysis returns relevant tags, case recommendations match by mood.

---

## PHASE 7 — AI Case Generation

**Goal:** The system can procedurally generate new mystery cases using LangChain, beyond the hardcoded seed cases.

### Task 7.1 — Case Generation Engine

- In `services/case_generator.py`, implement `generate_case()`:
  - Use LangChain with structured output parsing to generate a complete case:
    - Generate a compelling case title, era, mood, crime type
    - Generate 3-4 suspects with detailed backgrounds, personalities, alibis, and hidden knowledge
    - Designate one guilty suspect
    - Generate 8-12 evidence items (including 2-3 red herrings)
    - Generate a victim with background
    - Generate 4-6 case files (crime scene report, witness statements, forensic report, news clipping, police notes)
    - Generate the complete solution narrative
  - Use a multi-step LangChain chain:
    - Step 1: Generate high-level case concept and victim
    - Step 2: Generate suspects and their relationships
    - Step 3: Generate the crime details and guilty party's method
    - Step 4: Generate evidence items linked to suspects
    - Step 5: Generate case files
    - Step 6: Generate solution narrative and scoring rubric
  - Accept optional parameters: mood_tags, era, difficulty, crime_type (for mood-matched generation)
  - Validate the generated case for consistency (no contradictory alibis, evidence makes sense)
  - Store the generated case in PostgreSQL
- In `routers/cases.py`:
  - `POST /api/ai/cases/generate` — body: `{ mood_tags?, era?, difficulty?, crime_type? }` — triggers case generation, returns the new case summary
  - This should be an async operation — return immediately with a generation_id, then the client polls or gets a SignalR notification when complete

### Task 7.2 — Batch Pre-Generation

- Create a management script `ai-service/scripts/generate_batch.py` that:
  - Generates N cases with varied parameters
  - Can be run manually or on a schedule
  - Validates each generated case before storing
- Pre-generate 5-10 additional cases beyond the 3 seed cases to populate the platform

**Acceptance:** AI generates complete, playable mystery cases. Generated cases have consistent internal logic. Batch script populates the database.

---

## PHASE 8 — Community Features & Vue.js Public Site

**Goal:** Users can rate cases, view leaderboards, and the Vue.js public site showcases the platform.

### Task 8.1 — Leaderboard & Ratings API

- In the user-service:
  - `POST /api/users/cases/{caseId}/rate` — body: `{ agent_id, rating (1-5), review_text? }` — rate a solved case
  - `GET /api/users/leaderboard` — returns top 50 agents by score, with filters: `?period=weekly|monthly|alltime`
  - `GET /api/users/cases/{caseId}/ratings` — returns average rating and reviews for a case
  - `GET /api/users/stats/global` — returns platform stats: total agents, total cases solved, average rating

### Task 8.2 — Vue.js Public Site Build-Out

- Expand the public site with real data from APIs:
  - **Hero Section**: Animated typing effect "Can You Solve What They Couldn't?" with a terminal-style CTA button that links to the Angular app
  - **Featured Cases**: Pull top-rated cases from the API. Show case cards with title, difficulty, mood tags, average rating, and solve count. Make these visually appealing with dark card designs and mood-colored accents
  - **Leaderboard**: Show top 10 agents with ranks, avatars (ASCII art), and stats
  - **How It Works**: Three-step visual guide — "1. Pick a Case → 2. Investigate → 3. Solve" with terminal-styled illustrations
  - **Platform Stats**: Animated counters showing total agents, cases solved, etc.
  - **Footer**: Links to GitHub repo, tech stack badges
- Use Vue Router for `/`, `/leaderboard`, `/cases` (public case browse — read-only)
- Make it responsive — should look great on mobile too
- Use Pinia for state management

**Acceptance:** Public site displays real data, looks polished, and provides a compelling entry point to the platform.

### Task 8.3 — Community Case Prompts (Stretch Feature)

- Allow users to submit case "seeds" — a title, setting description, mood, and optional image
- Store these as `CasePrompt` entities
- Community can vote on prompts
- Top-voted prompts get AI-generated into full playable cases via the generation engine
- This is a stretch goal — implement only if time permits

**Acceptance:** Users can submit and vote on case prompts. Top prompts can be auto-generated into cases.

---

## PHASE 9 — Book & Media Recommendations (RAG)

**Goal:** After solving a case, users get AI-powered recommendations for books, podcasts, and shows that match the mood of their mystery.

### Task 9.1 — Recommendation Database & Embeddings

- Create a curated dataset in `ai-service/app/seed/media_catalog.py` with 50-100 entries:
  - Books (mystery/thriller/horror — title, author, description, mood_tags, genre_tags)
  - Podcasts (true crime, mystery fiction — title, description, mood_tags)
  - TV shows/movies (mystery/thriller — title, description, mood_tags)
- Generate embeddings for each entry's description + mood tags using a free HuggingFace embedding model (e.g., `sentence-transformers/all-MiniLM-L6-v2`)
- Store embeddings — either in PostgreSQL with pgvector extension, or in a simple FAISS index saved to disk
- This is a classic RAG (Retrieval-Augmented Generation) setup

### Task 9.2 — Recommendation Engine

- In `services/recommendation_engine.py`:
  - Given a solved case's mood tags and setting description, generate an embedding
  - Perform similarity search against the media catalog embeddings
  - Return top 5 recommendations with similarity scores
  - Use LangChain to generate a personalized recommendation blurb: "You enjoyed the foggy coastal noir of The Lake House? You'd love..."
- In `routers/recommendations.py`:
  - `GET /api/ai/recommendations/{case_id}` — returns recommendations based on case mood

### Task 9.3 — Recommendations UI (Angular)

- After the case solve reveal, add a section:
  ```
  > BASED ON YOUR INVESTIGATION STYLE AND THIS CASE'S ATMOSPHERE:
  > RECOMMENDED MEDIA:
  >
  > [BOOK] "The Lighthouse Witches" by C.J. Cooke
  >        Mood Match: 92% | Genre: Gothic Mystery
  >        "If the lakeside isolation resonated with you..."
  >
  > [PODCAST] "The Left Right Game"
  >           Mood Match: 87% | Genre: Horror Fiction
  >           "For that same sense of creeping dread..."
  >
  > [SHOW] "Broadchurch"
  >        Mood Match: 85% | Genre: Crime Drama
  >        "Small-town secrets, coastal atmosphere..."
  ```

**Acceptance:** After solving a case, relevant media recommendations appear based on case mood. RAG pipeline works correctly.

---

## PHASE 10 — Polish, Deploy & Documentation

**Goal:** Production-ready deployment, polished UX, comprehensive documentation.

### Task 10.1 — UI Polish

- Add CRT screen effects toggle (some users might find scanlines annoying)
- Add terminal color theme selector: Classic Green, Amber Glow, Blue Ice, Red Alert
- Add sound effects toggle with ambient terminal hum (optional — use a small royalty-free audio file)
- Add screen transition effects between major views (brief static/glitch)
- Add loading states for all API calls (terminal-style progress indicators)
- Responsive design — terminal should work on mobile (adjust font size, simplify layouts)
- Add keyboard navigation — Enter to confirm, Escape to go back, number keys for menu selection
- Add an "ABOUT" terminal command showing the tech stack as an ASCII art diagram

### Task 10.2 — Error Handling & Resilience

- Gateway: Add retry policies for inter-service calls (Polly in .NET)
- Gateway: Add circuit breaker pattern for AI service calls
- All services: Structured logging with correlation IDs
- All services: Proper error responses in terminal aesthetic: `> ERROR: System malfunction. Please try again. [ERROR CODE: 5XX]`
- Frontend: Global error handler that displays terminal-style error messages
- Add rate limiting on interrogation endpoints (prevent API abuse)

### Task 10.3 — Deployment Configuration

- Create production `docker-compose.prod.yml` with:
  - Environment variable management
  - Volume mounts for persistent data
  - Resource limits per container
  - Production database configuration
- Option A — Railway: Create `railway.toml` configs for each service
- Option B — Fly.io: Create `fly.toml` configs for each service
- Option C — DigitalOcean: Docker Compose on a single droplet (cheapest)
- Set up environment variables: JWT secret, HuggingFace API token, database credentials
- Add SSL/HTTPS configuration via nginx or the platform's built-in SSL
- Configure a custom domain (optional)

### Task 10.4 — Comprehensive README

- Update the root `README.md` with:
  - Project name with ASCII art logo
  - Animated GIF or screenshot of the terminal UI
  - Project description and features list
  - Architecture diagram (Mermaid or ASCII)
  - Tech stack with version badges
  - Getting started guide (prerequisites, clone, docker compose up)
  - Individual service documentation links
  - API documentation links (Swagger URLs)
  - Contributing guidelines
  - License (MIT)
- Create individual `README.md` files in each service directory with service-specific setup instructions
- Add API documentation via Swagger (gateway), Springdoc (user-service), and FastAPI auto-docs (ai-service)

### Task 10.5 — GitHub Profile Optimization

- Add relevant GitHub topics to the repo: `microservices`, `langchain`, `angular`, `spring-boot`, `dotnet`, `fastapi`, `vue`, `docker`, `ai`, `mystery-game`, `portfolio-project`
- Create GitHub Issues for future enhancements (shows project planning)
- Create a GitHub Project board with phases as milestones

**Acceptance:** Project is deployed, accessible via URL, all documentation complete, repo is portfolio-ready.

---

## Technical Decisions Summary

- **LLM Provider**: HuggingFace Inference API (free tier) with Mistral-7B-Instruct as primary model. LangChain abstracts this so swapping models later is trivial.
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` via HuggingFace (free)
- **Image Analysis**: BLIP or CLIP via HuggingFace Inference API (free)
- **Database**: PostgreSQL 16 with separate schemas per service. pgvector extension for embeddings.
- **Caching**: Redis for conversation memory, session data, and frequently accessed case data.
- **Messaging**: RabbitMQ for async tasks (forensics processing, case generation, notifications).
- **Real-time**: SignalR in the .NET gateway for push notifications.
- **Auth**: JWT tokens generated by the gateway, validated across services.
- **Testing**: xUnit (.NET), JUnit + Mockito (Java), pytest (Python), Jasmine/Karma (Angular), Vitest (Vue)

---

## Claude Code Usage Notes

When working through this roadmap with Claude Code:

1. **Work phase by phase, task by task** — do not skip ahead.
2. **Verify each acceptance criteria** before moving to the next task.
3. **Run the relevant service** after each task to verify it works.
4. **Run tests** after implementing each task.
5. **Commit after each completed task** with a descriptive message like: `feat(gateway): add JWT authentication and auth endpoints [Phase 1, Task 1.1]`
6. **If a task requires changes across multiple services**, complete the backend first, then the frontend.
7. **Keep Docker Compose running** during development for infrastructure services.
8. **Use the dev compose file** (`docker-compose.dev.yml`) during development, not the full stack one.
9. If you encounter version conflicts or deprecations, prefer the latest stable version of any library.
10. Always add proper error handling — never leave happy-path-only code.
