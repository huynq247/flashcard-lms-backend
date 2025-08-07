# **Test Framework Documentation**

## **📋 Overview**
Comprehensive testing framework for Flashcard LMS Backend, designed to support all development phases.

## **🛠️ Test Infrastructure**

### **Core Components**
- **pytest**: Main testing framework with async support
- **httpx**: HTTP client for API testing
- **Mock services**: Database and external service mocking
- **Fixtures**: Reusable test data and configurations

### **Test Categories**
```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── test_config.py             # Testing environment setup
├── unit/                      # Unit tests for individual functions
│   ├── test_auth_utils.py     # Authentication utilities
│   ├── test_srs_algorithm.py  # SRS learning algorithm
│   └── test_deck_operations.py # Deck management logic
├── integration/               # Integration tests
│   ├── test_auth_endpoints.py # Authentication API endpoints
│   ├── test_permissions.py    # Role-based access control
│   └── test_privacy_system.py # Deck privacy features
└── e2e/                       # End-to-end tests (Phase 7-8)
    ├── test_user_workflows.py # Complete user journeys
    └── test_study_sessions.py # Full study workflows
```

## **🎯 Phase-by-Phase Testing Strategy**

### **Phase 3: Authentication & Authorization ✅**
- [x] Authentication utilities testing
- [x] API endpoint testing
- [x] Permission system testing
- [x] Role-based access control
- [x] Privacy controls validation

### **Phase 4: Core API Endpoints**
- [ ] Deck CRUD operations
- [ ] Card management
- [ ] Class management
- [ ] User profile management
- [ ] API validation and error handling

### **Phase 5: SRS Learning Algorithm**
- [ ] SRS calculation logic
- [ ] Performance tracking
- [ ] Study session algorithms
- [ ] Progress analytics

### **Phase 6: Advanced Features**
- [ ] Study session workflows
- [ ] Progress tracking
- [ ] Analytics and reporting
- [ ] Advanced search and filters

### **Phase 7: Frontend Integration**
- [ ] API contract testing
- [ ] Cross-browser compatibility
- [ ] User interface workflows
- [ ] Real-time features

### **Phase 8: Testing & QA**
- [ ] Performance testing
- [ ] Load testing
- [ ] Security testing
- [ ] Final integration validation

## **🚀 Running Tests**

### **All Tests**
```bash
python -m pytest tests/ -v
```

### **Specific Phase**
```bash
# Phase 3 - Authentication
python -m pytest tests/test_auth* -v

# Phase 4 - API Endpoints  
python -m pytest tests/test_*_endpoints.py -v

# Phase 5 - SRS Algorithm
python -m pytest tests/test_srs* -v
```

### **Test Categories**
```bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v

# End-to-end tests
python -m pytest tests/e2e/ -v
```

### **With Coverage**
```bash
python -m pytest tests/ --cov=app --cov-report=html
```

## **📊 Test Markers**

```python
# test_example.py
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test
@pytest.mark.auth          # Authentication related
@pytest.mark.permissions   # Permission testing
@pytest.mark.privacy       # Privacy controls
@pytest.mark.srs           # SRS algorithm
@pytest.mark.api           # API endpoint testing
@pytest.mark.slow          # Slow running tests
```

### **Run by Markers**
```bash
# Run only unit tests
python -m pytest -m unit

# Run only auth tests
python -m pytest -m auth

# Skip slow tests
python -m pytest -m "not slow"
```

## **🔧 Test Configuration**

### **Environment Variables**
```bash
# Testing mode
TESTING=true

# Test database
TEST_DATABASE_NAME=flashcard_lms_test

# Mock external services
MOCK_GEMINI_API=true
```

### **Pytest Configuration (pyproject.toml)**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
asyncio_mode = "auto"
markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "auth: Authentication tests",
    "permissions: Permission tests",
    "privacy: Privacy control tests",
    "srs: SRS algorithm tests",
    "api: API endpoint tests",
    "slow: Slow running tests"
]
```

## **📝 Test Data Management**

### **Fixtures**
- `async_client`: HTTP client for API testing
- `auth_headers`: Authentication headers
- `sample_user_data`: Test user data
- `mock_user`: Mock user objects
- `clear_token_blacklist`: Clean token blacklist

### **Mock Services**
- `MockDatabaseService`: In-memory database for testing
- Mock external APIs (Gemini, file storage)
- Mock email services

## **🎨 Best Practices**

1. **Isolation**: Each test is independent
2. **Cleanup**: Automatic cleanup after tests
3. **Mocking**: Mock external dependencies
4. **Async Support**: Full async/await support
5. **Realistic Data**: Use realistic test data
6. **Coverage**: Aim for >90% test coverage

## **📈 Continuous Integration**

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ --cov=app
```

## **🔮 Future Expansions**

- **Performance Tests**: Load testing with locust
- **Security Tests**: Penetration testing automation
- **Visual Tests**: Screenshot comparison testing
- **Mobile Tests**: Mobile app integration testing
- **Analytics Tests**: Data pipeline validation

---

**This test framework grows with your project and supports all phases! 🚀**
