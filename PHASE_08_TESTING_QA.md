# 🧪 PHASE 8: TESTING & QA
*Comprehensive testing strategy and quality assurance*

## 📋 Overview
**Phase Goal**: Implement comprehensive testing and ensure system quality  
**Dependencies**: Phase 7 (Frontend Integration)  
**Estimated Time**: 4-5 days  
**Priority**: HIGH PRIORITY

---

## 🎯 PHASE OBJECTIVES

### **8.1 Backend Testing Strategy**
- [ ] Unit tests for all business logic
- [ ] Integration tests for APIs
- [ ] Database testing with test fixtures

### **8.2 Frontend Testing Strategy**
- [ ] Component unit tests
- [ ] Integration tests for user flows
- [ ] E2E testing with real scenarios

### **8.3 Security Testing**
- [ ] Authentication security validation
- [ ] Authorization testing
- [ ] Input validation and sanitization

### **8.4 Performance Testing**
- [ ] API performance testing
- [ ] Database query optimization
- [ ] Frontend performance optimization

---

## 🔧 BACKEND TESTING

### **8.1 Unit Testing Setup**

#### **Testing Dependencies**
```python
# requirements-test.txt
pytest==7.2.1
pytest-asyncio==0.20.3
pytest-mock==3.10.0
httpx==0.23.3
pytest-cov==4.0.0
factory-boy==3.2.1
freezegun==1.2.2
```

#### **Test Configuration**
```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_database
from app.core.config import settings
from app.models.user import User
from tests.factories import UserFactory, DeckFactory, FlashcardFactory

# Test database setup
TEST_DATABASE_URL = "mongodb://localhost:27017/test_flashcard_lms"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Provide a clean test database for each test."""
    client = AsyncIOMotorClient(TEST_DATABASE_URL)
    db = client.get_default_database()
    
    # Clean all collections before test
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})
    
    yield db
    
    # Clean up after test
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})

@pytest.fixture
async def client(test_db):
    """Provide HTTP client for API testing."""
    app.dependency_overrides[get_database] = lambda: test_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
async def admin_user(test_db):
    """Create admin user for testing."""
    user = await UserFactory.create(role="admin")
    return user

@pytest.fixture
async def teacher_user(test_db):
    """Create teacher user for testing."""
    user = await UserFactory.create(role="teacher")
    return user

@pytest.fixture
async def student_user(test_db):
    """Create student user for testing."""
    user = await UserFactory.create(role="student")
    return user

@pytest.fixture
async def auth_headers(client: AsyncClient, student_user: User):
    """Provide authentication headers."""
    login_data = {
        "email": student_user.email,
        "password": "testpassword123"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

#### **Factory Setup**
```python
# tests/factories.py
import factory
from factory import fuzzy
from datetime import datetime, timedelta
from bson import ObjectId

from app.models.user import User, UserRole
from app.models.deck import Deck
from app.models.flashcard import Flashcard

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.LazyFunction(lambda: str(ObjectId()))
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    password_hash = "$2b$12$example_hash"
    full_name = factory.Faker("name")
    role = UserRole.STUDENT
    is_active = True
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)

class DeckFactory(factory.Factory):
    class Meta:
        model = Deck

    id = factory.LazyFunction(lambda: str(ObjectId()))
    title = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("text", max_nb_chars=200)
    owner_id = factory.LazyFunction(lambda: str(ObjectId()))
    lesson_id = factory.LazyFunction(lambda: str(ObjectId()))
    is_public = False
    tags = factory.LazyFunction(lambda: ["test", "sample"])
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)

class FlashcardFactory(factory.Factory):
    class Meta:
        model = Flashcard

    id = factory.LazyFunction(lambda: str(ObjectId()))
    deck_id = factory.LazyFunction(lambda: str(ObjectId()))
    question = factory.Faker("sentence", nb_words=8)
    answer = factory.Faker("sentence", nb_words=6)
    hint = factory.Faker("sentence", nb_words=4)
    explanation = factory.Faker("text", max_nb_chars=150)
    tags = factory.LazyFunction(lambda: ["test"])
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)
```

#### **Implementation Checklist**
- [ ] **Test Setup**
  - [ ] Test database configuration
  - [ ] Test fixtures and factories
  - [ ] Authentication test helpers
  - [ ] Database cleanup utilities

### **8.2 Authentication & Authorization Tests**

#### **Authentication Tests**
```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient

