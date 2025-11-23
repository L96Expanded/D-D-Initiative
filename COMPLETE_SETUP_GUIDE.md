# Complete Setup Guide: From Scratch to Running Tests

This guide walks you through setting up the entire project and running tests successfully.

## Part 1: Initial Setup

### Step 1: Install Prerequisites

**Windows:**
```powershell
# Install Python 3.11 from python.org
# Install Docker Desktop from docker.com
# Install Git from git-scm.com
```

**Verify installations:**
```bash
python --version  # Should be 3.11+
docker --version
git --version
```

### Step 2: Clone and Navigate

```bash
cd "c:\Users\david\OneDrive\Documents\School\DevOps\DnD_Initiative_Project\D-D-Initiative"
```

### Step 3: Create Virtual Environment

```bash
cd backend
python -m venv .venv
```

### Step 4: Activate Virtual Environment

**Every time you work on the project:**
```bash
# Windows PowerShell:
.venv\Scripts\activate

# Windows CMD:
.venv\Scripts\activate.bat

# Linux/Mac:
source .venv/bin/activate
```

You should see `(.venv)` at the start of your command prompt.

### Step 5: Install All Dependencies

```bash
# Make sure you're in backend/ directory with venv activated
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

This installs:
- FastAPI, SQLAlchemy (production dependencies)
- pytest, pytest-cov (testing)
- prometheus-client (monitoring)
- flake8, black, mypy (code quality)

## Part 2: Understanding the Test Structure

### Test Files Created

```
backend/tests/
├── __init__.py                 # Makes tests a package
├── conftest.py                 # Shared fixtures (sample data, test client)
├── test_models.py              # Tests for database models
├── test_auth_utils.py          # Tests for authentication
└── test_api_integration.py     # Tests for API endpoints
```

### What Each File Does

**conftest.py**: Sets up testing infrastructure
- Creates in-memory test database
- Provides test client for API calls
- Defines reusable test data (sample users, creatures)

**test_models.py**: Unit tests for database models
- Tests User, Creature, Encounter models
- Verifies relationships and constraints

**test_auth_utils.py**: Unit tests for authentication
- Password hashing/verification
- JWT token creation/validation
- Input validation (username, email, password)

**test_api_integration.py**: Integration tests for API
- User registration and login
- CRUD operations for creatures
- CRUD operations for encounters
- Authorization checks

## Part 3: Running Tests Step by Step

### Command 1: Run All Tests

```bash
# Make sure you're in backend/ with venv activated
pytest tests/ -v
```

**Expected output:**
```
tests/test_models.py::TestUserModel::test_user_creation PASSED
tests/test_models.py::TestUserModel::test_user_unique_username PASSED
... more tests ...
======================== XX passed in X.XXs ========================
```

### Command 2: Run Tests with Coverage

```bash
pytest tests/ -v --cov=app --cov-report=term
```

**Expected output:**
```
----------- coverage: platform win32, python 3.11.x -----------
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
app/__init__.py                         0      0   100%
app/models/models.py                  120     24    80%
app/utils/auth.py                      45      5    89%
... more files ...
--------------------------------------------------------
TOTAL                                 450    135    70%
```

### Command 3: Generate HTML Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html
```

Then open: `backend/htmlcov/index.html` in your browser

**What you'll see:**
- Green lines: Covered by tests ✅
- Red lines: Not covered ❌
- Percentage for each file

### Command 4: Verify 70% Coverage Threshold

```bash
pytest tests/ --cov=app --cov-fail-under=70
```

**If coverage is ≥70%:**
```
======================== XX passed in X.XXs ========================
```

**If coverage is <70%:**
```
FAIL Required test coverage of 70% not reached. Total coverage: 65.32%
```

### Command 5: Run Specific Test Categories

```bash
# Only unit tests
pytest tests/ -m "unit" -v

# Only integration tests
pytest tests/ -m "integration" -v

# Specific test file
pytest tests/test_models.py -v

# Specific test function
pytest tests/test_models.py::TestUserModel::test_user_creation -v
```

## Part 4: Understanding Test Results

### Reading Test Output

```
tests/test_models.py::TestUserModel::test_user_creation PASSED [10%]
│                    │                │                   │       │
│                    │                │                   │       └─ Progress
│                    │                │                   └─ Result (PASSED/FAILED)
│                    │                │
│                    │                └─ Test function name
│                    └─ Test class name
└─ Test file
```

### Common Test Statuses

- `PASSED`: Test succeeded ✅
- `FAILED`: Test failed - shows error details ❌
- `SKIPPED`: Test was skipped
- `ERROR`: Test had an error before running

### Coverage Percentages

- **90-100%**: Excellent coverage ⭐⭐⭐
- **70-89%**: Good coverage ⭐⭐
- **50-69%**: Adequate coverage ⭐
- **<50%**: Poor coverage ⚠️

**Project requirement: ≥70%**

## Part 5: Troubleshooting

### Problem: "pytest: command not found"

