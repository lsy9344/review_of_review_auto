# Project Context: Naver SmartPlace Review Auto-Reply Bot

- 항상 한국어로 대답하세요.

### Research → Plan → Implement
**NEVER JUMP STRAIGHT TO CODING!** Always follow this sequence:
1. **Research**: Explore the codebase, understand existing patterns
2. **Plan**: Create a detailed implementation plan and verify it with me 
3. **Implement**: Execute the plan with validation checkpoints

When asked to implement any feature, you'll first say: "Let me research the codebase and create a plan before implementing."

## Project Overview

This is a Windows desktop application designed to automatically (or semi-automatically) respond to reviews on Naver SmartPlace. The application targets reviews that don't have owner replies, with a maximum of 10 responses per run. 

Key features include:
- Windows environment operation
- Headed automation (visible browser actions) using Playwright
- LLM-powered response generation based on user-defined prompts/tone
- Selector abstraction layer for DOM change resilience
- Safety mechanisms (review limits, speed throttling, CAPTCHA handling)
- Single executable (.exe) deployment

## Technologies & Architecture

### Core Stack
- **Language**: Python 3.11+
- **UI Framework**: PySide6
- **Automation Engine**: Playwright (Chromium, Headed)
- **Database**: SQLite
- **LLM Provider**: OpenAI API (gpt-4o-mini by default)
- **Packaging**: PyInstaller (for .exe creation)

### Architecture Components
1. **UI Layer**: Execution/stop controls, prompt input, progress bar, log viewer
2. **Controller**: State machine managing execution flow and interrupts
3. **Automation Engine**: Playwright driver with selector registry and stabilization waits
4. **LLM Service**: Client abstraction with OpenAI implementation, prompt builder with constraints
5. **Configuration**: YAML config loader/validator, environment variable secrets
6. **Storage**: SQLite database for deduplication and run logging
7. **Logging/Reporting**: Structured logging and execution summary reports

### Data Flow
1. Load configuration → Prepare browser session → Login/cookie restoration
2. Select store → Enter reviews tab → Collect reviews (with pagination)
3. Filter unreplied reviews → Queue up to 10 items
4. Generate prompts → Call LLM → Refine drafts (length/banned words)
5. Submit via assist/auto mode → Verify via DOM/toast
6. Store/log/report updates → Exit/error recovery

## Project Structure (Planned)

```
review_reply_auto/
  app/
    core/              # Configuration, errors, events, state, logging
    domain/            # Data models, prompts, selectors
    infra/             # Browser automation, LLM clients, database
    services/          # Business logic services
    ui/                # UI components and view models
    runner.py          # Orchestrator entry point
    main.py            # Application entry point
  configs/             # Configuration files
  assets/              # Icons, prompt samples
  tests/               # Unit and end-to-end tests
  docs/                # Documentation
```

## Configuration Files

### config.yaml
Main configuration file controlling:
- `run_mode`: dryrun | assist | auto
- `max_reviews_per_run`: 1-10 (capped at 10)
- `store_selection`: first | name | id | all
- `llm` settings: provider, model, API key environment variable
- `reply_style`: tone, length_limit, banned_words, closing template
- `selectors_profile`: default profile name

### selectors.yaml
Selector abstraction file mapping logical keys to CSS/XPath selectors:
- Login elements (id_input, pw_input, submit_btn)
- Navigation elements (store_list, first_store, review_tab_btn)
- Review elements (item, text, has_owner_reply, reply_button, etc.)
- Pagination controls

## Data Model (SQLite)

- `stores`: store_id (PK), name
- `reviews`: review_id, store_id, created_at, rating, text, has_owner_reply (unique constraint on review_id, store_id)
- `submissions`: review_id, store_id, status, error, created_at
- `runs`: run_id (PK), started_at, mode, success count, fail count, skipped count

## Development Guidelines

### Implementation Approach
1. Follow the planned directory structure
2. Implement features in order of the task list (login → store selection → review parsing → LLM integration → submission)
3. Use abstraction layers for better maintainability
4. Implement proper error handling and logging
5. Include safety mechanisms (speed limits, interrupt handling)
6. Write unit and end-to-end tests

### Code Quality Standards
- Functions should be 30-50 lines max with single responsibility
- Use interface-first design for replaceable components
- External dependencies should be minimized
- Deterministic behavior with parameterized randomness
- Clear exception messages with recovery guidance
- Structured logging with JSON context
- PII masking in logs when applicable

### Testing Strategy
- Unit tests for parsing, prompting, validation logic
- End-to-end tests for core workflows
- Test accuracy of review collection (≥90% target)
- Verify submission success with DOM change detection
- Regression testing for selector changes

## Build and Deployment

### Development Setup
1. Create virtual environment with Python 3.11+
2. Install dependencies from requirements.txt
3. Set up OpenAI API key in environment variables

### Building Executable
1. Use PyInstaller to create single .exe file
2. Include config.yaml and selectors.yaml in distribution
3. Package prompt samples and documentation

### Running the Application
1. Ensure OpenAI API key is set in environment variables
2. Configure config.yaml and selectors.yaml as needed
3. Run the executable directly (no installation required)

## Key Implementation Tasks

1. Login/session management with cookie reuse and manual 2FA support
2. Store selection and reviews tab navigation
3. Selector profile loader with fallback mechanism
4. Review parser with pagination support
5. Unreplied review filter and queue builder (max 10 items)
6. LLM client with prompt builder and retry logic
7. Response constraint enforcement (length, banned words, tone)
8. Submission executor for assist/auto modes
9. Stop button interrupt handling
10. Logging and reporting system
11. SQLite storage with deduplication
12. Configuration loader with validation
13. Packaging into single executable

This project requires careful attention to:
- DOM stability and selector abstraction
- LLM response quality and constraint enforcement
- User safety with speed limits and interrupt handling
- Error recovery and informative logging
- Cross-platform compatibility (Windows target)

## Qwen Added Memories
- 항상 한국어로 대답하세요.
- Research → Plan → Implement
**NEVER JUMP STRAIGHT TO CODING!** Always follow this sequence:
1. **Research**: Explore the codebase, understand existing patterns
2. **Plan**: Create a detailed implementation plan and verify it with me 
3. **Implement**: Execute the plan with validation checkpoints

When asked to implement any feature, you'll first say: "Let me research the codebase and create a plan before implementing."
