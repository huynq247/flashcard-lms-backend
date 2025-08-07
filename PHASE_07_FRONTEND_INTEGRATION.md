# 🔗 PHASE 7: FRONTEND INTEGRATION
*Complete React TypeScript frontend with advanced features*

## 📋 Overview
**Phase Goal**: Build complete React TypeScript frontend with advanced UI/UX  
**Dependencies**: Phase 6 (Study System Implementation)  
**Estimated Time**: 8-10 days  
**Priority**: HIGH PRIORITY

---

## 🎯 PHASE OBJECTIVES

### **7.1 Frontend Architecture (Decision #5: React TypeScript)**
- [ ] React TypeScript setup with modern tooling
- [ ] State management and API integration

### **7.2 Authentication UI (Decision #3: JWT + #4: Student/Teacher/Admin)**
- [ ] Login/register components
- [ ] Role-based UI components

### **7.3 3-Level Hierarchy UI (Decision #6: Classes → Courses → Lessons)**
- [ ] Class management interface
- [ ] Course and lesson navigation
- [ ] Hierarchical navigation

### **7.4 Study Interface (Decision #9: SM-2 + #11: Multiple Modes)**
- [ ] Interactive study session UI
- [ ] Multiple study mode interfaces
- [ ] Progress visualization

### **7.5 Import/Export UI (Decision #15: CSV+JSON + #16: Multi-format)**
- [ ] File upload interfaces
- [ ] Export/download functionality
- [ ] Data portability features

---

## 🏗️ FRONTEND ARCHITECTURE

### **7.1 Project Setup & Structure**

#### **Package.json Configuration**
```json
{
  "name": "flashcard-lms-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "@tanstack/react-query": "^4.24.6",
    "zustand": "^4.3.2",
    "axios": "^1.3.0",
    "@headlessui/react": "^1.7.12",
    "@heroicons/react": "^2.0.16",
    "clsx": "^1.2.1",
    "react-hook-form": "^7.43.1",
    "@hookform/resolvers": "^2.9.11",
    "zod": "^3.20.6",
    "recharts": "^2.5.0",
    "react-dropzone": "^14.2.3",
    "react-hot-toast": "^2.4.0",
    "date-fns": "^2.29.3"
  },
  "devDependencies": {
    "@types/react": "^18.0.27",
    "@types/react-dom": "^18.0.10",
    "@vitejs/plugin-react": "^3.1.0",
    "typescript": "^4.9.3",
    "vite": "^4.1.0",
    "tailwindcss": "^3.2.7",
    "@types/node": "^18.14.2",
    "eslint": "^8.35.0",
    "@typescript-eslint/eslint-plugin": "^5.54.0",
    "@typescript-eslint/parser": "^5.54.0",
    "vitest": "^0.28.5",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^5.16.5"
  }
}
```

#### **Project Structure**
```
src/
├── components/           # Reusable UI components
│   ├── ui/              # Basic UI components
│   ├── forms/           # Form components
│   ├── layout/          # Layout components
│   └── study/           # Study-specific components
├── pages/               # Page components
│   ├── auth/            # Authentication pages
│   ├── dashboard/       # Dashboard pages
│   ├── classes/         # Class management pages
│   ├── study/           # Study pages
│   └── admin/           # Admin pages
├── hooks/               # Custom React hooks
├── services/            # API services
├── stores/              # Zustand stores
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
└── constants/           # App constants
```

#### **Implementation Checklist**
- [ ] **Project Setup**
  - [ ] Vite + React + TypeScript configuration
  - [ ] Tailwind CSS setup
  - [ ] ESLint and Prettier configuration
  - [ ] Testing setup (Vitest + Testing Library)

- [ ] **Core Dependencies**
  - [ ] React Router for navigation
  - [ ] TanStack Query for API management
  - [ ] Zustand for state management
  - [ ] React Hook Form + Zod for forms
  - [ ] Headless UI for accessible components

### **7.2 API Integration Layer**

