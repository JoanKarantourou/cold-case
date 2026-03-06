# ColdCase AI

An AI-powered interactive mystery investigation platform styled as a retro FBI terminal.

```
   ██████╗ ██████╗ ██╗     ██████╗  ██████╗ █████╗ ███████╗███████╗     █████╗ ██╗
  ██╔════╝██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝    ██╔══██╗██║
  ██║     ██║   ██║██║     ██║  ██║██║     ███████║███████╗█████╗      ███████║██║
  ██║     ██║   ██║██║     ██║  ██║██║     ██╔══██║╚════██║██╔══╝      ██╔══██║██║
  ╚██████╗╚██████╔╝███████╗██████╔╝╚██████╗██║  ██║███████║███████╗    ██║  ██║██║
   ╚═════╝ ╚═════╝ ╚══════╝╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝  ╚═╝╚═╝
```

> Connect to the classified cold case database. Pick a case. Interrogate suspects. Solve the mystery.

## Features

- Retro CRT terminal UI with scanline effects and typewriter animations
- AI-powered suspect interrogation using LangChain
- Interactive evidence board with drag-and-drop
- Mood-based case matching via image analysis
- Forensics lab with async processing
- Book & media recommendations after solving cases
- Community features and leaderboards

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────>│   Gateway    │────>│ User Service │
│  Angular 17  │     │   .NET 8     │     │ Spring Boot 3│
│  port: 4200  │     │  port: 5000  │     │  port: 8080  │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
┌──────────────┐            │              ┌──────────────┐
│ Public Site  │            └─────────────>│  AI Service  │
│   Vue.js 3   │                           │   FastAPI    │
│  port: 5173  │                           │  port: 8000  │
└──────────────┘                           └──────────────┘
                    ┌──────────────────────────────┐
                    │       Infrastructure          │
                    │  PostgreSQL | RabbitMQ | Redis │
                    └──────────────────────────────┘
```

## Tech Stack

- **Gateway**: .NET 8 (C#) — YARP reverse proxy, JWT auth, SignalR
- **User Service**: Java 21 / Spring Boot 3 — User management, progress tracking
- **AI Service**: Python 3.12 / FastAPI — LangChain, HuggingFace, case generation
- **Frontend**: Angular 17+ — Terminal investigation UI
- **Public Site**: Vue.js 3 — Landing page and community showcase
- **Infrastructure**: Docker Compose, PostgreSQL 16, RabbitMQ, Redis

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 20+
- .NET 8 SDK
- Java 21
- Python 3.12+

### Quick Start

```bash
# Clone the repository
git clone https://github.com/JoanKarantourou/cold-case.git
cd cold-case

# Start infrastructure services
docker compose -f docker-compose.dev.yml up -d

# Start individual services (see each service's README for details)
```

## Project Structure

```
cold-case/
├── gateway/                 # .NET 8 API Gateway
├── user-service/            # Java / Spring Boot 3
├── ai-service/              # Python / FastAPI
├── frontend/                # Angular 17+
├── public-site/             # Vue.js 3
├── infrastructure/          # Docker, DB init, nginx
├── .github/workflows/       # CI/CD pipelines
├── docker-compose.yml       # Full stack orchestration
└── docker-compose.dev.yml   # Development infrastructure
```

## License

MIT
