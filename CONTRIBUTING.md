# Contributing to D&D Initiative Tracker

Thank you for your interest in contributing! This document provides guidelines for setting up the development environment and contributing to the project.

## 🚀 Getting Started

### Prerequisites

- **Git**: [Install Git](https://git-scm.com/downloads)
- **Docker Desktop**: [Install Docker](https://www.docker.com/products/docker-desktop/)
- **Code Editor**: VS Code recommended with Docker and Python extensions

### Quick Setup

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/D-D-Initiative.git
   cd D-D-Initiative
   ```

2. **Run Automated Setup**
   
   **Windows:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File setup.ps1
   ```
   
   **Mac/Linux:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

## 🛠️ Development Workflow

### Project Structure

```
D-D-Initiative/
├── frontend/           # React + TypeScript frontend
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── pages/      # Page components
│   │   ├── utils/      # API client and utilities
│   │   └── types/      # TypeScript types
│   └── Dockerfile
├── backend/            # FastAPI + Python backend
│   ├── app/
│   │   ├── models/     # Database models and schemas
│   │   ├── routers/    # API endpoints
│   │   └── utils/      # Authentication and utilities
│   ├── tests/          # Test suite (pytest)
│   └── Dockerfile
├── .env.example        # Environment template
├── docker-compose.yml  # Docker configuration
└── setup.ps1/setup.sh  # Automated setup scripts
```

### Making Changes

#### Frontend Development

```bash
# Frontend runs in Docker, but you can develop locally:
cd frontend

# Install dependencies
npm install

# Run dev server (outside Docker)
npm run dev

# Or edit files and Docker will hot-reload
```

#### Backend Development

```bash
# Backend runs in Docker with live reload enabled
cd backend

# View logs
docker-compose logs -f backend

# Run tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=term-missing
```

### Running Tests

```bash
# Full test suite
cd backend
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=app --cov-report=html

# Specific test file
python -m pytest tests/test_encounters.py -v

# Test with output
python -m pytest tests/ -v -s
```

**Current Test Status:** 98/98 tests passing, 71%+ coverage

### Code Quality

```bash
# Backend linting
cd backend
pylint app/

# Frontend linting
cd frontend
npm run lint

# Type checking
npm run type-check
```

## 📝 Contribution Guidelines

### Before You Start

1. **Check existing issues** to avoid duplicate work
2. **Create an issue** for new features or bugs
3. **Discuss major changes** before implementing

### Making a Pull Request

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, commented code
   - Follow existing code style
   - Add tests for new features
   - Update documentation

3. **Test your changes**
   ```bash
   # Run all tests
   cd backend
   pytest tests/ -v
   
   # Verify Docker build
   docker-compose up --build
   ```

4. **Commit with clear messages**
   ```bash
   git add .
   git commit -m "feat: Add creature image auto-fetch feature
   
   - Implement D&D 5e API integration
   - Add image caching
   - Add fallback for missing images
   - Update tests
   "
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

### Commit Message Format

Follow conventional commits:

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: Add initiative auto-sort feature

fix: Resolve CORS error on production deployment

docs: Update QUICKSTART.md with Mac setup instructions

test: Add tests for creature image upload
```

## 🧪 Testing Guidelines

### Writing Tests

All new features must include tests:

```python
# backend/tests/test_your_feature.py

def test_your_feature(client, authenticated_headers):
    """Test description."""
    # Arrange
    data = {"key": "value"}
    
    # Act
    response = client.post("/api/endpoint", json=data, headers=authenticated_headers)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

### Test Coverage Requirements

- **Minimum coverage**: 70%
- **Aim for**: 80%+
- All new routes must have tests
- Critical features should have multiple test cases

## 🐛 Reporting Bugs

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Docker version, browser
6. **Logs**: Relevant error logs

**Example:**
```markdown
### Bug: Encounter not saving after edit

**Steps to Reproduce:**
1. Create a new encounter
2. Add 3 creatures
3. Edit encounter name
4. Click save
5. Refresh page

**Expected:** Encounter name should be updated
**Actual:** Encounter name reverts to original

**Environment:**
- OS: Windows 11
- Browser: Chrome 120
- Docker: 24.0.7

**Logs:**
```
[backend] ERROR: IntegrityError on encounter update
```
```

## 💡 Feature Requests

When suggesting features:

1. **Use Case**: Why is this feature needed?
2. **Expected Behavior**: How should it work?
3. **Mockups/Examples**: If applicable
4. **Alternatives Considered**: Other approaches

## 🎨 Code Style

### Python (Backend)

- Follow **PEP 8**
- Use **type hints**
- Maximum line length: 100 characters
- Use docstrings for functions/classes

```python
def create_encounter(
    encounter_data: EncounterCreate,
    user_id: int
) -> Encounter:
    """
    Create a new encounter for a user.
    
    Args:
        encounter_data: Encounter creation data
        user_id: ID of the user creating the encounter
        
    Returns:
        Created encounter instance
        
    Raises:
        ValueError: If encounter data is invalid
    """
    # Implementation
```

### TypeScript (Frontend)

- Use **TypeScript** (no `any` types)
- Follow **React best practices**
- Use functional components with hooks
- Maximum line length: 100 characters

```typescript
interface CreatureProps {
  creature: Creature;
  onUpdate: (creature: Creature) => void;
  onDelete: (id: string) => void;
}

export const CreatureCard: React.FC<CreatureProps> = ({
  creature,
  onUpdate,
  onDelete
}) => {
  // Implementation
};
```

## 🔒 Security

- **Never commit** `.env` files or secrets
- Use environment variables for sensitive data
- Validate all user input
- Report security issues privately to maintainers

## 📚 Documentation

Update documentation when:

- Adding new features
- Changing API endpoints
- Modifying setup procedures
- Fixing bugs that users might encounter

## ✅ Checklist Before Submitting PR

- [ ] Code follows project style guidelines
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Coverage is maintained or improved
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up to date with main
- [ ] Docker build succeeds (`docker-compose up --build`)
- [ ] No secrets or sensitive data in commits

## 🙏 Thank You!

Your contributions make this project better! Questions? Feel free to open an issue.

## 📞 Getting Help

- **Documentation**: [README.md](README.md) | [QUICKSTART.md](QUICKSTART.md)
- **Issues**: [GitHub Issues](https://github.com/L96Expanded/D-D-Initiative/issues)
- **Discussions**: [GitHub Discussions](https://github.com/L96Expanded/D-D-Initiative/discussions)