#### **API Service Setup**
```typescript
// src/services/api.ts
import axios, { AxiosResponse } from 'axios';
import { useAuthStore } from '../stores/authStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance
export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

// Type-safe API client
export class ApiClient {
  static async get<T>(url: string): Promise<T> {
    const response = await api.get<T>(url);
    return response.data;
  }

  static async post<T>(url: string, data?: any): Promise<T> {
    const response = await api.post<T>(url, data);
    return response.data;
  }

  static async put<T>(url: string, data?: any): Promise<T> {
    const response = await api.put<T>(url, data);
    return response.data;
  }

  static async delete<T>(url: string): Promise<T> {
    const response = await api.delete<T>(url);
    return response.data;
  }
}
```

#### **React Query Setup**
```typescript
// src/hooks/useAuth.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../stores/authStore';
import { authService } from '../services/authService';
import type { LoginRequest, RegisterRequest, User } from '../types/auth';

export const useLogin = () => {
  const { setAuth } = useAuthStore();
  
  return useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: (response) => {
      setAuth(response.access_token, response.user);
    },
  });
};

export const useRegister = () => {
  return useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),
  });
};

export const useProfile = () => {
  const { token } = useAuthStore();
  
  return useQuery({
    queryKey: ['profile'],
    queryFn: () => authService.getProfile(),
    enabled: !!token,
  });
};

// src/hooks/useClasses.ts
export const useClasses = () => {
  return useQuery({
    queryKey: ['classes'],
    queryFn: () => classService.getClasses(),
  });
};

export const useCreateClass = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateClassRequest) => classService.createClass(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classes'] });
    },
  });
};
```

#### **Implementation Checklist**
- [ ] **API Integration**
  - [ ] Axios setup with interceptors
  - [ ] Type-safe API client
  - [ ] React Query configuration
  - [ ] Error handling middleware

- [ ] **Custom Hooks**
  - [ ] Authentication hooks
  - [ ] Data fetching hooks
  - [ ] Mutation hooks with cache invalidation
  - [ ] Loading and error state management

---

## 🔐 AUTHENTICATION UI

### **7.3 Authentication Components (Decision #3: JWT + #4: Roles)**

#### **Login Component**
```typescript
// src/pages/auth/LoginPage.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, Navigate } from 'react-router-dom';
import { useLogin } from '../../hooks/useAuth';
import { useAuthStore } from '../../stores/authStore';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import toast from 'react-hot-toast';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginForm = z.infer<typeof loginSchema>;

export const LoginPage: React.FC = () => {
  const { user } = useAuthStore();
  const loginMutation = useLogin();
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    try {
      await loginMutation.mutateAsync(data);
      toast.success('Login successful!');
    } catch (error) {
      toast.error('Login failed. Please check your credentials.');
    }
  };

  // Redirect if already logged in
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <Input
              id="email"
              type="email"
              label="Email address"
              error={errors.email?.message}
              {...register('email')}
            />
            <Input
              id="password"
              type="password"
              label="Password"
              error={errors.password?.message}
              {...register('password')}
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            loading={isSubmitting}
            disabled={isSubmitting}
          >
            Sign in
          </Button>

          <div className="text-center">
            <Link
              to="/auth/register"
              className="text-indigo-600 hover:text-indigo-500"
            >
              Don't have an account? Sign up
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};
```

#### **Role-based Route Protection**
```typescript
// src/components/auth/ProtectedRoute.tsx
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { UserRole } from '../../types/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: UserRole;
  fallback?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  fallback,
}) => {
  const { user, token } = useAuthStore();
  const location = useLocation();

  // Not authenticated
  if (!token || !user) {
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }

  // Role check
  if (requiredRole && user.role !== requiredRole) {
    if (fallback) {
      return <>{fallback}</>;
    }
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

// src/components/auth/RoleGuard.tsx
interface RoleGuardProps {
  allowedRoles: UserRole[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({
  allowedRoles,
  children,
  fallback,
}) => {
  const { user } = useAuthStore();

  if (!user || !allowedRoles.includes(user.role)) {
    return fallback ? <>{fallback}</> : null;
  }

  return <>{children}</>;
};
```

#### **Implementation Checklist**
- [ ] **Authentication UI**
  - [ ] Login page with validation
  - [ ] Registration page with role selection
  - [ ] Password reset functionality
  - [ ] Profile management page

- [ ] **Role-based Access**
  - [ ] Protected route wrapper
  - [ ] Role guard component
  - [ ] Conditional UI rendering
  - [ ] Unauthorized page

