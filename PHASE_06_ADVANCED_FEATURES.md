# 📚 PHASE 6: STUDY SYSTEM IMPLEMENTATION
*Learning and progress tracking (Decision #9: SM-2 + #10: Advanced + #11: Multiple Modes)*

## 📋 Overview
**Phase Goal**: Implement comprehensive study system with spaced repetition  
**Dependencies**: Phase 5 (3-Level Hierarchy Management)  
**Estimated Time**: 5-6 days  
**Priority**: HIGH PRIORITY

---

## 🎯 PHASE OBJECTIVES

### **6.1 Study Session APIs (Decision #10: Advanced + #11: Multiple Modes)**
- [ ] Study session management
- [ ] Multiple study modes implementation

### **6.2 Spaced Repetition System (Decision #9: SM-2)**
- [ ] SM-2 algorithm implementation
- [ ] SRS scheduling APIs

### **6.3 Progress Tracking (Decision #12: Standard Analytics + #13: Session-based)**
- [ ] Progress APIs across hierarchy levels
- [ ] Analytics & charts implementation
- [ ] Session-based updates

---

## 🎮 STUDY SESSION SYSTEM

### **6.1 Study Session Management**

#### **Study Session Endpoints**
```python
# POST /api/v1/study/sessions/start
@router.post("/sessions/start", response_model=StudySessionResponse)
async def start_study_session(
    session_data: StudySessionStartRequest,
    current_user: User = Depends(get_current_user)
):
    # Validate deck access
    await permission_service.validate_deck_access(current_user.id, session_data.deck_id)
    
    # Get due cards based on study mode
    cards = await study_service.get_cards_for_session(
        user_id=current_user.id,
        deck_id=session_data.deck_id,
        study_mode=session_data.study_mode,
        target_cards=session_data.target_cards
    )
    
    session = await study_service.create_session({
        **session_data.dict(),
        "user_id": current_user.id,
        "cards_scheduled": len(cards)
    })
    
    return StudySessionResponse(**session.dict(), scheduled_cards=cards)

# PUT /api/v1/study/sessions/{session_id}/answer
@router.put("/sessions/{session_id}/answer")
async def answer_flashcard(
    session_id: str,
    answer_data: FlashcardAnswerRequest,
    current_user: User = Depends(get_current_user)
):
    # Validate session ownership
    session = await study_service.get_session(session_id)
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your study session")
    
    # Process answer and update SM-2 data
    result = await study_service.process_answer(
        session_id=session_id,
        flashcard_id=answer_data.flashcard_id,
        quality=answer_data.quality,
        response_time=answer_data.response_time
    )
    
    return result
```

#### **Study Session Models**
```python
class StudySessionStartRequest(BaseModel):
    deck_id: str
    lesson_id: str?
    study_mode: StudyMode
    target_time: int? = Field(gt=0)  # minutes
    target_cards: int? = Field(gt=0)
    break_reminders_enabled: bool = True

class StudySessionResponse(BaseModel):
    id: str
    user_id: str
    deck_id: str
    lesson_id: str?
    study_mode: StudyMode
    target_time: int?
    target_cards: int?
    break_reminders_enabled: bool
    
    # Session Progress
    cards_studied: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    total_time: int = 0  # seconds
    break_count: int = 0
    is_completed: bool = False
    
    # Session Analytics
    accuracy_rate: float?
    average_response_time: float?
    
    # Scheduled Cards for this session
    scheduled_cards: List[FlashcardStudyResponse]
    
    created_at: datetime
    updated_at: datetime

class FlashcardAnswerRequest(BaseModel):
    flashcard_id: str
    quality: int = Field(ge=0, le=5)  # SM-2 quality rating
    response_time: float  # seconds
    was_correct: bool

class StudyMode(str, Enum):
    REVIEW = "review"        # SRS-based review
    PRACTICE = "practice"    # Non-SRS practice
    CRAM = "cram"           # Rapid review
    TEST = "test"           # Assessment mode
    LEARN = "learn"         # New card introduction
```

#### **Implementation Checklist**
- [ ] **Study Session Management**
  - [ ] `POST /api/v1/study/sessions/start` (with mode selection)
  - [ ] `GET /api/v1/study/sessions/{id}`
  - [ ] `PUT /api/v1/study/sessions/{id}/answer`
  - [ ] `POST /api/v1/study/sessions/{id}/break` (break reminders)
  - [ ] `POST /api/v1/study/sessions/{id}/complete`

- [ ] **Session Features**
  - [ ] Goal-based sessions (time/card targets)
  - [ ] Break reminder system
  - [ ] Session analytics calculation
  - [ ] Progress tracking during session

### **6.2 Study Modes Implementation (Decision #11: Multiple Modes)**

#### **Study Mode Logic**
```python
class StudyModeHandler:
    @staticmethod
    async def get_cards_for_mode(
        user_id: str, 
        deck_id: str, 
        mode: StudyMode, 
        target_cards: int? = None
    ) -> List[Flashcard]:
        
        if mode == StudyMode.REVIEW:
            # SRS-based: only due cards
            return await srs_service.get_due_cards(user_id, deck_id, limit=target_cards)
            
        elif mode == StudyMode.PRACTICE:
            # Non-SRS: random selection from deck
            return await deck_service.get_random_cards(deck_id, limit=target_cards)
            
        elif mode == StudyMode.CRAM:
            # All cards in deck for rapid review
            return await deck_service.get_all_cards(deck_id, limit=target_cards)
            
        elif mode == StudyMode.TEST:
            # Assessment mode: all cards, no hints
            return await deck_service.get_test_cards(deck_id, limit=target_cards)
            
        elif mode == StudyMode.LEARN:
            # New cards only
            return await srs_service.get_new_cards(user_id, deck_id, limit=target_cards)
```

#### **Implementation Checklist**
- [ ] **Study Modes (Decision #11: Multiple Modes)**
  - [ ] Review mode (SRS-based)
  - [ ] Practice mode (non-SRS)
  - [ ] Cram mode (rapid review)
  - [ ] Test mode (assessment)
  - [ ] Learn mode (new cards introduction)

- [ ] **Mode-Specific Features**
  - [ ] Different card selection algorithms
  - [ ] Mode-specific UI restrictions
  - [ ] Different scoring systems
  - [ ] Mode-appropriate analytics

---

## 🧠 SPACED REPETITION SYSTEM

### **6.3 SM-2 Algorithm Implementation (Decision #9: SM-2)**

#### **SM-2 Algorithm Core**
```python
class SM2Algorithm:
    @staticmethod
    def calculate_next_review(
        quality: int,
        repetitions: int,
        ease_factor: float,
        interval: int
    ) -> tuple[int, float, int, datetime]:
        """
        SM-2 Algorithm Implementation
        
        Args:
            quality: Response quality (0-5)
            repetitions: Number of repetitions
            ease_factor: Current ease factor
            interval: Current interval in days
            
        Returns:
            (new_repetitions, new_ease_factor, new_interval, next_review_date)
        """
        
        if quality >= 3:
            # Correct response
            if repetitions == 0:
                new_interval = 1
            elif repetitions == 1:
                new_interval = 6
            else:
                new_interval = round(interval * ease_factor)
            
            new_repetitions = repetitions + 1
        else:
            # Incorrect response - reset
            new_repetitions = 0
            new_interval = 1
        
        # Update ease factor
        new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        
        # Ensure ease factor doesn't go below 1.3
        new_ease_factor = max(1.3, new_ease_factor)
        
        # Calculate next review date
        next_review = datetime.utcnow() + timedelta(days=new_interval)
        
        return new_repetitions, new_ease_factor, new_interval, next_review

# Usage in study service
async def process_flashcard_answer(
    user_id: str,
    flashcard_id: str,
    quality: int,
    response_time: float
) -> dict:
    
    # Get current flashcard data
    progress = await get_user_flashcard_progress(user_id, flashcard_id)
    
    # Calculate next review using SM-2
    new_repetitions, new_ease_factor, new_interval, next_review = SM2Algorithm.calculate_next_review(
        quality=quality,
        repetitions=progress.repetitions,
        ease_factor=progress.ease_factor,
        interval=progress.interval
    )
    
    # Update flashcard progress
    await update_flashcard_progress(
        user_id=user_id,
        flashcard_id=flashcard_id,
        repetitions=new_repetitions,
        ease_factor=new_ease_factor,
        interval=new_interval,
        next_review=next_review,
        quality=quality
    )
    
    # Update statistics
    await update_review_statistics(user_id, flashcard_id, quality, response_time)
    
    return {
        "next_review": next_review,
        "interval": new_interval,
        "ease_factor": new_ease_factor,
        "quality": quality
    }
```

#### **Implementation Checklist**
- [ ] **SM-2 Algorithm Implementation**
  - [ ] Calculate next review intervals
  - [ ] Update ease factors based on performance
  - [ ] Handle repetition scheduling
  - [ ] Quality rating processing (0-5 scale)

- [ ] **Algorithm Features**
  - [ ] Correct response handling
  - [ ] Incorrect response reset
  - [ ] Ease factor bounds (min 1.3)
  - [ ] Interval progression logic

### **6.4 SRS APIs**

#### **SRS Management Endpoints**
```python
# GET /api/v1/study/due-cards
@router.get("/due-cards", response_model=List[FlashcardStudyResponse])
async def get_due_cards(
    deck_id: str? = None,
    lesson_id: str? = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    due_cards = await srs_service.get_due_cards(
        user_id=current_user.id,
        deck_id=deck_id,
        lesson_id=lesson_id,
        limit=limit
    )
    return [FlashcardStudyResponse(**card.dict()) for card in due_cards]

# POST /api/v1/study/cards/{flashcard_id}/review
@router.post("/cards/{flashcard_id}/review")
async def review_flashcard(
    flashcard_id: str,
    review_data: FlashcardReviewRequest,
    current_user: User = Depends(get_current_user)
):
    result = await srs_service.process_review(
        user_id=current_user.id,
        flashcard_id=flashcard_id,
        quality=review_data.quality,
        response_time=review_data.response_time
    )
    return result

# GET /api/v1/study/schedule
@router.get("/schedule", response_model=StudyScheduleResponse)
async def get_study_schedule(
    days_ahead: int = 7,
    current_user: User = Depends(get_current_user)
):
    schedule = await srs_service.get_study_schedule(
        user_id=current_user.id,
        days_ahead=days_ahead
    )
    return StudyScheduleResponse(**schedule)
```

#### **SRS Models**
```python
class FlashcardStudyResponse(BaseModel):
    id: str
    deck_id: str
    question: str
    answer: str
    hint: str?
    explanation: str?
    
    # Multimedia
    question_image: str?
    answer_image: str?
    question_audio: str?
    answer_audio: str?
    
    # SM-2 Data
    repetitions: int
    ease_factor: float
    interval: int
    next_review: datetime
    
    # Study Statistics
    review_count: int
    correct_count: int
    accuracy_rate: float

class FlashcardReviewRequest(BaseModel):
    quality: int = Field(ge=0, le=5)
    response_time: float  # seconds
    study_mode: StudyMode

class StudyScheduleResponse(BaseModel):
    daily_schedule: List[DailySchedule]
    total_due: int
    total_new: int
    
class DailySchedule(BaseModel):
    date: date
    due_cards: int
    new_cards: int
    estimated_time: int  # minutes
```

#### **Implementation Checklist**
- [ ] **SRS APIs**
  - [ ] `GET /api/v1/study/due-cards`
  - [ ] `POST /api/v1/study/cards/{id}/review`
  - [ ] `GET /api/v1/study/schedule`
  - [ ] `PUT /api/v1/study/cards/{id}/reset-progress`

- [ ] **SRS Features**
  - [ ] Due card calculation
  - [ ] Review processing
  - [ ] Schedule generation
  - [ ] Progress reset capability

---

## 📊 PROGRESS TRACKING

### **6.5 Progress APIs (Decision #12: Standard Analytics + #13: Session-based)**

#### **Progress Tracking Endpoints**
```python
# GET /api/v1/progress/classes/{class_id}
@router.get("/classes/{class_id}", response_model=ClassProgressResponse)
@require_role(UserRole.TEACHER, UserRole.ADMIN)
async def get_class_progress(
    class_id: str,
    current_user: User = Depends(get_current_user)
):
    # Validate class access
    await permission_service.validate_class_access(current_user.id, class_id)
    
    progress = await progress_service.get_class_progress(class_id)
    return ClassProgressResponse(**progress)

# GET /api/v1/progress/courses/{course_id}
@router.get("/courses/{course_id}", response_model=CourseProgressResponse)
async def get_course_progress(
    course_id: str,
    current_user: User = Depends(get_current_user)
):
    await permission_service.validate_course_access(current_user.id, course_id)
    
    progress = await progress_service.get_course_progress(
        user_id=current_user.id,
        course_id=course_id
    )
    return CourseProgressResponse(**progress)

# GET /api/v1/progress/lessons/{lesson_id}
@router.get("/lessons/{lesson_id}", response_model=LessonProgressResponse)
async def get_lesson_progress(
    lesson_id: str,
    current_user: User = Depends(get_current_user)
):
    await permission_service.validate_lesson_access(current_user.id, lesson_id)
    
    progress = await progress_service.get_lesson_progress(
        user_id=current_user.id,
        lesson_id=lesson_id
    )
    return LessonProgressResponse(**progress)
```

#### **Progress Models**
```python
class ClassProgressResponse(BaseModel):
    class_id: str
    class_name: str
    student_count: int
    overall_completion: float
    average_accuracy: float
    total_study_time: int  # seconds
    
    # Student Progress Details
    student_progress: List[StudentProgress]
    
    # Course Progress within Class
    course_progress: List[CourseProgressSummary]

class CourseProgressResponse(BaseModel):
    course_id: str
    course_title: str
    completion_percentage: float
    accuracy_rate: float
    time_spent: int  # seconds
    lessons_completed: int
    total_lessons: int
    
    # Lesson Progress Details
    lesson_progress: List[LessonProgressSummary]
    
    # Charts Data (Decision #12: Standard Analytics)
    daily_progress: List[DailyProgressPoint]
    weekly_progress: List[WeeklyProgressPoint]

class LessonProgressResponse(BaseModel):
    lesson_id: str
    lesson_title: str
    completion_percentage: float
    accuracy_rate: float
    time_spent: int
    cards_mastered: int
    total_cards: int
    current_streak: int
    
    # Deck Progress within Lesson
    deck_progress: List[DeckProgressSummary]
```

#### **Implementation Checklist**
- [ ] **Progress APIs**
  - [ ] `GET /api/v1/progress/classes/{id}`
  - [ ] `GET /api/v1/progress/courses/{id}`
  - [ ] `GET /api/v1/progress/lessons/{id}`
  - [ ] `GET /api/v1/progress/decks/{id}`

- [ ] **Multi-level Tracking**
  - [ ] Class-level progress aggregation
  - [ ] Course-level progress tracking
  - [ ] Lesson-level completion
  - [ ] Deck-level statistics

### **6.6 Analytics & Charts (Decision #12: Standard)**

#### **Analytics Implementation**
```python
class AnalyticsService:
    @staticmethod
    async def calculate_accuracy_rate(user_id: str, resource_id: str, resource_type: str) -> float:
        """Calculate accuracy rate for user on specific resource"""
        sessions = await get_study_sessions(user_id, resource_id, resource_type)
        
        total_answers = sum(s.correct_answers + s.incorrect_answers for s in sessions)
        correct_answers = sum(s.correct_answers for s in sessions)
        
        return (correct_answers / total_answers * 100) if total_answers > 0 else 0.0
    
    @staticmethod
    async def generate_progress_charts(user_id: str, resource_id: str, days: int = 30) -> dict:
        """Generate chart data for progress visualization"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            day_progress = await get_daily_progress(user_id, resource_id, current_date)
            daily_data.append({
                "date": current_date.isoformat(),
                "cards_studied": day_progress.cards_studied,
                "time_spent": day_progress.time_spent,
                "accuracy": day_progress.accuracy_rate
            })
            current_date += timedelta(days=1)
        
        return {
            "daily_progress": daily_data,
            "summary": {
                "total_cards": sum(d["cards_studied"] for d in daily_data),
                "total_time": sum(d["time_spent"] for d in daily_data),
                "average_accuracy": sum(d["accuracy"] for d in daily_data) / len(daily_data)
            }
        }
```

#### **Implementation Checklist**
- [ ] **Analytics & Charts (Decision #12: Standard)**
  - [ ] Accuracy rates calculation
  - [ ] Progress charts data
  - [ ] Study time tracking
  - [ ] Performance trends

- [ ] **Chart Types**
  - [ ] Daily progress charts
  - [ ] Weekly progress summaries
  - [ ] Accuracy trend charts
  - [ ] Study time distribution

### **6.7 Session-based Updates (Decision #13)**

#### **Session Update Logic**
```python
class SessionUpdateService:
    @staticmethod
    async def complete_study_session(session_id: str) -> dict:
        """Complete study session and update all progress tracking"""
        session = await get_study_session(session_id)
        
        # Update user progress
        await update_user_progress(
            user_id=session.user_id,
            deck_id=session.deck_id,
            lesson_id=session.lesson_id,
            session_data=session
        )
        
        # Update study streak
        await update_study_streak(session.user_id)
        
        # Check and award achievements
        await check_achievements(session.user_id, session)
        
        # Update lesson/course completion
        if session.lesson_id:
            await check_lesson_completion(session.user_id, session.lesson_id)
        
        # Generate session summary
        summary = await generate_session_summary(session)
        
        return summary
    
    @staticmethod
    async def update_real_time_progress(session_id: str, flashcard_result: dict):
        """Update progress during session (real-time updates disabled by Decision #13)"""
        # Session-based: only update at completion
        # This method is for internal tracking only
        pass
```

#### **Implementation Checklist**
- [ ] **Session-based Updates (Decision #13)**
  - [ ] Progress update after session completion
  - [ ] Streak calculation and maintenance
  - [ ] Achievement trigger checking

- [ ] **Update Features**
  - [ ] Multi-level progress updates
  - [ ] Completion percentage calculation
  - [ ] Time tracking aggregation
  - [ ] Statistics recalculation

---

## 🧪 TESTING CHECKLIST

### **Study Session Tests**
- [ ] **Session Management Tests**
  - [ ] Session creation with different modes
  - [ ] Answer processing and validation
  - [ ] Session completion workflow
  - [ ] Break reminder functionality

- [ ] **Study Mode Tests**
  - [ ] Review mode (SRS-based)
  - [ ] Practice mode (non-SRS)
  - [ ] Cram mode functionality
  - [ ] Test mode restrictions
  - [ ] Learn mode for new cards

### **SM-2 Algorithm Tests**
- [ ] **Algorithm Tests**
  - [ ] Correct response handling
  - [ ] Incorrect response reset
  - [ ] Ease factor calculations
  - [ ] Interval progression
  - [ ] Edge case scenarios

### **Progress Tracking Tests**
- [ ] **Multi-level Progress Tests**
  - [ ] Class progress aggregation
  - [ ] Course progress tracking
  - [ ] Lesson completion detection
  - [ ] Deck statistics accuracy

- [ ] **Analytics Tests**
  - [ ] Accuracy rate calculations
  - [ ] Chart data generation
  - [ ] Time tracking accuracy
  - [ ] Progress trend analysis

---

## 📋 COMPLETION CRITERIA

✅ **Phase 6 Complete When:**
- [ ] Study session system fully functional
- [ ] All 5 study modes implemented
- [ ] SM-2 algorithm working correctly
- [ ] SRS scheduling operational
- [ ] Multi-level progress tracking working
- [ ] Analytics and charts generating
- [ ] Session-based updates functional
- [ ] Comprehensive testing completed
- [ ] Performance optimization done
- [ ] Algorithm accuracy validated

---

## 🔄 NEXT PHASE
**PHASE 7**: Import/Export & File Handling
- Implement CSV and JSON import/export
- Build file management system
- Create data portability features

---

*Part of comprehensive Flashcard LMS implementation*  
*Based on 20 decisions from DECISION_FRAMEWORK.md*
