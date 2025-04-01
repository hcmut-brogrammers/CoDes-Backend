# FastAPI Backend

This repository contains a FastAPI backend. Follow the instructions below to set up and run the project.

## Setup

### 1. Create a Virtual Environment

Run the following command to create a virtual environment:

```bash
python -m venv .venv
```

#### Activate the Virtual Environment

- **MacOS/Linux**:
  ```bash
  source .venv/bin/activate
  ```
- **Windows (Bash)**:
  ```bash
  source .venv/Scripts/activate
  ```

### 2. Verify Virtual Environment Activation

To check if the virtual environment is active, run:

```bash
which python  # MacOS/Linux
```

Expected output:

```
/home/user/code/awesome-project/.venv/bin/python
```

### 3. Upgrade Pip and Install Dependencies

Run the following commands:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Node.js Dependencies

To install the required Node.js dependencies listed in `package.json`, run the following command:

```bash
yarn install
```

This will install all dependencies and devDependencies specified in the `package.json` file.

## Running the Project

To start the FastAPI application, use the command:

```bash
fastapi dev main.py
```

The application should now be running. Access the API documentation at:

```
http://127.0.0.1:8000/docs
```

## Running Unit Tests

To run the unit tests using pytest, execute the following command:

```bash
pytest
```

This will discover and run all test files in the project. Ensure that the virtual environment is activated before running the tests.

For more detailed output, use:

```bash
pytest -v
```

To run a specific test file, provide the file path:

```bash
pytest path/to/test_file.py
```

## Checking Test Coverage

To measure test coverage using pytest, install the `pytest-cov` plugin if not already installed:

```bash
pip install pytest-cov
```

Run the tests with coverage enabled:

```bash
pytest --cov=src
```

This will display a summary of the test coverage in the terminal. To generate a detailed HTML report, use:

```bash
pytest --cov=src --cov-report=html
```

The HTML report will be saved in a `htmlcov` directory. Open `htmlcov/index.html` in a browser to view the detailed coverage report.

## Formatting

To ensure consistent import formatting across the project, install the `isort` extension for Python in Visual Studio Code:

[Install isort Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.isort)

After installation, you can format imports in your Python files by running the `Sort Imports` command in VS Code.

## Additional Information

- FastAPI packages are put in requirements.txt
- Modify `main.py` as needed to customize the application.

Happy coding! 🚀
Happy testing! 🧪