class TestAuthentication:
    
    async def test_user_registration(self, client: AsyncClient):
        """Test user registration endpoint."""
        registration_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepassword123",
            "full_name": "New User",
            "role": "student"
        }
        
        response = await client.post("/api/v1/auth/register", json=registration_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == registration_data["email"]
        assert data["username"] == registration_data["username"]
        assert "password" not in data  # Password should not be returned

    async def test_user_login_success(self, client: AsyncClient, student_user):
        """Test successful login."""
        login_data = {
            "email": student_user.email,
            "password": "testpassword123"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == student_user.email

    async def test_user_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token."""
        response = await client.get("/api/v1/users/me")
        
        assert response.status_code == 401

    async def test_protected_endpoint_with_token(self, client: AsyncClient, auth_headers):
        """Test accessing protected endpoint with valid token."""
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
```

#### **Authorization Tests**
```python
# tests/test_authorization.py
import pytest
from httpx import AsyncClient

class TestAuthorization:
    
    async def test_student_cannot_access_admin_endpoint(
        self, client: AsyncClient, student_user, auth_headers
    ):
        """Test that students cannot access admin-only endpoints."""
        response = await client.get("/api/v1/admin/users", headers=auth_headers)
        
        assert response.status_code == 403

    async def test_teacher_can_create_class(
        self, client: AsyncClient, teacher_user
    ):
        """Test that teachers can create classes."""
        # Login as teacher
        login_data = {
            "email": teacher_user.email,
            "password": "testpassword123"
        }
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create class
        class_data = {
            "name": "Test Class",
            "description": "A test class",
            "subject": "Mathematics"
        }
        
        response = await client.post("/api/v1/classes/", json=class_data, headers=headers)
        
        assert response.status_code == 201

    async def test_student_cannot_create_class(
        self, client: AsyncClient, auth_headers
    ):
        """Test that students cannot create classes."""
        class_data = {
            "name": "Test Class",
            "description": "A test class",
            "subject": "Mathematics"
        }
        
        response = await client.post("/api/v1/classes/", json=class_data, headers=auth_headers)
        
        assert response.status_code == 403
```

#### **Implementation Checklist**
- [ ] **Authentication Tests**
  - [ ] User registration validation
  - [ ] Login success/failure scenarios
  - [ ] Token validation
  - [ ] Password security tests

- [ ] **Authorization Tests**
  - [ ] Role-based access control
  - [ ] Resource ownership validation
  - [ ] Permission boundary testing
  - [ ] Unauthorized access prevention

### **8.3 Business Logic Tests**

#### **Deck Management Tests**
```python
# tests/test_deck_service.py
import pytest
from app.services.deck_service import DeckService
from tests.factories import UserFactory, DeckFactory, FlashcardFactory

class TestDeckService:
    
    async def test_create_deck(self, test_db):
        """Test deck creation."""
        user = await UserFactory.create()
        deck_data = {
            "title": "Test Deck",
            "description": "A test deck",
            "lesson_id": None,
            "is_public": False,
            "tags": ["test"]
        }
        
        deck = await DeckService.create_deck(user.id, deck_data)
        
        assert deck.title == deck_data["title"]
        assert deck.owner_id == user.id
        assert deck.is_public == False

    async def test_get_user_decks(self, test_db):
        """Test retrieving user's decks."""
        user = await UserFactory.create()
        deck1 = await DeckFactory.create(owner_id=user.id)
        deck2 = await DeckFactory.create(owner_id=user.id)
        deck3 = await DeckFactory.create()  # Different owner
        
        decks = await DeckService.get_user_decks(user.id)
        
        assert len(decks) == 2
        deck_ids = [deck.id for deck in decks]
        assert deck1.id in deck_ids
        assert deck2.id in deck_ids
        assert deck3.id not in deck_ids

    async def test_delete_deck_with_flashcards(self, test_db):
        """Test deleting deck cascades to flashcards."""
        user = await UserFactory.create()
        deck = await DeckFactory.create(owner_id=user.id)
        flashcard1 = await FlashcardFactory.create(deck_id=deck.id)
        flashcard2 = await FlashcardFactory.create(deck_id=deck.id)
        
        await DeckService.delete_deck(user.id, deck.id)
        
        # Verify deck is deleted
        deleted_deck = await DeckService.get_deck(deck.id)
        assert deleted_deck is None
        
        # Verify flashcards are deleted
        from app.services.flashcard_service import FlashcardService
        deck_flashcards = await FlashcardService.get_deck_flashcards(deck.id)
        assert len(deck_flashcards) == 0
```

#### **SM-2 Algorithm Tests**
```python
# tests/test_sm2_algorithm.py
import pytest
from datetime import datetime, timedelta
from app.algorithms.sm2 import SM2Algorithm

class TestSM2Algorithm:
    
    def test_first_correct_answer(self):
        """Test SM-2 algorithm for first correct answer."""
        repetitions, ease_factor, interval, next_review = SM2Algorithm.calculate_next_review(
            quality=4,  # Easy
            repetitions=0,
            ease_factor=2.5,
            interval=0
        )
        
        assert repetitions == 1
        assert interval == 1
        assert ease_factor > 2.5  # Should increase for easy answer

    def test_second_correct_answer(self):
        """Test SM-2 algorithm for second correct answer."""
        repetitions, ease_factor, interval, next_review = SM2Algorithm.calculate_next_review(
            quality=3,  # Good
            repetitions=1,
            ease_factor=2.5,
            interval=1
        )
        
        assert repetitions == 2
        assert interval == 6

    def test_incorrect_answer_resets(self):
        """Test that incorrect answer resets repetitions."""
        repetitions, ease_factor, interval, next_review = SM2Algorithm.calculate_next_review(
            quality=1,  # Again/Incorrect
            repetitions=5,
            ease_factor=2.5,
            interval=30
        )
        
        assert repetitions == 0
        assert interval == 1
        assert ease_factor < 2.5  # Should decrease for incorrect answer

    def test_ease_factor_minimum(self):
        """Test that ease factor doesn't go below 1.3."""
        repetitions, ease_factor, interval, next_review = SM2Algorithm.calculate_next_review(
            quality=0,  # Very incorrect
            repetitions=0,
            ease_factor=1.3,
            interval=1
        )
        
        assert ease_factor >= 1.3
```

#### **Implementation Checklist**
- [ ] **Business Logic Tests**
  - [ ] Deck CRUD operations
  - [ ] Flashcard management
  - [ ] SM-2 algorithm accuracy
  - [ ] Study session logic

- [ ] **Algorithm Tests**
  - [ ] SM-2 calculation correctness
  - [ ] Edge case handling
  - [ ] Performance optimization
  - [ ] Statistical validation

### **8.4 API Integration Tests**

#### **API Endpoint Tests**
```python
# tests/test_api_endpoints.py
import pytest
from httpx import AsyncClient

class TestDeckEndpoints:
    
    async def test_create_deck_endpoint(self, client: AsyncClient, auth_headers):
        """Test deck creation via API."""
        deck_data = {
            "title": "Test Deck API",
            "description": "Created via API test",
            "is_public": False,
            "tags": ["api", "test"]
        }
        
        response = await client.post(
            "/api/v1/decks/",
            json=deck_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == deck_data["title"]
        assert "id" in data

    async def test_get_deck_endpoint(self, client: AsyncClient, auth_headers):
        """Test retrieving deck via API."""
        # First create a deck
        deck_data = {
            "title": "Test Deck Get",
            "description": "For get test",
            "is_public": False,
            "tags": ["test"]
        }
        
        create_response = await client.post(
            "/api/v1/decks/",
            json=deck_data,
            headers=auth_headers
        )
        deck_id = create_response.json()["id"]
        
        # Then retrieve it
        response = await client.get(
            f"/api/v1/decks/{deck_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == deck_data["title"]

    async def test_update_deck_endpoint(self, client: AsyncClient, auth_headers):
        """Test updating deck via API."""
        # Create deck
        deck_data = {
            "title": "Original Title",
            "description": "Original description",
            "is_public": False,
            "tags": ["test"]
        }
        
        create_response = await client.post(
            "/api/v1/decks/",
            json=deck_data,
            headers=auth_headers
        )
        deck_id = create_response.json()["id"]
        
        # Update deck
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }
        
        response = await client.put(
            f"/api/v1/decks/{deck_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]

class TestStudyEndpoints:
    
    async def test_start_study_session(self, client: AsyncClient, auth_headers):
        """Test starting a study session."""
        # First create a deck with flashcards
        deck_data = {
            "title": "Study Test Deck",
            "description": "For study testing",
            "is_public": False,
            "tags": ["study"]
        }
        
        deck_response = await client.post(
            "/api/v1/decks/",
            json=deck_data,
            headers=auth_headers
        )
        deck_id = deck_response.json()["id"]
        
        # Add some flashcards
        for i in range(5):
            flashcard_data = {
                "question": f"Question {i+1}",
                "answer": f"Answer {i+1}",
                "hint": f"Hint {i+1}"
            }
            await client.post(
                f"/api/v1/decks/{deck_id}/flashcards/",
                json=flashcard_data,
                headers=auth_headers
            )
        
        # Start study session
        session_data = {
            "deck_id": deck_id,
            "study_mode": "review",
            "target_cards": 5
        }
        
        response = await client.post(
            "/api/v1/study/sessions/start",
            json=session_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["deck_id"] == deck_id
        assert data["study_mode"] == "review"
        assert len(data["scheduled_cards"]) <= 5
```

#### **Implementation Checklist**
- [ ] **API Integration Tests**
  - [ ] All CRUD endpoints
  - [ ] Study session workflow
  - [ ] File upload/download
  - [ ] Error response validation

---

## 🖥️ FRONTEND TESTING

### **8.5 Component Unit Tests**

#### **React Testing Setup**
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
});
```

```typescript
// src/test/setup.ts
import '@testing-library/jest-dom';
import { beforeAll, afterEach, afterAll } from 'vitest';
import { cleanup } from '@testing-library/react';
import { server } from './mocks/server';

// Establish API mocking before all tests
beforeAll(() => server.listen());

// Reset any request handlers that we may add during the tests
afterEach(() => {
  server.resetHandlers();
  cleanup();
});

// Clean up after the tests are finished
afterAll(() => server.close());
```

#### **Authentication Component Tests**
```typescript
// src/pages/auth/__tests__/LoginPage.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LoginPage } from '../LoginPage';
import { useAuthStore } from '../../../stores/authStore';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      {children}
    </BrowserRouter>
  </QueryClientProvider>
);

describe('LoginPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, token: null });
  });

  it('renders login form', () => {
    render(<LoginPage />, { wrapper: Wrapper });
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    render(<LoginPage />, { wrapper: Wrapper });
    
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
      expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    render(<LoginPage />, { wrapper: Wrapper });
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });
  });
});
```

#### **Study Component Tests**
```typescript
// src/components/study/__tests__/FlashcardDisplay.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { FlashcardDisplay } from '../FlashcardDisplay';
import type { FlashcardStudyResponse } from '../../../types/study';

const mockFlashcard: FlashcardStudyResponse = {
  id: '1',
  deck_id: 'deck1',
  question: 'What is 2 + 2?',
  answer: '4',
  hint: 'Simple addition',
  explanation: 'Basic arithmetic',
  repetitions: 0,
  ease_factor: 2.5,
  interval: 0,
  next_review: new Date(),
  review_count: 0,
  correct_count: 0,
  accuracy_rate: 0,
};

describe('FlashcardDisplay', () => {
  const mockOnShowAnswer = vi.fn();
  const mockOnAnswer = vi.fn();

  beforeEach(() => {
    mockOnShowAnswer.mockClear();
    mockOnAnswer.mockClear();
  });

  it('renders question', () => {
    render(
      <FlashcardDisplay
        flashcard={mockFlashcard}
        showAnswer={false}
        onShowAnswer={mockOnShowAnswer}
        onAnswer={mockOnAnswer}
        studyMode="review"
      />
    );
    
    expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument();
    expect(screen.getByText('Show Answer')).toBeInTheDocument();
  });

  it('shows answer when clicked', () => {
    render(
      <FlashcardDisplay
        flashcard={mockFlashcard}
        showAnswer={true}
        onShowAnswer={mockOnShowAnswer}
        onAnswer={mockOnAnswer}
        studyMode="review"
      />
    );
    
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('Simple addition')).toBeInTheDocument();
    expect(screen.getByText('Basic arithmetic')).toBeInTheDocument();
  });

  it('displays difficulty buttons in review mode', () => {
    render(
      <FlashcardDisplay
        flashcard={mockFlashcard}
        showAnswer={true}
        onShowAnswer={mockOnShowAnswer}
        onAnswer={mockOnAnswer}
        studyMode="review"
      />
    );
    
    expect(screen.getByText('Again')).toBeInTheDocument();
    expect(screen.getByText('Hard')).toBeInTheDocument();
    expect(screen.getByText('Good')).toBeInTheDocument();
    expect(screen.getByText('Easy')).toBeInTheDocument();
  });

  it('calls onAnswer with correct quality when button clicked', () => {
    render(
      <FlashcardDisplay
        flashcard={mockFlashcard}
        showAnswer={true}
        onShowAnswer={mockOnShowAnswer}
        onAnswer={mockOnAnswer}
        studyMode="review"
      />
    );
    
    fireEvent.click(screen.getByText('Easy'));
    
    expect(mockOnAnswer).toHaveBeenCalledWith(4, expect.any(Number));
  });
});
```

#### **Implementation Checklist**
- [ ] **Component Tests**
  - [ ] Authentication form validation
  - [ ] Study session interactions
  - [ ] Navigation components
  - [ ] Form submission handling

### **8.6 Integration Tests**

#### **User Flow Tests**
```typescript
// src/test/integration/StudyFlow.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { App } from '../../App';
import { server } from '../mocks/server';
import { rest } from 'msw';

describe('Study Flow Integration', () => {
  it('completes full study session', async () => {
    // Mock API responses
    server.use(
      rest.post('/api/v1/auth/login', (req, res, ctx) => {
        return res(
          ctx.json({
            access_token: 'mock-token',
            user: { id: '1', email: 'test@example.com', role: 'student' }
          })
        );
      }),
      rest.get('/api/v1/decks', (req, res, ctx) => {
        return res(
          ctx.json([
            { id: '1', title: 'Test Deck', description: 'Test description' }
          ])
        );
      }),
      rest.post('/api/v1/study/sessions/start', (req, res, ctx) => {
        return res(
          ctx.json({
            id: 'session1',
            deck_id: '1',
            study_mode: 'review',
            scheduled_cards: [
              {
                id: 'card1',
                question: 'Test question',
                answer: 'Test answer'
              }
            ]
          })
        );
      })
    );

    render(
      <QueryClientProvider client={new QueryClient()}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    );

    // Login
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Navigate to study
    await waitFor(() => {
      expect(screen.getByText('Test Deck')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Study'));

    // Start study session
    await waitFor(() => {
      expect(screen.getByText('Start Study Session')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Start Study Session'));

    // Complete study session
    await waitFor(() => {
      expect(screen.getByText('Test question')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Show Answer'));
    fireEvent.click(screen.getByText('Good'));

    // Verify completion
    await waitFor(() => {
      expect(screen.getByText('Session Complete')).toBeInTheDocument();
    });
  });
});
```

#### **Implementation Checklist**
- [ ] **Integration Tests**
  - [ ] Complete user authentication flow
  - [ ] Study session workflow
  - [ ] Deck management workflow
  - [ ] Class enrollment process

---

## 🛡️ SECURITY TESTING

### **8.7 Security Validation**

#### **Input Validation Tests**
```python
# tests/test_security.py
import pytest
from httpx import AsyncClient

class TestInputValidation:
    
    async def test_sql_injection_prevention(self, client: AsyncClient, auth_headers):
        """Test that SQL injection attempts are blocked."""
        malicious_input = "'; DROP TABLE users; --"
        
        deck_data = {
            "title": malicious_input,
            "description": "Normal description",
            "is_public": False
        }
        
        response = await client.post(
            "/api/v1/decks/",
            json=deck_data,
            headers=auth_headers
        )
        
        # Should succeed but sanitize input
        assert response.status_code == 201
        data = response.json()
        # Verify malicious content is sanitized
        assert "DROP TABLE" not in data["title"]

    async def test_xss_prevention(self, client: AsyncClient, auth_headers):
        """Test XSS script injection prevention."""
        xss_script = "<script>alert('xss')</script>"
        
        deck_data = {
            "title": f"Test Deck {xss_script}",
            "description": "Normal description",
            "is_public": False
        }
        
        response = await client.post(
            "/api/v1/decks/",
            json=deck_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        # Verify script tags are escaped or removed
        assert "<script>" not in data["title"]

    async def test_file_upload_validation(self, client: AsyncClient, auth_headers):
        """Test file upload security validation."""
        # Test malicious file upload
        malicious_content = b"<?php system($_GET['cmd']); ?>"
        
        files = {"file": ("malicious.php", malicious_content, "application/php")}
        
        response = await client.post(
            "/api/v1/upload/",
            files=files,
            headers=auth_headers
        )
        
        # Should reject dangerous file types
        assert response.status_code == 400
        assert "file type not allowed" in response.json()["detail"].lower()

    async def test_rate_limiting(self, client: AsyncClient):
        """Test rate limiting protection."""
        # Attempt many login requests rapidly
        for i in range(10):
            response = await client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "wrongpassword"
            })
            
            if response.status_code == 429:
                # Rate limiting activated
                break
        else:
            pytest.fail("Rate limiting not activated after multiple failed attempts")
```

#### **Authorization Security Tests**
```python
# tests/test_authorization_security.py
import pytest
from httpx import AsyncClient

class TestAuthorizationSecurity:
    
    async def test_jwt_token_tampering(self, client: AsyncClient):
        """Test that tampered JWT tokens are rejected."""
        # Create a tampered token
        tampered_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.TAMPERED.signature"
        headers = {"Authorization": f"Bearer {tampered_token}"}
        
        response = await client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 401

    async def test_expired_token_rejection(self, client: AsyncClient):
        """Test that expired tokens are rejected."""
        # This would require creating an expired token for testing
        # Implementation depends on JWT library configuration
        pass

    async def test_privilege_escalation_prevention(
        self, client: AsyncClient, student_user
    ):
        """Test that users cannot escalate their privileges."""
        # Login as student
        login_data = {
            "email": student_user.email,
            "password": "testpassword123"
        }
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Attempt to update own role to admin
        update_data = {"role": "admin"}
        
        response = await client.put(
            f"/api/v1/users/{student_user.id}",
            json=update_data,
            headers=headers
        )
        
        # Should be forbidden or ignore role change
        assert response.status_code in [403, 422]
```

#### **Implementation Checklist**
- [ ] **Security Tests**
  - [ ] Input validation and sanitization
  - [ ] XSS prevention
  - [ ] SQL injection prevention
  - [ ] File upload security

- [ ] **Authentication Security**
  - [ ] JWT token validation
  - [ ] Token expiration handling
  - [ ] Rate limiting verification
  - [ ] Privilege escalation prevention

---

## ⚡ PERFORMANCE TESTING

### **8.8 API Performance Tests**

#### **Load Testing Setup**
```python
# tests/test_performance.py
import pytest
import asyncio
import time
from httpx import AsyncClient

class TestAPIPerformance:
    
    async def test_concurrent_requests(self, client: AsyncClient, auth_headers):
        """Test API performance under concurrent load."""
        
        async def make_request():
            response = await client.get("/api/v1/decks/", headers=auth_headers)
            return response.status_code
        
        # Create 50 concurrent requests
        tasks = [make_request() for _ in range(50)]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        
        # Should complete within reasonable time (adjust threshold as needed)
        total_time = end_time - start_time
        assert total_time < 5.0  # 5 seconds for 50 requests

    async def test_database_query_performance(self, client: AsyncClient, auth_headers):
        """Test database query performance."""
        # Create multiple decks for testing
        for i in range(100):
            deck_data = {
                "title": f"Performance Test Deck {i}",
                "description": f"Deck {i} for performance testing",
                "is_public": False
            }
            await client.post("/api/v1/decks/", json=deck_data, headers=auth_headers)
        
        # Test pagination performance
        start_time = time.time()
        response = await client.get(
            "/api/v1/decks/?page=1&page_size=20",
            headers=auth_headers
        )
        end_time = time.time()
        
        assert response.status_code == 200
        query_time = end_time - start_time
        assert query_time < 1.0  # Should complete within 1 second

    async def test_study_session_performance(self, client: AsyncClient, auth_headers):
        """Test study session creation performance."""
        # Create deck with many flashcards
        deck_data = {
            "title": "Large Performance Test Deck",
            "description": "Deck with many cards",
            "is_public": False
        }
        deck_response = await client.post(
            "/api/v1/decks/",
            json=deck_data,
            headers=auth_headers
        )
        deck_id = deck_response.json()["id"]
        
        # Add 1000 flashcards
        for i in range(1000):
            flashcard_data = {
                "question": f"Question {i}",
                "answer": f"Answer {i}"
            }
            await client.post(
                f"/api/v1/decks/{deck_id}/flashcards/",
                json=flashcard_data,
                headers=auth_headers
            )
        
        # Test study session creation performance
        start_time = time.time()
        session_data = {
            "deck_id": deck_id,
            "study_mode": "review",
            "target_cards": 20
        }
        response = await client.post(
            "/api/v1/study/sessions/start",
            json=session_data,
            headers=auth_headers
        )
        end_time = time.time()
        
        assert response.status_code == 200
        session_time = end_time - start_time
        assert session_time < 2.0  # Should complete within 2 seconds
```

#### **Database Optimization Tests**
```python
# tests/test_database_performance.py
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.database import get_database

class TestDatabaseOptimization:
    
    async def test_index_usage(self, test_db):
        """Test that database queries use indexes efficiently."""
        collection = test_db.flashcards
        
        # Explain query to check index usage
        explain_result = await collection.find(
            {"deck_id": "test_deck_id"}
        ).explain()
        
        # Verify that index is used (not collection scan)
        execution_stats = explain_result["executionStats"]
        assert execution_stats["executionSuccess"] == True
        assert "IXSCAN" in str(execution_stats)  # Index scan used

    async def test_aggregation_performance(self, test_db):
        """Test aggregation pipeline performance."""
        import time
        
        # Create test data
        collection = test_db.study_sessions
        test_sessions = [
            {
                "user_id": "user1",
                "deck_id": f"deck{i}",
                "cards_studied": i * 10,
                "correct_answers": i * 7,
                "study_time": i * 300
            }
            for i in range(1000)
        ]
        await collection.insert_many(test_sessions)
        
        # Test aggregation performance
        start_time = time.time()
        
        pipeline = [
            {"$match": {"user_id": "user1"}},
            {"$group": {
                "_id": "$user_id",
                "total_cards": {"$sum": "$cards_studied"},
                "total_correct": {"$sum": "$correct_answers"},
                "total_time": {"$sum": "$study_time"}
            }}
        ]
        
        result = await collection.aggregate(pipeline).to_list(None)
        end_time = time.time()
        
        aggregation_time = end_time - start_time
        assert aggregation_time < 1.0  # Should complete within 1 second
        assert len(result) == 1
```

#### **Implementation Checklist**
- [ ] **Performance Tests**
  - [ ] Concurrent request handling
  - [ ] Database query optimization
  - [ ] API response time validation
  - [ ] Memory usage monitoring

- [ ] **Optimization Tests**
  - [ ] Index usage verification
  - [ ] Query performance benchmarks
  - [ ] Aggregation pipeline efficiency
  - [ ] Connection pooling effectiveness

---

## 📊 TEST REPORTING

### **8.9 Coverage and Reporting**

#### **Coverage Configuration**
```python
# pytest.ini
[tool:pytest]
addopts = 
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85
    --strict-markers
    --disable-warnings
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

#### **Test Automation Script**
```bash
#!/bin/bash
# scripts/run_tests.sh

set -e

echo "Running Backend Tests..."

# Run unit tests with coverage
pytest tests/unit/ --cov=app --cov-report=html:htmlcov/unit --cov-report=term

# Run integration tests
pytest tests/integration/ --cov=app --cov-append --cov-report=html:htmlcov/integration --cov-report=term

# Run security tests
pytest tests/security/ --cov=app --cov-append --cov-report=html:htmlcov/security --cov-report=term

# Run performance tests
pytest tests/performance/ --cov=app --cov-append --cov-report=html:htmlcov/performance --cov-report=term

echo "Running Frontend Tests..."

# Run frontend unit tests
cd frontend
npm run test:coverage

# Run E2E tests
npm run test:e2e

echo "All tests completed!"
```

#### **Implementation Checklist**
- [ ] **Test Reporting**
  - [ ] Code coverage reports
  - [ ] Test result summaries
  - [ ] Performance benchmarks
  - [ ] Security scan results

---

## 📋 COMPLETION CRITERIA

✅ **Phase 8 Complete When:**
- [ ] Backend unit tests achieve >85% coverage
- [ ] All API endpoints have integration tests
- [ ] Frontend components have unit tests
- [ ] Security vulnerabilities identified and fixed
- [ ] Performance benchmarks established
- [ ] Automated testing pipeline configured
- [ ] Test documentation complete
- [ ] CI/CD integration working
- [ ] Quality gates implemented
- [ ] Test reports generated

---

## 🔄 NEXT PHASE
**PHASE 9**: Performance Optimization
- Implement caching strategies
- Optimize database queries
- Set up monitoring and logging

---

*Part of comprehensive Flashcard LMS implementation*  
*Based on 20 decisions from DECISION_FRAMEWORK.md*
