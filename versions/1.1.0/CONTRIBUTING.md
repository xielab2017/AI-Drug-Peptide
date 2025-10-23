# Contributing to AI-Drug Peptide V1.0

Thank you for your interest in contributing to AI-Drug Peptide! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git
- Basic knowledge of bioinformatics and Python

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/AI-Drug-Peptide.git
   cd AI-Drug-Peptide
   ```

2. **Create a development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or venv\Scripts\activate  # Windows
   
   # Install development dependencies
   python install.py --dev
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## 📝 How to Contribute

### Reporting Issues

- Use the GitHub issue tracker
- Provide detailed information about the problem
- Include system information and error messages
- Use appropriate labels

### Suggesting Features

- Use GitHub Discussions for feature requests
- Provide clear use cases and benefits
- Consider implementation complexity

### Code Contributions

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test your changes**
   ```bash
   # Run tests
   python -m pytest tests/
   
   # Run linting
   flake8 src/
   
   # Run type checking
   mypy src/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📋 Coding Standards

### Python Code Style

- Follow PEP 8
- Use Black for formatting
- Use flake8 for linting
- Use type hints where appropriate

### Documentation

- Use docstrings for all functions and classes
- Follow Google docstring format
- Update README.md for user-facing changes
- Update API documentation for code changes

### Testing

- Write tests for new functionality
- Aim for >80% code coverage
- Use pytest for testing framework
- Include both unit and integration tests

## 🏗️ Project Structure

```
AI-Drug-Peptide/
├── src/                    # Source code
│   ├── core/              # Core functionality
│   ├── api/               # API endpoints
│   ├── cli/               # Command-line interface
│   ├── models/            # Data models
│   └── utils/             # Utility functions
├── tests/                 # Test files
├── docs/                  # Documentation
├── config/                # Configuration files
├── scripts/               # Utility scripts
└── installers/            # Installation scripts
```

## 🔧 Development Tools

### Code Quality

- **Black**: Code formatting
- **flake8**: Code linting
- **mypy**: Type checking
- **pytest**: Testing framework
- **pre-commit**: Git hooks

### IDE Setup

Recommended VS Code extensions:
- Python
- Pylance
- Black Formatter
- GitLens

## 📊 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_core.py

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test
python -m pytest tests/test_core.py::test_function_name
```

### Writing Tests

```python
import pytest
from src.core.analysis import AnalysisPipeline

def test_analysis_pipeline():
    """Test analysis pipeline functionality."""
    pipeline = AnalysisPipeline()
    result = pipeline.run("THBS4")
    assert result is not None
    assert "binding_energy" in result
```

## 🚀 Release Process

### Version Numbering

We use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release notes
- [ ] Tag release
- [ ] Publish to PyPI

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the project's coding standards

### Communication

- Use GitHub Issues for bug reports
- Use GitHub Discussions for questions
- Use Pull Requests for code changes
- Be clear and concise in communications

## 📚 Resources

### Documentation

- [Project Documentation](docs/)
- [API Reference](docs/API.md)
- [Configuration Guide](docs/CONFIGURATION.md)

### External Resources

- [Python Documentation](https://docs.python.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)

## 🆘 Getting Help

If you need help:

1. Check the documentation
2. Search existing issues
3. Ask in GitHub Discussions
4. Create a new issue if needed

## 📄 License

By contributing to AI-Drug Peptide, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AI-Drug Peptide! 🎉
