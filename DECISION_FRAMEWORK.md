# Flashcard LMS Backend - Structured Decision Framework

## 📋 Project Overview
**Goal**: Build a comprehensive Flashcard Learning Management System  
**Tech Stack**: FastAPI + MongoDB + React TypeScript  
**Approach**: Sequential decision-making with numbered choices

---

## 🎯 DECISION MATRIX

### **SECTION A: AUTHENTICATION & USER MANAGEMENT**

#### **Decision #1: User Role System** ✅ DECIDED
**Context**: Define user permissions and capabilities  
**Options**:
- A) **Simple**: Student-only system (personal flashcards)
- B) **Standard**: Student + Teacher roles (classroom management)  
- C) **Full**: Student + Teacher + Admin roles (enterprise-ready)

**Your Choice**: **C - Full**  
**Reasoning**: Admin & Teacher cần tạo được lớp học, khóa học, bài học. Cần full classroom management system.

**Impact**: 
- Database cần thêm Collections: Classes, Courses, Lessons
- API cần endpoints cho classroom management
- Permission system phức tạp hơn (role-based + resource-based)
- **3-level hierarchy**: Classes → Courses → Lessons

---

#### **Decision #2: Email Verification** ✅
**Context**: Account registration security vs user friction  
**Options**:
- A) **Required**: Must verify email before using system
- B) **Optional**: Can use immediately, email verification for features
- C) **Skip MVP**: No email verification in first version

**Your Choice**: B - Optional  
**Reasoning**: Good balance for classroom environment - users can start using immediately for quick setup, while email verification can be enabled for advanced features or security. Teachers can onboard students faster.

---

#### **Decision #3: Password Reset System** ✅
**Context**: User account recovery mechanism  
**Options**:
- A) **Email-based**: Reset via email link (requires email service)
- B) **Admin-reset**: Only admins can reset passwords
- C) **Skip MVP**: Manual process for first version

**Your Choice**: B - Admin-reset  
**Reasoning**: Perfect for classroom environment - simple implementation, good control. Teachers can reset passwords for students they created, Admins can reset any password. No email service dependency, secure and manageable.

---

#### **Decision #4: User Profile Information** ✅
**Context**: What data to store about users  
**Options**:
- A) **Minimal**: Email, username, password only
- B) **Standard**: + Full name, avatar, bio, learning preferences
- C) **Extended**: + Learning goals, study schedule, achievements

**Your Choice**: C - Extended  
**Reasoning**: Comprehensive LMS needs rich user profiles. Learning goals and study schedules enable personalized learning paths. Achievements motivate students. Teachers can better understand and support individual student needs.

---

### **SECTION B: DECK & FLASHCARD MANAGEMENT**

#### **Decision #5: Deck Privacy Levels** ✅ DECIDED
**Context**: Who can access and view decks  
**Options**:
- A) **Simple**: Private (owner only) or Public (everyone)
- B) **Standard**: Private, Public, Shared (specific users)
- C) **Advanced**: + Organization-level, Class-level permissions

**Your Choice**: **C - Advanced**  
**Reasoning**: Admin & Teacher tạo decks, sau đó assign decks to class/course/lesson. Cần multi-level permissions để students có thể access assigned decks.

**Impact**: 
- Deck privacy: Private, Class-assigned, Course-assigned, Lesson-assigned, Public
- Assignment system: decks được assign to classes, courses, hoặc specific lessons
- Access control phức tạp: role + resource + assignment based
- **3-level assignment**: Class level, Course level, Lesson level

---

#### **Decision #6: Flashcard Content Types** ✅
**Context**: What types of content to support  
**Options**:
- A) **Text-only**: Question/answer pairs with text
- B) **Text + Basic**: + Optional hint and explanation fields
- C) **Multimedia**: + Images, audio, formatting support

**Your Choice**: C - Multimedia (with optional image/audio fields)  
**Reasoning**: Rich content with images and audio enhances learning effectiveness, especially for visual/auditory learners. Optional fields maintain flexibility while supporting diverse learning styles.

---