---

## 🏫 3-LEVEL HIERARCHY UI

### **7.4 Class Management Interface (Decision #6: Classes → Courses → Lessons)**

#### **Class Dashboard**
```typescript
// src/pages/classes/ClassDashboard.tsx
import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useClass, useClassCourses } from '../../hooks/useClasses';
import { RoleGuard } from '../../components/auth/RoleGuard';
import { UserRole } from '../../types/auth';
import { CourseCard } from '../../components/classes/CourseCard';
import { StudentList } from '../../components/classes/StudentList';
import { ClassProgress } from '../../components/classes/ClassProgress';

export const ClassDashboard: React.FC = () => {
  const { classId } = useParams<{ classId: string }>();
  const { data: classData, isLoading } = useClass(classId!);
  const { data: courses } = useClassCourses(classId!);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Class Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {classData?.name}
            </h1>
            <p className="text-gray-600 mt-1">{classData?.description}</p>
          </div>
          
          <RoleGuard allowedRoles={[UserRole.TEACHER, UserRole.ADMIN]}>
            <div className="flex space-x-3">
              <Link
                to={`/classes/${classId}/manage`}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Manage Class
              </Link>
              <Link
                to={`/classes/${classId}/courses/new`}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
              >
                Add Course
              </Link>
            </div>
          </RoleGuard>
        </div>
      </div>

      {/* Class Progress Overview */}
      <RoleGuard allowedRoles={[UserRole.TEACHER, UserRole.ADMIN]}>
        <ClassProgress classId={classId!} />
      </RoleGuard>

      {/* Courses Grid */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Courses</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses?.map((course) => (
            <CourseCard
              key={course.id}
              course={course}
              classId={classId!}
            />
          ))}
        </div>
      </div>

      {/* Students List (Teachers/Admins only) */}
      <RoleGuard allowedRoles={[UserRole.TEACHER, UserRole.ADMIN]}>
        <StudentList classId={classId!} />
      </RoleGuard>
    </div>
  );
};
```

#### **Course Navigation Component**
```typescript
// src/components/classes/CourseNavigation.tsx
import React from 'react';
import { Link, useParams } from 'react-router-dom';
import { useCourse, useCourseLessons } from '../../hooks/useCourses';
import { ChevronRightIcon } from '@heroicons/react/24/outline';

export const CourseNavigation: React.FC = () => {
  const { classId, courseId } = useParams();
  const { data: course } = useCourse(courseId!);
  const { data: lessons } = useCourseLessons(courseId!);

  return (
    <div className="bg-white shadow rounded-lg p-6">
      {/* Breadcrumb */}
      <nav className="flex mb-6" aria-label="Breadcrumb">
        <ol className="flex items-center space-x-4">
          <li>
            <Link to={`/classes/${classId}`} className="text-indigo-600 hover:text-indigo-800">
              Class
            </Link>
          </li>
          <ChevronRightIcon className="h-5 w-5 text-gray-400" />
          <li className="text-gray-900 font-medium">{course?.title}</li>
        </ol>
      </nav>

      {/* Course Info */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{course?.title}</h1>
        <p className="text-gray-600 mt-1">{course?.description}</p>
      </div>

      {/* Lessons List */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Lessons</h2>
        <div className="space-y-3">
          {lessons?.map((lesson, index) => (
            <Link
              key={lesson.id}
              to={`/classes/${classId}/courses/${courseId}/lessons/${lesson.id}`}
              className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">
                    Lesson {index + 1}: {lesson.title}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {lesson.deck_count} decks • {lesson.card_count} cards
                  </p>
                </div>
                <div className="text-sm text-gray-500">
                  {lesson.completion_percentage}% Complete
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};
```

#### **Implementation Checklist**
- [ ] **Class Management UI**
  - [ ] Class dashboard with overview
  - [ ] Class creation and editing forms
  - [ ] Student enrollment management
  - [ ] Class settings and permissions

- [ ] **Course Management UI**
  - [ ] Course listing and navigation
  - [ ] Course creation and editing
  - [ ] Lesson organization interface
  - [ ] Course progress tracking

- [ ] **Lesson Management UI**
  - [ ] Lesson detail view
  - [ ] Deck management within lessons
  - [ ] Lesson completion tracking
  - [ ] Study session launcher

