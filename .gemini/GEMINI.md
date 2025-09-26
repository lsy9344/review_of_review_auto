### Project Overview

This is a Python-based desktop application designed to automate the process of replying to reviews on Na이버 Smart Place. It features a graphical user interface built with PySide6 (Qt for Python).

The core functionality involves:
1.  **Secure Login:** Logging into Naver, with cookie reuse for subsequent sessions.
2.  **Review Crawling:** Automatically collecting new reviews that have not been replied to.
3.  **AI-Powered Replies:** Utilizing the OpenAI GPT API to generate natural and context-aware replies.
4.  **Browser Automation:** Using Playwright to interact with the Naver Smart Place website for submitting replies.
5.  **Flexible Operation Modes:** Offering `DryRun` (preview), `Assist` (semi-auto), and `Auto` (fully-automatic) modes.
6.  **Monitoring:** Providing a real-time log and progress display within the UI.

The architecture is modular, separating the UI (`app/ui`), core services (`app/services`), and application logic (`app/main.py`). Configuration is managed through `.yaml` files, and data is stored in a local SQLite database.

### Building and Running

**1. Environment Setup:**

```bash
# 1. Create and activate a Python virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set the required environment variable for the OpenAI API
export OPENAI_API_KEY='your_openai_api_key_here'
```

**2. Running the Application:**

*   **Standard Mode:**
    To run the application for normal use.
    ```bash
    python run.py
    ```

*   **Development Mode:**
    To run the application with live-reloading. The application will automatically restart when files in the `app/` directory are changed.
    ```bash
    python dev.py
    ```

### Development Conventions

*   **Code Style:** The project uses `black` for code formatting and `isort` for import sorting. Linting is performed with `ruff`. Configurations are defined in `project.toml`.
*   **Entry Points:**
    *   `run.py`: The main entry point for the production application.
    *   `dev.py`: The entry point for development, which enables auto-restarting.
*   **Testing:** Tests are written using the `pytest` framework. They can be run automatically in development mode:
    ```bash
    python dev.py --command "python -m pytest"
    ```
*   **Dependencies:** Python dependencies are managed in `requirements.txt`. There is also a `package.json` for Node.js-based development tools.
*   **Documentation:** The project contains extensive documentation in the `docs/` directory, including `ARCHITECTURE.md` and `DEVELOPMENT.md`.


### Research → Plan → Implement
**NEVER JUMP STRAIGHT TO CODING!** Always follow this sequence:
1. **Research**: Explore the codebase, understand existing patterns
2. **Plan**: Create a detailed implementation plan and verify it with me 
3. **Implement**: Execute the plan with validation checkpoints

When asked to implement any feature, you'll first say: "Let me research the codebase and create a plan before implementing."