#### **Decision #7: Deck Categories System** ✅
**Context**: How to organize and categorize decks  
**Options**:
- A) **Free tags**: Users create their own tags
- B) **Predefined**: System-defined categories + custom tags
- C) **Hierarchical**: Nested categories with subcategories

**Your Choice**: B - Predefined  
**Reasoning**: In classroom environment, teachers/admins need structured categories for better organization. Predefined categories ensure consistency while custom tags provide flexibility for specific needs.

---

#### **Decision #8: Import/Export Features** ✅
**Context**: Data portability and integration  
**Options**:
- A) **JSON only**: Simple backup/restore functionality
- B) **CSV + JSON**: Excel-compatible import/export
- C) **Multi-format**: + Anki, Quizlet compatibility

**Your Choice**: B - CSV + JSON  
**Reasoning**: Teachers often work with Excel/CSV for student data and flashcard content. JSON for technical backup/restore. Good balance between functionality and implementation complexity for classroom environment.

---

### **SECTION C: LEARNING & STUDY SYSTEM**

#### **Decision #9: Spaced Repetition Algorithm** ✅
**Context**: How to schedule card reviews  
**Options**:
- A) **Simple**: Fixed intervals (1, 3, 7, 14, 30 days)
- B) **SM-2**: SuperMemo 2 algorithm with ease factors
- C) **Advanced**: SM-18 or custom adaptive algorithm

**Your Choice**: B - SM-2  
**Reasoning**: SM-2 is proven effective, widely used (Anki uses it), and offers good balance between simplicity and performance. It adapts to individual card difficulty while being straightforward to implement.

---

#### **Decision #10: Study Session Features** ✅
**Context**: How to structure study sessions  
**Options**:
- A) **Basic**: Review due cards until none left
- B) **Goal-based**: Set targets (time limit, card count)
- C) **Advanced**: + Break reminders, session analytics

**Your Choice**: C - Advanced (+ Break reminders, session analytics)  
**Reasoning**: In classroom environment, teachers need to set study goals for students (time limits, card counts) AND need detailed session analytics to track student progress and performance for better teaching insights. Break reminders help with student wellness.

---

#### **Decision #11: Study Modes** ✅
**Context**: Different ways to practice flashcards  
**Options**:
- A) **Review only**: Study due cards based on SRS
- B) **Review + Learn**: + New card introduction mode
- C) **Multiple modes**: + Practice, Cram, Test modes

**Your Choice**: C - Multiple modes  
**Reasoning**: Teachers need to assign specific study modes for different situations (practice before exams, cram sessions, formal tests). Implementation complexity is manageable with good design - just different session configurations and rules.

---

### **SECTION D: ANALYTICS & PROGRESS TRACKING**

#### **Decision #12: User Statistics Depth** ✅
**Context**: How much data to track and display  
**Options**:
- A) **Basic**: Total cards studied, study time, streak
- B) **Standard**: + Accuracy rates, progress charts
- C) **Detailed**: + Learning curves, performance analytics

**Your Choice**: B - Standard  
**Reasoning**: Standard analytics provide good balance - teachers get accuracy rates and progress charts for effective monitoring without overwhelming complexity. Sufficient for classroom insights.

---

#### **Decision #13: Real-time Updates** ✅
**Context**: How frequently to update progress data  
**Options**:
- A) **Session-based**: Update after each study session
- B) **Real-time**: Live updates during study
- C) **Batch**: Daily/periodic summary updates

**Your Choice**: A - Session-based  
**Reasoning**: For classroom environment, session-based updates provide good balance. Teachers get timely progress updates without the complexity of real-time infrastructure. Simpler to implement and maintain.

---

### **SECTION E: TECHNICAL ARCHITECTURE**

#### **Decision #14: Database Collections** ✅ 🔄 UPDATED by Decision #1
**Context**: How to structure MongoDB collections  
**Options**:
- A) **Minimal**: Users, Decks, Flashcards only
- B) **Standard**: + StudySessions, UserProgress
- C) **Comprehensive**: + Analytics, Achievements, Notifications

