# Quick Start: Running Tests

## Setup (One-time)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# OR
source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Run All Tests

```bash
cd backend
.venv\Scripts\activate  # Make sure venv is activated
pytest tests/ -v --cov=app --cov-report=html --cov-report=term --cov-fail-under=70
```

## View Coverage Report

Open in browser: `backend/htmlcov/index.html`

## Quick Test Commands

```bash
# Run only unit tests
pytest tests/ -m "unit"

# Run only integration tests  
pytest tests/ -m "integration"

# Run specific file
pytest tests/test_models.py -v

# Fast run (no coverage)
pytest tests/ -v
```

## Verify 70% Coverage

```bash
pytest tests/ --cov=app --cov-fail-under=70
```

✅ If this passes, your coverage meets requirements!

## Common Issues

**"Import pytest could not be resolved"**
→ Activate virtual environment: `.venv\Scripts\activate`

**"No module named 'app'"**
→ Run from `backend/` directory

**Coverage below 70%**
→ Run with HTML report and add tests for red lines:
```bash
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html
```
