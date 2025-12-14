# Book QA Feature - Implementation Summary

## Overview
Implemented Book QA mode that displays questions and answers from qa.json in a hierarchical structure similar to the teaching content. Questions are grouped by questionType (Very Short, Short, Long, Very Long) and displayed with expandable Question/Answer nodes.

## Implementation Details

### Data Loading (TopicView.jsx)

**Conditional Data Loading:**
- When `viewMode === 'book-qa'`: Loads `/db/{standard}-{subject}/qa.json`
- When `viewMode === 'teaching'`: Loads `/db/{standard}-{subject}/concept.json`
- Reloads data whenever `viewMode`, `chapter`, `standard`, or `subject` changes

**Chapter Matching:**
- Finds the matching chapter in qa.json using `chapterNo` (converted to string for comparison)
- Validates that the chapter exists and has Q&A data
- Shows error message if no Q&A available

### Data Transformation

**transformQAToTopics() Function:**

Transforms flat Q&A array into hierarchical topic structure:

```
qa.json structure:
{
  "chapters": [
    {
      "chapterNo": "1",
      "qa": [
        { "questionType": "very-short", "question": [...], "answer": [...] },
        { "questionType": "short", "question": [...], "answer": [...] }
      ]
    }
  ]
}

Transformed to:
{
  "topics": [
    {
      "id": "topic-very-short",
      "title": "Very Short",
      "subTopics": [
        {
          "id": "very-short-qa-0",
          "title": "Q1",
          "subTopics": [
            { "id": "very-short-qa-0-question", "title": "Question", "content": [...] },
            { "id": "very-short-qa-0-answer", "title": "Answer", "content": [...] }
          ]
        },
        {
          "id": "very-short-qa-1",
          "title": "Q2",
          "subTopics": [...]
        }
      ]
    },
    {
      "id": "topic-short",
      "title": "Short",
      "subTopics": [...]
    }
  ]
}
```

### Hierarchical Structure

**Level 1 - Question Type (Topic):**
- Very Short
- Short
- Long
- Very Long
- Only shown if questions of that type exist

**Level 2 - Question Number (SubTopic):**
- Q1, Q2, Q3, etc.
- Numbered sequentially within each question type

**Level 3 - Question/Answer (SubTopic):**
- "Question" node - displays question content
- "Answer" node - displays answer content

### Exclusive Expansion Behavior

The existing expansion logic is reused:
- Clicking a node expands it and collapses all siblings
- Clicking an expanded node collapses it and all descendants
- Same behavior as teaching content for consistency

### Content Rendering

**Content Display:**
- Question and Answer content uses the same Content schema as teaching content
- Supports all content types: body, bullets, equations, images, etc.
- Rendered using the existing ContentView component

**Example Q&A Display:**
```
📘 Very Short                    (Level 1 - Topic)
  └─ Q1                          (Level 2 - SubTopic)
      ├─ Question                (Level 3 - SubTopic)
      │   └─ [Question content]  (Content items)
      └─ Answer                  (Level 3 - SubTopic)
          └─ [Answer content]    (Content items)
```

### Error Handling

**Error States:**
1. **Q&A file not found**: "Q&A data not available for this chapter"
2. **Chapter not found in qa.json**: "No Q&A available for this chapter"
3. **No qa array**: "No Q&A available for this chapter"

**Error Display:**
- Shows error message in topics-view
- Displays BottomNav for navigation
- User can switch back to Teaching mode or navigate away

### User Flow

1. **Select Subject** → Teaching mode by default
2. **Click "Book QA" button** → Switches to Book QA mode
3. **Select Chapter** → Loads qa.json for that chapter
4. **View Question Types** → Shows available types (Very Short, Short, etc.)
5. **Click Question Type** → Expands to show Q1, Q2, Q3...
6. **Click Q1** → Expands to show Question and Answer nodes
7. **Click Question** → Displays question content
8. **Click Answer** → Collapses Question, displays answer content

### Data Grouping Logic

Questions are grouped by `questionType` field:
- `"very-short"` → "Very Short"
- `"short"` → "Short"
- `"long"` → "Long"
- `"very-long"` → "Very Long"

Only question types with at least one question are displayed.

### ID Generation

Unique IDs are generated for each node:
- Topic: `topic-{questionType}` (e.g., "topic-very-short")
- Q Number: `{questionType}-qa-{index}` (e.g., "very-short-qa-0")
- Question: `{questionType}-qa-{index}-question`
- Answer: `{questionType}-qa-{index}-answer`

This ensures no ID conflicts and maintains hierarchy.

## Future Enhancements

The structure is ready for:
- **Board QA mode**: Filter by `exerciseType === "board"`
- **Exercise filtering**: Filter by `reference` field
- **Difficulty indicators**: Show difficulty level badges
- **MCQ support**: Special rendering for questions with `mcqAnswer`
- **Search**: Search within questions and answers

## Testing Checklist

- [x] Loads qa.json when Book QA button is clicked
- [x] Groups questions by questionType
- [x] Shows only available question types
- [x] Displays Q1, Q2, Q3... for each type
- [x] Shows Question and Answer as expandable nodes
- [x] Maintains exclusive expansion behavior
- [x] Renders question/answer content correctly
- [x] Handles missing qa.json gracefully
- [x] Handles chapters with no Q&A
- [x] Switches back to teaching mode correctly
