# Contributing

Contributions are welcome and appreciated! Here's how to get involved.

---

## Reporting Bugs

When reporting a bug, please include:

- Your OS name and version
- Your Python version (`python --version`)
- Steps to reproduce the issue
- The full error traceback

---

## Setting Up for Development

1. Clone the repo:

    ```bash
    git clone https://github.com/byuirpytooling/slapyshot.git
    cd slapyshot
    ```

2. Install dependencies with `uv`:

    ```bash
    uv sync
    ```

3. Create a `.env` file with your API key:

    ```bash
    SPORTRADAR_API_KEY=your_key_here
    ```

4. Run the tests:

    ```bash
    uv run pytest tests/ -v
    ```

---

## Making Changes

1. Create a branch:

    ```bash
    git checkout -b my-feature-or-fix
    ```

2. Make your changes and add tests where appropriate
3. Run the full test suite before opening a PR:

    ```bash
    uv run pytest tests/ -v
    ```

4. Open a pull request against `main`

---

## Code of Conduct

Please note that this project is released with a [Code of Conduct](https://github.com/byuirpytooling/slapyshot/blob/main/CONDUCT.md). By contributing you agree to abide by its terms.