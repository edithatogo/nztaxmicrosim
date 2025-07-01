# Contributing to NZ Microsimulation Model

We welcome contributions to the NZ Microsimulation Model! By contributing, you help us create a more transparent, accessible, and extensible model for New Zealand's tax and transfer system.

## How to Contribute

### 1. Fork and Clone the Repository

First, fork this repository to your own GitHub account. Then, clone your forked repository to your local machine:

```bash
git clone https://github.com/your-username/irdmicrosim.git
cd irdmicrosim
```

### 2. Set Up Your Development Environment

This project uses `pyproject.toml` for dependency management. We recommend using a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
pip install -e .
```

### 3. Install Pre-commit Hooks

We use [pre-commit](https://pre-commit.com/) to ensure code quality and consistency. Install the hooks by running:

```bash
pre-commit install
```

These hooks will automatically run `ruff` checks and formatting on your staged files before each commit.

### 4. Make Your Changes

Create a new branch for your feature or bug fix:

```bash
git checkout -b feature/your-feature-name
```

Implement your changes. Remember to follow the existing code style and conventions.

### 5. Run Tests

Ensure your changes haven't introduced any regressions by running the test suite:

```bash
pytest
```

### 6. Lint and Format Your Code

Before committing, ensure your code adheres to the project's linting and formatting standards using [Ruff](https://beta.ruff.rs/docs/):

```bash
ruff check .
ruff format .
```

To automatically fix most linting issues, run:

```bash
ruff check . --fix
```

### 7. Commit Your Changes

Commit your changes with a clear and concise commit message. The pre-commit hooks will run automatically at this stage.

```bash
git add .
git commit -m "feat: Add a new feature" # or "fix: Fix a bug"
```

### 8. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 9. Create a Pull Request

Go to the original repository on GitHub and open a pull request from your forked branch to the `main` branch. Provide a clear description of your changes and reference any relevant issues.

Thank you for contributing!
