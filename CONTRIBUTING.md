# Contributing to Yoosee Local Cloud

Thank you for your interest in contributing! We welcome contributions to make Yoosee / Gwelltimes IP cameras 100% cloud-free, secure, and integrated into local home automation systems.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/joaorura/yoosee-local-cloud.git
   cd yoosee-local-cloud
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt -r requirements-dev.txt
   ```

3. Run the test suite:
   ```bash
   pytest -v --cov=yoosee_local
   ```

## Development Guidelines

- **Test-Driven Development (TDD):** We strictly follow the Red-Green-Refactor loop. Every new feature, bug fix, or protocol handler must start with a failing test.
- **Code Style:** We use `ruff` and `black` for formatting.
  ```bash
  ruff check .
  black --check .
  ```
- **Commits:** We follow Conventional Commits:
  - `feat(scope): ...`
  - `fix(scope): ...`
  - `test(scope): ...`
  - `docs(scope): ...`

## Submitting Pull Requests

1. Fork the repo and create your branch from `main`.
2. Ensure all tests pass and coverage remains above 90%.
3. Open a Pull Request referencing any related issues.