**Solution:**
```bash
# Make sure virtual environment is activated
.venv\Scripts\activate

# If still not working, install pytest
pip install pytest pytest-cov
```

### Problem: "Import 'app' could not be resolved"

**Solution:**
```bash
# Make sure you're in the backend/ directory
cd backend

# Check if conftest.py has correct path setup
# conftest.py should add parent dir to sys.path
```

### Problem: "No tests ran"

**Check:**
```bash
# Are test files named correctly? (test_*.py)
# Are test functions named correctly? (test_*)
# Are you in the right directory?
pwd  # Should show .../backend/
```

### Problem: Coverage below 70%

**Steps to fix:**
```bash
# 1. Generate HTML report
pytest tests/ --cov=app --cov-report=html

# 2. Open htmlcov/index.html

# 3. Click on files with low coverage

# 4. Look for red lines (not tested)

# 5. Write tests for those lines

# 6. Re-run tests
pytest tests/ --cov=app --cov-fail-under=70
```

### Problem: Tests fail with database errors

**Solution:**
```bash
# Tests use in-memory SQLite, not your actual database
# Check conftest.py fixture setup
# Make sure app/models/database.py has proper imports
```

### Problem: Import errors for 'fastapi', 'sqlalchemy', etc.

**Solution:**
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify installation
pip list | grep fastapi
pip list | grep pytest
```

## Part 6: Integrating with CI/CD

### Local Pre-commit Check

Before pushing code, run:

```bash
# 1. Format code
black app/ tests/

# 2. Lint code
flake8 app/ --count --show-source --statistics

# 3. Run tests with coverage
pytest tests/ --cov=app --cov-fail-under=70

# If all pass, you're good to commit! ✅
```

### What Happens in CI Pipeline

When you push to GitHub:

1. ✅ Install dependencies
2. ✅ Run flake8 linting
3. ✅ Run mypy type checking
4. ✅ Run pytest with coverage
5. ✅ Verify coverage ≥70%
6. ✅ Upload coverage reports
7. ✅ Build Docker images (if main branch)
8. ✅ Deploy (if main branch)

**Pipeline fails if:**
- ❌ Any test fails
- ❌ Coverage < 70%
- ❌ Linting errors exist
- ❌ Build fails

## Part 7: Quick Reference

### Daily Development Workflow

```bash
# 1. Activate environment
cd backend
.venv\Scripts\activate

# 2. Make code changes
# ... edit files ...

# 3. Run tests
pytest tests/ -v --cov=app

# 4. Fix any failures
# ... edit more ...

# 5. Verify coverage
pytest tests/ --cov=app --cov-fail-under=70

# 6. Commit and push
git add .
git commit -m "Your message"
git push
```

### Essential Commands

```bash
# Full test run with coverage report
pytest tests/ -v --cov=app --cov-report=html --cov-report=term --cov-fail-under=70

# Quick test (no coverage)
pytest tests/ -v

# Watch mode (re-run on file changes)
pytest-watch tests/

# Specific test
pytest tests/test_models.py::TestUserModel::test_user_creation -v -s
```

### Files You'll Modify

When adding features:
1. Write code in `app/`
2. Write tests in `tests/`
3. Run tests: `pytest tests/`
4. Check coverage: open `htmlcov/index.html`
5. Add tests until coverage ≥70%

### Getting Help

```bash
# Pytest help
pytest --help

# List all tests without running
pytest tests/ --collect-only

# Show available markers (unit, integration)
pytest --markers

# Verbose output with print statements
pytest tests/ -v -s
```

## Part 8: Advanced Testing

### Running Tests with Different Options

```bash
# Stop at first failure
pytest tests/ -x

# Show local variables in traceback
pytest tests/ -l

# Run tests in parallel (faster)
pytest tests/ -n auto  # requires pytest-xdist

# Only run failed tests from last run
pytest tests/ --lf

# Run tests that failed last time first
pytest tests/ --ff
```

### Debugging Tests

```bash
# Drop into debugger on failure
pytest tests/ --pdb

# Show print statements
pytest tests/ -s

# Very verbose
pytest tests/ -vv
```

---

## Summary Checklist

Before submitting your project:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage ≥70%: `pytest tests/ --cov=app --cov-fail-under=70`
- [ ] HTML report generated: `htmlcov/index.html` exists
- [ ] No linting errors: `flake8 app/`
- [ ] Code formatted: `black app/ tests/`
- [ ] CI/CD pipeline configured: `.github/workflows/ci-cd.yml` exists
- [ ] Documentation updated: `REPORT.md` and `DEVELOPMENT_GUIDE.md`
- [ ] Health endpoint working: curl http://localhost:8000/api/health
- [ ] Metrics endpoint working: curl http://localhost:8000/api/metrics

---

**If you can run this command successfully, you're ready:**

```bash
cd backend
.venv\Scripts\activate
pytest tests/ -v --cov=app --cov-report=html --cov-report=term --cov-fail-under=70
```

Expected: All tests pass, coverage ≥70% ✅
