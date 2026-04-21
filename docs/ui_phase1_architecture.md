# UI Phase 1 Architecture

## Objective

Create a premium frontend foundation without duplicating Tarot engine logic.

## Recommended split

- **Python backend**: source of truth for rules, simulation, inference, and recommendation
- **HTTP API**: stable transport contract for web clients
- **Vue 3 frontend**: presentation, interaction, and state orchestration only

## Backend additions in Phase 1

- `src/tarot_engine/api/app.py`
- `src/tarot_engine/api/schemas.py`
- `src/tarot_engine/api/mappers.py`

### API routes

- `GET /api/v1/health`
- `GET /api/v1/meta/contracts`
- `POST /api/v1/contracts/evaluate`
- `POST /api/v1/moves/recommend`

## Frontend additions in Phase 1

- `frontend/` created as a dedicated Vue 3 + TypeScript app
- Vite + Vue Router + Pinia + Tailwind initialized
- app shell and route placeholders created for:
  - setup
  - current game state
  - recommendation
  - analysis

## Architectural rules

1. No Tarot decision logic in the frontend.
2. No direct imports from Python into the UI layer.
3. HTTP schemas stay separate from internal application DTOs.
4. Frontend uses a typed API client layer (`src/lib/api.ts`).
5. UI components are split by layout / presentation / domain view.

## Next recommended UI step

Phase 2 UI should build the real setup flow:
- visual card picker
- contract/role selectors
- form validation
- API connectivity test
- initial recommendation submission flow