---

## 📚 STUDY INTERFACE

### **7.5 Study Session UI (Decision #9: SM-2 + #11: Multiple Modes)**

#### **Study Session Component**
```typescript
// src/pages/study/StudySession.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useStudySession, useAnswerFlashcard } from '../../hooks/useStudy';
import { StudyModeSelector } from '../../components/study/StudyModeSelector';
import { FlashcardDisplay } from '../../components/study/FlashcardDisplay';
import { StudyProgress } from '../../components/study/StudyProgress';
import { StudySessionComplete } from '../../components/study/StudySessionComplete';
import type { StudyMode } from '../../types/study';

export const StudySession: React.FC = () => {
  const { deckId } = useParams();
  const navigate = useNavigate();
  
  const [studyMode, setStudyMode] = useState<StudyMode>('review');
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [sessionStarted, setSessionStarted] = useState(false);

  const {
    data: session,
    mutate: startSession,
    isLoading: isStarting,
  } = useStudySession();

  const answerMutation = useAnswerFlashcard();

  const startStudySession = async () => {
    await startSession({
      deck_id: deckId!,
      study_mode: studyMode,
      target_cards: 20,
    });
    setSessionStarted(true);
  };

  const handleAnswer = async (quality: number, responseTime: number) => {
    const currentCard = session?.scheduled_cards[currentCardIndex];
    if (!currentCard) return;

    await answerMutation.mutateAsync({
      session_id: session.id,
      flashcard_id: currentCard.id,
      quality,
      response_time: responseTime,
    });

    // Move to next card or complete session
    if (currentCardIndex < session.scheduled_cards.length - 1) {
      setCurrentCardIndex(currentCardIndex + 1);
      setShowAnswer(false);
    } else {
      // Session complete
      navigate(`/study/sessions/${session.id}/complete`);
    }
  };

  if (!sessionStarted) {
    return (
      <div className="max-w-2xl mx-auto py-8">
        <StudyModeSelector
          selectedMode={studyMode}
          onModeChange={setStudyMode}
          deckId={deckId!}
          onStart={startStudySession}
          isLoading={isStarting}
        />
      </div>
    );
  }

  if (!session || session.is_completed) {
    return <StudySessionComplete sessionId={session?.id} />;
  }

  const currentCard = session.scheduled_cards[currentCardIndex];

  return (
    <div className="max-w-4xl mx-auto py-8">
      {/* Progress Header */}
      <StudyProgress
        current={currentCardIndex + 1}
        total={session.scheduled_cards.length}
        correct={session.correct_answers}
        accuracy={session.accuracy_rate}
      />

      {/* Flashcard Display */}
      <div className="mt-8">
        <FlashcardDisplay
          flashcard={currentCard}
          showAnswer={showAnswer}
          onShowAnswer={() => setShowAnswer(true)}
          onAnswer={handleAnswer}
          studyMode={studyMode}
        />
      </div>
    </div>
  );
};
```

