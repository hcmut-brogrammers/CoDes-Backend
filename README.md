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

## Running the Project

To start the FastAPI application, use the command:

```bash
fastapi dev main.py
```

The application should now be running. Access the API documentation at:

```
http://127.0.0.1:8000/docs
```

## Additional Information

- FastAPI packages are put in requirements.txt
- Modify `main.py` as needed to customize the application.

Happy coding! 🚀
