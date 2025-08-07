# Database Schema Notes - Based on Decision #1 (Full Role System)

## 📊 Required Collections from Decision #1

### **Core User & Content Collections**
```
users: {
  _id, email, username, hashed_password, role (student/teacher/admin),
  full_name, avatar, created_at, updated_at, is_active,
  // Learning stats
  total_study_time, cards_studied, study_streak, last_study_date
}

decks: {
  _id, title, description, owner_id, privacy_level,
  tags[], category, difficulty_level, card_count,
  created_at, updated_at, study_count, average_rating
}

flashcards: {
  _id, deck_id, question, answer, hint?, explanation?,
  // Rich Content (Decision #6: Multimedia)
  question_image?, answer_image?, question_audio?, answer_audio?,
  formatting_data?, // For text formatting (bold, italic, etc.)
  // SRS data (Decision #9: SM-2 Algorithm)
  repetitions: 0, // Number of successful reviews
  ease_factor: 2.5, // SM-2 ease factor (min: 1.3)
  interval: 0, // Days until next review
  next_review: Date, // Calculated next review date
  quality: null, // Last review quality (0-5)
  // Stats
  review_count, correct_count, incorrect_count,
  created_at, updated_at
}
```

### **Classroom Management Collections (NEW from Decision #1)**
```
classes: {
  _id, name, description, teacher_id, 
  student_ids[], course_id?, 
  start_date, end_date, is_active,
  created_at, updated_at
}

courses: {
  _id, title, description, creator_id (admin/teacher),
  lesson_ids[], category, difficulty_level,
  is_public, enrollment_count,
  created_at, updated_at
}

lessons: {
  _id, title, description, course_id,
  deck_ids[], order_index, 
  learning_objectives[], estimated_time,
  created_at, updated_at
}

enrollments: {
  _id, user_id, class_id?, course_id?,
  enrollment_date, completion_date?, status,
  progress_percentage, last_activity
}
```

### **Study & Analytics Collections**
```
study_sessions: {
  _id, user_id, deck_id, lesson_id?,
  cards_studied, correct_answers, incorrect_answers,
  total_time, is_completed, completed_at,
  created_at, updated_at
}

user_progress: {
  _id, user_id, course_id?, lesson_id?,
  completion_percentage, time_spent,
  cards_mastered, current_streak,
  last_activity, created_at, updated_at
}
```

## 🔗 Relationships & Constraints

### **User Roles Impact:**
- **Student**: Can enroll in classes/courses, study assigned lessons
- **Teacher**: Can create classes, assign courses/lessons, view student progress
- **Admin**: Can create courses, manage all classes, system oversight

### **Privacy Levels (Decision #5 DECIDED):**
- **Private**: Owner only (admin/teacher personal decks)
- **Class-assigned**: Assigned to specific class by admin/teacher
- **Course-assigned**: Part of course curriculum
- **Public**: Everyone can access (community decks)

### **Deck Assignment System:**
```
deck_assignments: {
  _id, deck_id, class_id?, course_id?,
  assigned_by (teacher/admin), assignment_date,
  due_date?, is_required, status (active/archived)
}
```

### **Access Control Logic:**
- **Admin**: Can create decks, assign to any class/course
- **Teacher**: Can create decks, assign to their classes only  
- **Student**: Can access assigned decks + public decks
- **Deck Creator**: Always has full access to their decks

### **Data Flow:**
```
Admin creates Course → Teacher creates Class → Teacher assigns Course to Class
→ Students enroll in Class → Students study Lessons → Progress tracked
```

## 🤔 Open Questions for Decision #14:

1. **Analytics depth**: Simple stats vs detailed learning analytics?
2. **Notifications**: Real-time notifications for assignments/progress?
3. **Achievements**: Gamification with badges/rewards system?
4. **Audit logs**: Track all user actions for admin oversight?

## 🧠 SM-2 Algorithm Implementation Notes (Decision #9):

### **SM-2 Parameters:**
- **Initial ease_factor**: 2.5 (for all new cards)
- **Minimum ease_factor**: 1.3 (prevents cards from becoming too difficult)
- **Quality responses**: 0-5 scale (0=blackout, 5=perfect)
- **Initial intervals**: 1 day, 6 days, then formula-based

### **SM-2 Formula:**
```
If quality >= 3:
  repetitions += 1
  if repetitions == 1: interval = 1
  elif repetitions == 2: interval = 6
  else: interval = previous_interval * ease_factor
  
If quality < 3:
  repetitions = 0
  interval = 1
  
ease_factor = ease_factor + (0.1 - (5-quality) * (0.08 + (5-quality) * 0.02))
```

### **Study Session Flow:**
1. Fetch cards where `next_review <= today`
2. Present card to user
3. User rates quality (0-5)
4. Update SRS parameters using SM-2
5. Calculate next_review date
6. Track statistics

## 📋 Next Decisions Needed:

- **Decision #5**: Deck Privacy (affects deck access in classroom context)
- **Decision #12**: Analytics Depth (affects user_progress collection design)
- **Decision #13**: Real-time Updates (affects notifications collection)

**Ready to continue with Decision #5: Deck Privacy?** 🚀