#### **Flashcard Display Component**
```typescript
// src/components/study/FlashcardDisplay.tsx
import React, { useState, useEffect } from 'react';
import { Button } from '../ui/Button';
import type { FlashcardStudyResponse, StudyMode } from '../../types/study';

interface FlashcardDisplayProps {
  flashcard: FlashcardStudyResponse;
  showAnswer: boolean;
  onShowAnswer: () => void;
  onAnswer: (quality: number, responseTime: number) => void;
  studyMode: StudyMode;
}

export const FlashcardDisplay: React.FC<FlashcardDisplayProps> = ({
  flashcard,
  showAnswer,
  onShowAnswer,
  onAnswer,
  studyMode,
}) => {
  const [startTime, setStartTime] = useState<number>(Date.now());

  useEffect(() => {
    setStartTime(Date.now());
  }, [flashcard.id]);

  const handleAnswer = (quality: number) => {
    const responseTime = (Date.now() - startTime) / 1000;
    onAnswer(quality, responseTime);
  };

  const getDifficultyButtons = () => {
    if (studyMode === 'test') {
      // Test mode: only correct/incorrect
      return (
        <div className="flex space-x-4 justify-center">
          <Button
            onClick={() => handleAnswer(1)}
            className="bg-red-600 hover:bg-red-700"
          >
            Incorrect
          </Button>
          <Button
            onClick={() => handleAnswer(4)}
            className="bg-green-600 hover:bg-green-700"
          >
            Correct
          </Button>
        </div>
      );
    }

    // Standard SM-2 difficulty buttons
    return (
      <div className="flex space-x-2 justify-center">
        <Button
          onClick={() => handleAnswer(1)}
          className="bg-red-600 hover:bg-red-700 text-sm"
        >
          Again
        </Button>
        <Button
          onClick={() => handleAnswer(2)}
          className="bg-orange-600 hover:bg-orange-700 text-sm"
        >
          Hard
        </Button>
        <Button
          onClick={() => handleAnswer(3)}
          className="bg-yellow-600 hover:bg-yellow-700 text-sm"
        >
          Good
        </Button>
        <Button
          onClick={() => handleAnswer(4)}
          className="bg-green-600 hover:bg-green-700 text-sm"
        >
          Easy
        </Button>
      </div>
    );
  };

  return (
    <div className="bg-white shadow-lg rounded-lg p-8 min-h-[400px]">
      {/* Question Side */}
      <div className="mb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Question</h3>
        <div className="text-xl text-gray-800">
          {flashcard.question}
        </div>
        {flashcard.question_image && (
          <img
            src={flashcard.question_image}
            alt="Question"
            className="mt-4 max-w-md rounded-lg"
          />
        )}
        {flashcard.question_audio && (
          <audio controls className="mt-4">
            <source src={flashcard.question_audio} type="audio/mpeg" />
          </audio>
        )}
      </div>

      {/* Answer Side */}
      {showAnswer ? (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Answer</h3>
          <div className="text-xl text-gray-800 mb-4">
            {flashcard.answer}
          </div>
          {flashcard.answer_image && (
            <img
              src={flashcard.answer_image}
              alt="Answer"
              className="mb-4 max-w-md rounded-lg"
            />
          )}
          {flashcard.answer_audio && (
            <audio controls className="mb-4">
              <source src={flashcard.answer_audio} type="audio/mpeg" />
            </audio>
          )}
          
          {flashcard.hint && (
            <div className="text-sm text-gray-600 mb-4">
              <strong>Hint:</strong> {flashcard.hint}
            </div>
          )}
          
          {flashcard.explanation && (
            <div className="text-sm text-gray-600 mb-6">
              <strong>Explanation:</strong> {flashcard.explanation}
            </div>
          )}

          {/* Difficulty Buttons */}
          <div className="border-t pt-6">
            <p className="text-center text-gray-600 mb-4">
              How did you do?
            </p>
            {getDifficultyButtons()}
          </div>
        </div>
      ) : (
        <div className="text-center">
          <Button
            onClick={onShowAnswer}
            className="bg-indigo-600 hover:bg-indigo-700"
          >
            Show Answer
          </Button>
        </div>
      )}
    </div>
  );
};
```

#### **Implementation Checklist**
- [ ] **Study Session UI**
  - [ ] Study mode selection interface
  - [ ] Interactive flashcard display
  - [ ] Progress tracking during session
  - [ ] Session completion summary

- [ ] **Study Features**
  - [ ] Multiple study modes support
  - [ ] SM-2 difficulty rating buttons
  - [ ] Multimedia content display
  - [ ] Response time tracking

---

## 📁 IMPORT/EXPORT UI

### **7.6 File Management Interface (Decision #15: CSV+JSON + #16: Multi-format)**

