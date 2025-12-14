# Pop Quiz Feature - Implementation Summary

## Overview
Added a fourth toggle button "Pop Quiz" that displays 5 randomly selected very-short questions from the current chapter. If fewer than 5 very-short questions exist, it shows all available ones.

## Changes Made

### 1. BottomNav.jsx
**Added Pop Quiz Button:**
- Fourth toggle button after "Board QA"
- Label: "Pop Quiz"
- viewMode value: `'pop-quiz'`
- Same styling as other toggle buttons (green color scheme)

### 2. TopicView.jsx

**Updated Data Loading:**
- Added `'pop-quiz'` to the condition for loading Q&A data
- Now loads qa.json when viewMode is 'book-qa', 'board-qa', OR 'pop-quiz'

**Pop Quiz Logic in transformQAToTopics:**

1. **Filter for very-short questions:**
   ```javascript
   const veryShortQuestions = qaChapter.qa.filter(qa => qa.questionType === 'very-short');
   ```

2. **Random Selection:**
   ```javascript
   const shuffled = [...veryShortQuestions].sort(() => Math.random() - 0.5);
   const selectedQuestions = shuffled.slice(0, Math.min(5, shuffled.length));
   ```
   - Shuffles all very-short questions randomly
   - Takes up to 5 questions (or all if less than 5)

3. **Display Structure:**
   ```
   📝 Pop Quiz (Topic level)
     ├─ Q1: "question preview..." (reference)
     ├─ Answer
     ├─ Q2: "question preview..." (reference)
     ├─ Answer
     ├─ Q3: "question preview..." (reference)
     ├─ Answer
     ├─ Q4: "question preview..." (reference)
     ├─ Answer
     ├─ Q5: "question preview..." (reference)
     └─ Answer
   ```

4. **Question Preview:**
   - Same truncation logic as Book QA and Board QA
   - Truncates at first space after 20 characters
   - Shows reference in parentheses if available
   - Format: `Q1: "question text..." (Ex 1.1)`

## Features

### Random Selection
- Each time you switch to Pop Quiz mode, different questions may appear
- Uses `Math.random()` for shuffling
- Ensures variety in practice

### Smart Filtering
- Only shows `questionType: "very-short"` questions
- Ignores exerciseType (shows book, board, and extra questions)
- Automatically handles chapters with fewer than 5 very-short questions

### Consistent UI
- Uses same Q/Answer structure as Book QA and Board QA
- Maintains exclusive expansion behavior
- Same content rendering (supports all content types)

## User Flow

1. Select a subject
2. Select a chapter
3. Click **"Pop Quiz"** button
4. See "Pop Quiz" topic with 5 random very-short questions
5. Click Q1 to see the question
6. Click Answer to see the answer
7. Continue through Q2, Q3, Q4, Q5

## Edge Cases Handled

1. **No very-short questions:** Returns empty Pop Quiz topic
2. **Fewer than 5 questions:** Shows all available questions
3. **Exactly 5 questions:** Shows all 5 questions
4. **More than 5 questions:** Randomly selects 5

## ID Generation

Unique IDs for Pop Quiz mode:
- Topic: `topic-pop-quiz`
- Question: `pop-quiz-qa-{index}-q` (e.g., "pop-quiz-qa-0-q")
- Answer: `pop-quiz-qa-{index}-answer` (e.g., "pop-quiz-qa-0-answer")

## Future Enhancements

Possible improvements:
- **Configurable count:** Allow user to choose number of questions (5, 10, 15)
- **Question type mix:** Include short questions as well
- **Difficulty filter:** Filter by difficulty level
- **Score tracking:** Track which questions were answered correctly
- **Timer:** Add a countdown timer for timed quizzes
- **Shuffle on refresh:** Add a "Shuffle" button to get new questions
- **Save progress:** Remember which questions were already shown

## Testing Checklist

- [x] Pop Quiz button appears in navigation
- [x] Loads qa.json when clicked
- [x] Filters for very-short questions only
- [x] Randomly selects up to 5 questions
- [x] Shows all questions if fewer than 5
- [x] Displays questions with proper formatting
- [x] Shows reference if available
- [x] Answer nodes work correctly
- [x] Exclusive expansion behavior maintained
- [x] Content renders correctly