**Forced by Decision #1**: Must include classroom management collections:
- **Core Collections**: `users`, `decks`, `flashcards`, `study_sessions`
- **Classroom Collections**: `classes`, `courses`, `lessons`, `enrollments`
- **Extended Collections**: `user_progress`, `analytics`, `notifications`
- **Hierarchy**: Classes → Courses → Lessons (3-level structure)

**Your Choice**: C - Comprehensive  
**Reasoning**: Need detailed analytics, achievements for student motivation, and notification system for classroom assignments. 3-level hierarchy requires comprehensive data tracking across all levels.

---

#### **Decision #15: API Versioning Strategy** ✅
**Context**: How to handle API evolution  
**Options**:
- A) **No versioning**: Single API version for MVP
- B) **URL versioning**: /api/v1/, /api/v2/ structure
- C) **Header versioning**: Version in request headers

**Your Choice**: B - URL versioning  
**Reasoning**: Industry standard approach, clear and easy for frontend developers to understand. Better for documentation and API evolution planning. /api/v1/ structure is widely recognized.

---

#### **Decision #16: Performance Optimization** ✅
**Context**: What optimizations to implement initially  
**Options**:
- A) **Basic**: Simple pagination for lists
- B) **Standard**: + Database indexing, response caching
- C) **Advanced**: + Rate limiting, CDN, query optimization

**Your Choice**: B - Standard  
**Reasoning**: Good balance for production-ready system. Database indexing and response caching are essential for classroom environment with multiple users. Provides solid performance foundation without over-engineering.

---

#### **Decision #17: File Storage Strategy** ✅
**Context**: How to store multimedia files (images, audio)  
**Options**:
- A) **Local file storage**: Store files on server filesystem
- B) **Cloud storage**: AWS S3, CloudFlare R2, etc.
- C) **Database storage**: MongoDB GridFS

**Your Choice**: A - Local file storage  
**Reasoning**: For classroom environment, local storage is simpler to implement and maintain. No cloud service dependencies or costs. Suitable for moderate file volumes in educational settings.

---

#### **Decision #18: Notification System** ✅
**Context**: How to notify users about assignments, progress, etc.  
**Options**:
- A) **In-app notifications only**: Simple notification center in UI
- B) **In-app + Email**: Add email notifications for important events
- C) **Multi-channel**: + Push notifications for mobile

**Your Choice**: A - In-app notifications only  
**Reasoning**: Keeps system simple and focused. Teachers and students are already in the app for learning activities. No email service dependencies. Easy to implement with notification collection in database.

---

#### **Decision #19: Security & Data Protection** ✅
**Context**: Security measures and compliance requirements  
**Options**:
- A) **Basic authentication**: JWT tokens, password hashing
- B) **Standard security**: + Rate limiting, input validation, audit logs
- C) **Enterprise security**: + GDPR compliance, advanced monitoring

**Your Choice**: A - Basic authentication  
**Reasoning**: For educational environment, basic security is sufficient for MVP. JWT tokens and proper password hashing provide good security foundation. Can be enhanced later as system grows.

---

#### **Decision #20: Classroom Hierarchy Structure** ✅
**Context**: Define the organizational structure for classroom management  
**Options**:
- A) **2-level**: Classes → Lessons (simple structure)
- B) **3-level**: Classes → Courses → Lessons (comprehensive)
- C) **Flexible**: Dynamic hierarchy based on institution needs

**Your Choice**: B - 3-level hierarchy (Classes → Courses → Lessons)  
**Reasoning**: Provides comprehensive educational structure. Classes represent physical classrooms, Courses represent subjects/curricula, Lessons represent specific topics. Enables detailed organization and progress tracking across all levels.

**Implementation Details**:
- **Classes**: Physical classroom (e.g., "Grade 10A", "Math Advanced Class")
- **Courses**: Subject curriculum (e.g., "Algebra I", "English Literature") 
- **Lessons**: Specific topics (e.g., "Linear Equations", "Shakespeare's Hamlet")
- **Deck Assignment**: Decks can be assigned at Class, Course, or Lesson level
- **Student Enrollment**: Students enroll in Classes, get access to all Courses/Lessons