#### **Import Interface**
```typescript
// src/pages/decks/ImportDeck.tsx
import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useImportDeck } from '../../hooks/useDecks';
import { Button } from '../../components/ui/Button';
import { FileFormatSelector } from '../../components/import/FileFormatSelector';
import { ImportPreview } from '../../components/import/ImportPreview';
import type { ImportFormat } from '../../types/import';

export const ImportDeck: React.FC = () => {
  const [selectedFormat, setSelectedFormat] = useState<ImportFormat>('csv');
  const [file, setFile] = useState<File | null>(null);
  const [previewData, setPreviewData] = useState<any>(null);

  const importMutation = useImportDeck();

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      const uploadedFile = acceptedFiles[0];
      setFile(uploadedFile);
      
      // Generate preview
      generatePreview(uploadedFile, selectedFormat);
    },
  });

  const generatePreview = async (file: File, format: ImportFormat) => {
    const text = await file.text();
    
    if (format === 'csv') {
      // Parse CSV and show preview
      const lines = text.split('\n').slice(0, 5); // First 5 rows
      setPreviewData({ type: 'csv', lines });
    } else if (format === 'json') {
      // Parse JSON and show preview
      try {
        const data = JSON.parse(text);
        setPreviewData({ type: 'json', data: data.slice(0, 5) });
      } catch (error) {
        setPreviewData({ type: 'error', message: 'Invalid JSON format' });
      }
    }
  };

  const handleImport = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('format', selectedFormat);

    await importMutation.mutateAsync(formData);
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Import Deck</h1>

      {/* Format Selection */}
      <div className="mb-8">
        <FileFormatSelector
          selectedFormat={selectedFormat}
          onFormatChange={setSelectedFormat}
        />
      </div>

      {/* File Upload */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-indigo-500 bg-indigo-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <div className="text-gray-600">
          {isDragActive ? (
            <p>Drop the file here...</p>
          ) : (
            <div>
              <p className="text-lg mb-2">
                Drag & drop a file here, or click to select
              </p>
              <p className="text-sm">
                Supports CSV, JSON, and TXT formats
              </p>
            </div>
          )}
        </div>
      </div>

      {/* File Preview */}
      {file && previewData && (
        <div className="mt-8">
          <ImportPreview
            file={file}
            previewData={previewData}
            format={selectedFormat}
          />
        </div>
      )}

      {/* Import Button */}
      {file && (
        <div className="mt-8 text-center">
          <Button
            onClick={handleImport}
            loading={importMutation.isLoading}
            disabled={importMutation.isLoading}
            className="bg-green-600 hover:bg-green-700"
          >
            Import Deck
          </Button>
        </div>
      )}
    </div>
  );
};
```

#### **Export Interface**
```typescript
// src/components/decks/ExportDeck.tsx
import React, { useState } from 'react';
import { useExportDeck } from '../../hooks/useDecks';
import { Button } from '../ui/Button';
import { Modal } from '../ui/Modal';
import type { ExportFormat } from '../../types/export';

interface ExportDeckProps {
  deckId: string;
  deckTitle: string;
  isOpen: boolean;
  onClose: () => void;
}

export const ExportDeck: React.FC<ExportDeckProps> = ({
  deckId,
  deckTitle,
  isOpen,
  onClose,
}) => {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('csv');
  const [includeProgress, setIncludeProgress] = useState(false);
  const [includeMultimedia, setIncludeMultimedia] = useState(false);

  const exportMutation = useExportDeck();

  const handleExport = async () => {
    const blob = await exportMutation.mutateAsync({
      deck_id: deckId,
      format: selectedFormat,
      include_progress: includeProgress,
      include_multimedia: includeMultimedia,
    });

    // Download file
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${deckTitle}.${selectedFormat}`;
    link.click();
    window.URL.revokeObjectURL(url);

    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Export Deck">
      <div className="space-y-6">
        {/* Format Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Export Format
          </label>
          <div className="space-y-2">
            {(['csv', 'json', 'anki'] as ExportFormat[]).map((format) => (
              <label key={format} className="flex items-center">
                <input
                  type="radio"
                  value={format}
                  checked={selectedFormat === format}
                  onChange={(e) => setSelectedFormat(e.target.value as ExportFormat)}
                  className="mr-2"
                />
                <span className="capitalize">{format}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Export Options */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Export Options
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeProgress}
                onChange={(e) => setIncludeProgress(e.target.checked)}
                className="mr-2"
              />
              Include learning progress
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeMultimedia}
                onChange={(e) => setIncludeMultimedia(e.target.checked)}
                className="mr-2"
              />
              Include multimedia files
            </label>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleExport}
            loading={exportMutation.isLoading}
            disabled={exportMutation.isLoading}
          >
            Export
          </Button>
        </div>
      </div>
    </Modal>
  );
};
```

#### **Implementation Checklist**
- [ ] **Import UI**
  - [ ] Drag & drop file upload
  - [ ] Format selection (CSV, JSON, TXT)
  - [ ] File preview before import
  - [ ] Import progress indication

- [ ] **Export UI**
  - [ ] Format selection (CSV, JSON, Anki)
  - [ ] Export options (progress, multimedia)
  - [ ] Download functionality
  - [ ] Export progress indication

---

## 📊 PROGRESS VISUALIZATION

### **7.7 Analytics Dashboard (Decision #12: Standard Analytics)**

#### **Progress Charts Component**
```typescript
// src/components/analytics/ProgressCharts.tsx
import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useProgressCharts } from '../../hooks/useAnalytics';

