# Complexity Analyzer Web App

A modern, dark-themed web interface for the Complexity Analyzer project.

## Features

- **Code Editor**: Syntax-highlighted editor for writing and modifying algorithms.
- **Complexity Analysis**: Real-time display of Big-O, Big-Omega, and Big-Theta complexity.
- **Reasoning Trace**: Step-by-step explanation of how the complexity was derived.
- **Example Library**: A sidebar containing 18+ example algorithms including:
  - Sorting (Insertion, Merge, Quick, Heap, Bubble, Selection)
  - Searching (Binary, Linear)
  - Mathematics (Factorial, Fibonacci, GCD, Prime Check, Matrix Mult, Power)
  - Recursion (Tower of Hanoi, Sum Array)

## Setup

1.  **Install Dependencies**:
    ```bash
    npm install
    ```

2.  **Run Development Server**:
    ```bash
    npm run dev
    ```

3.  **Backend Requirement**:
    Ensure the Python backend is running on port 8000:
    ```bash
    # From the root directory
    python -m uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8000
    ```