---

## 📊 DECISION SUMMARY TABLE

| Decision # | Topic | Choice | Status |
|------------|-------|--------|--------|
| #1 | User Roles | **C - Full** | ✅ **DECIDED** |
| #2 | Email Verification | **B - Optional** | ✅ **DECIDED** |
| #3 | Password Reset | **B - Admin-reset** | ✅ **DECIDED** |
| #4 | User Profile | **C - Extended** | ✅ **DECIDED** |
| #5 | Deck Privacy | **C - Advanced** | ✅ **DECIDED** |
| #6 | Content Types | **C - Multimedia** | ✅ **DECIDED** |
| #7 | Categories | **B - Predefined** | ✅ **DECIDED** |
| #8 | Import/Export | **B - CSV+JSON** | ✅ **DECIDED** |
| #9 | SRS Algorithm | **B - SM-2** | ✅ **DECIDED** |
| #10 | Study Sessions | **C - Advanced** | ✅ **DECIDED** |
| #11 | Study Modes | **C - Multiple** | ✅ **DECIDED** |
| #12 | Analytics Depth | **B - Standard** | ✅ **DECIDED** |
| #13 | Real-time Updates | **A - Session-based** | ✅ **DECIDED** |
| #14 | DB Collections | **C - Comprehensive** | ✅ **DECIDED** |
| #15 | API Versioning | **B - URL** | ✅ **DECIDED** |
| #16 | Performance | **B - Standard** | ✅ **DECIDED** |
| #17 | File Storage | **A - Local** | ✅ **DECIDED** |
| #18 | Notifications | **A - In-app only** | ✅ **DECIDED** |
| #19 | Security | **A - Basic auth** | ✅ **DECIDED** |
| #20 | Classroom Hierarchy | **B - 3-level** | ✅ **DECIDED** |

---

## 🎯 DISCUSSION WORKFLOW

### **Phase 1: Core Decisions (Must Decide)** ✅ COMPLETED
Priority decisions that affect everything else:
- [x] Decision #1: User Roles
- [x] Decision #5: Deck Privacy  
- [x] Decision #6: Content Types
- [x] Decision #9: SRS Algorithm

### **Phase 2: Feature Decisions (Should Decide)** ✅ COMPLETED
Important for user experience:
- [x] Decision #7: Categories
- [x] Decision #10: Study Sessions
- [x] Decision #11: Study Modes
- [x] Decision #12: Analytics Depth

### **Phase 3: Technical Decisions (Can Defer)** ✅ COMPLETED
Implementation details:
- [x] Decision #14: DB Collections
- [x] Decision #15: API Versioning
- [x] Decision #16: Performance
- [x] Decision #17: File Storage
- [x] Decision #19: Security

### **Phase 4: Polish Decisions (Optional for MVP)** ✅ COMPLETED
Nice-to-have features:
- [x] Decision #2: Email Verification
- [x] Decision #3: Password Reset
- [x] Decision #8: Import/Export
- [x] Decision #13: Real-time Updates
- [x] Decision #18: Notifications

---

## 🗣️ HOW TO USE THIS DOCUMENT

1. **Start with Phase 1** - Make core architectural decisions first
2. **For each decision**: Choose A, B, or C and explain your reasoning  
3. **Reference previous decisions** when they impact current choices
4. **Update the summary table** as we progress
5. **Generate implementation steps** after all decisions are made

## 🎉 **ALL DECISIONS COMPLETED!**

**Status**: ✅ **FRAMEWORK COMPLETE** - All 20 decisions finalized  
**Next Step**: Ready to proceed with implementation planning and project setup! 🚀

**Summary**: 
- **20/20 decisions** completed across all phases
- **Comprehensive classroom LMS** with full 3-level hierarchy (Classes → Courses → Lessons)
- **Balanced complexity** - enterprise features with manageable implementation
- **Tech stack aligned** - FastAPI + MongoDB + React TypeScript ready