interface ProgressChartsProps {
  resourceId: string;
  resourceType: 'deck' | 'lesson' | 'course' | 'class';
  timeRange: number; // days
}

export const ProgressCharts: React.FC<ProgressChartsProps> = ({
  resourceId,
  resourceType,
  timeRange,
}) => {
  const { data: chartData, isLoading } = useProgressCharts(
    resourceId,
    resourceType,
    timeRange
  );

  if (isLoading || !chartData) {
    return <div>Loading charts...</div>;
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Daily Progress Line Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Daily Progress
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData.daily_progress}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="cards_studied"
              stroke="#8884d8"
              name="Cards Studied"
            />
            <Line
              type="monotone"
              dataKey="accuracy"
              stroke="#82ca9d"
              name="Accuracy %"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Study Time Bar Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Study Time (Minutes)
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData.daily_progress}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="time_spent" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Accuracy Distribution Pie Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Card Difficulty Distribution
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData.difficulty_distribution}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) =>
                `${name} ${(percent * 100).toFixed(0)}%`
              }
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.difficulty_distribution.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Statistics Summary */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Summary</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-indigo-600">
              {chartData.summary.total_cards}
            </div>
            <div className="text-sm text-gray-600">Total Cards</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {chartData.summary.average_accuracy.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Avg Accuracy</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {Math.round(chartData.summary.total_time / 60)}h
            </div>
            <div className="text-sm text-gray-600">Study Time</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {chartData.summary.current_streak}
            </div>
            <div className="text-sm text-gray-600">Day Streak</div>
          </div>
        </div>
      </div>
    </div>
  );
};
```

#### **Implementation Checklist**
- [ ] **Analytics UI**
  - [ ] Progress charts with Recharts
  - [ ] Multi-level analytics views
  - [ ] Time range selection
  - [ ] Performance statistics

- [ ] **Chart Types**
  - [ ] Daily progress line charts
  - [ ] Study time bar charts
  - [ ] Accuracy distribution
  - [ ] Summary statistics cards

---

## 🧪 TESTING CHECKLIST

### **Frontend Component Tests**
- [ ] **Authentication Tests**
  - [ ] Login/register form validation
  - [ ] Protected route behavior
  - [ ] Role-based access control
  - [ ] Token refresh handling

- [ ] **UI Component Tests**
  - [ ] Class/course/lesson navigation
  - [ ] Study session workflow
  - [ ] Import/export functionality
  - [ ] Progress visualization

### **Integration Tests**
- [ ] **API Integration Tests**
  - [ ] Authentication flow
  - [ ] CRUD operations
  - [ ] File upload/download
  - [ ] Real-time updates

### **E2E Tests**
- [ ] **User Journey Tests**
  - [ ] Complete study session
  - [ ] Class management workflow
  - [ ] Import deck and study
  - [ ] Progress tracking

---

## 📋 COMPLETION CRITERIA

✅ **Phase 7 Complete When:**
- [ ] React TypeScript frontend fully functional
- [ ] Authentication UI implemented
- [ ] 3-level hierarchy navigation working
- [ ] Study interface with all modes complete
- [ ] Import/export UI functional
- [ ] Progress visualization working
- [ ] Role-based access control implemented
- [ ] Mobile responsive design
- [ ] Comprehensive testing completed
- [ ] Performance optimization done

---

## 🔄 NEXT PHASE
**PHASE 8**: Testing & QA
- Implement comprehensive testing strategy
- Set up automated testing pipelines
- Perform security and performance testing

---

*Part of comprehensive Flashcard LMS implementation*  
*Based on 20 decisions from DECISION_FRAMEWORK.md*
