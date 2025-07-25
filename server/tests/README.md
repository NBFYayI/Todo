# Test Suite Documentation

This directory contains comprehensive tests for the Todo API application.

## Test Structure

```
tests/
├── conftest.py          # Test fixtures and configuration
├── test_models.py       # Database model tests
├── test_crud.py         # CRUD operation tests
├── test_services.py     # Business logic tests
├── test_controllers.py  # API endpoint tests
├── test_auth.py         # Authentication & security tests
└── README.md           # This file
```

## Test Layers

### 1. **Models Tests** (`test_models.py`)
- Tests SQLAlchemy model definitions
- Database constraints and validations
- Model relationships

### 2. **CRUD Tests** (`test_crud.py`)
- Database operations (Create, Read, Update, Delete)
- Query functions
- Data persistence

### 3. **Services Tests** (`test_services.py`)
- Business logic
- Error handling
- Service layer functionality

### 4. **Controllers Tests** (`test_controllers.py`)
- API endpoint testing
- HTTP request/response validation
- API contract testing

### 5. **Authentication Tests** (`test_auth.py`)
- Password hashing and verification
- JWT token creation and validation
- Security functionality

## Running Tests

### Prerequisites
```bash
pip install -r app/requirements.txt
```

### Basic Usage

#### Run all tests:
```bash
pytest tests/
# or
python run_tests.py
```

#### Run specific test files:
```bash
pytest tests/test_models.py
python run_tests.py --type models
```

#### Run with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
python run_tests.py --coverage
```

### Test Runner Script

Use the `run_tests.py` script for convenient test execution:

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type models
python run_tests.py --type crud
python run_tests.py --type services
python run_tests.py --type controllers
python run_tests.py --type auth

# Run with coverage report
python run_tests.py --coverage

# Verbose output
python run_tests.py --verbose

# Stop on first failure
python run_tests.py --failfast
```

## Test Configuration

### Test Database
- Tests use SQLite in-memory database for speed
- Each test gets a fresh database session
- No need for separate test database setup

### Fixtures
- `db_session`: Fresh database session for each test
- `client`: FastAPI test client with database override
- `sample_user_data`: Sample user data for testing
- `created_user`: Pre-created user in database
- `auth_headers`: Authentication headers for protected endpoints
- `multiple_users_data`: Multiple user data for bulk testing

### Coverage Target
- Minimum coverage: 85%
- Coverage reports generated in `htmlcov/` directory

## Test Patterns

### Model Testing
```python
def test_create_user(self, db_session):
    user = User(email="test@example.com", hashed_password="hash")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

### API Testing
```python
def test_register_user(self, client, sample_user_data):
    response = client.post("/user/register", json=sample_user_data)
    assert response.status_code == 201
    assert response.json()["email"] == sample_user_data["email"]
```

### Authentication Testing
```python
def test_login_success(self, client, auth_headers):
    response = client.get("/protected-endpoint", headers=auth_headers)
    assert response.status_code == 200
```

## Coverage Report

After running tests with coverage, open `htmlcov/index.html` in your browser to see detailed coverage information.

## Best Practices

1. **Test Isolation**: Each test is independent and doesn't affect others
2. **Descriptive Names**: Test names clearly describe what they test
3. **Arrange-Act-Assert**: Tests follow AAA pattern
4. **Edge Cases**: Tests cover both success and failure scenarios
5. **Fast Execution**: Tests use in-memory database for speed

## Adding New Tests

When adding new functionality:

1. Add model tests for new database models
2. Add CRUD tests for new database operations
3. Add service tests for new business logic
4. Add controller tests for new API endpoints
5. Maintain test coverage above 85% 