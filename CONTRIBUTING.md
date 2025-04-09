# Contributing to Mecanum Robot Control System

Thank you for your interest in contributing to the Mecanum Robot Control System! This document provides guidelines and instructions for contributing to this project.

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Process](#development-process)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## How to Contribute

1. **Fork the Repository**
   - Click the 'Fork' button on the GitHub repository page
   - Clone your forked repository to your local machine
   ```bash
   git clone https://github.com/your-username/mecanum-robot-control.git
   cd mecanum-robot-control
   ```

2. **Create a New Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow the style guidelines
   - Write clear commit messages
   - Add tests if applicable

4. **Test Your Changes**
   - Run existing tests
   - Add new tests if needed
   - Ensure all tests pass

5. **Submit a Pull Request**
   - Push your changes to your fork
   - Create a pull request to the main repository
   - Follow the pull request template

## Development Process

1. **Setup Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Code Style**
   - Follow PEP 8 guidelines
   - Use type hints where appropriate
   - Document your code with docstrings

3. **Testing**
   - Write unit tests for new features
   - Ensure existing tests pass
   - Maintain test coverage

## Pull Request Process

1. **Create a Pull Request**
   - Use the provided pull request template
   - Describe your changes clearly
   - Reference any related issues

2. **Review Process**
   - Address reviewer comments
   - Update your pull request as needed
   - Ensure all checks pass

3. **Merge Process**
   - Squash commits if requested
   - Wait for maintainer approval
   - Merge after approval

## Style Guidelines

### Python Code
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all functions and classes
- Keep functions focused and small

### Documentation
- Update README.md for significant changes
- Document new features
- Keep documentation up to date

### Commit Messages
- Use present tense
- Be descriptive but concise
- Reference issues if applicable

Example:
```
feat: add IMU calibration feature
fix: resolve serial communication issue
docs: update installation instructions
```

## Questions?

If you have any questions about contributing, please:
1. Check the documentation
2. Open an issue
3. Contact the maintainers

Thank you for contributing! 🚀 