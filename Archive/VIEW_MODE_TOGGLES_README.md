# View Mode Toggle Buttons - Implementation Summary

## Overview
Added three vertical toggle buttons (Teaching, Book QA, Board QA) to the right side of the bottom navigation panel. These buttons are mutually exclusive, with "Teaching" selected by default. The buttons are displayed in both Chapter and Topic views after a subject is selected.

## Changes Made

### 1. App.jsx
**Added State Management:**
- Added `viewMode` state with default value `'teaching'`
- Three possible values: `'teaching'`, `'book-qa'`, `'board-qa'`
- Resets to `'teaching'` when:
  - User selects a new subject
  - User navigates back to subjects view

**Props Passed to Child Components:**
- `viewMode`: Current selected view mode
- `onViewModeChange`: Function to update view mode
- Passed to both `ChapterView` and `TopicView`

### 2. BottomNav.jsx
**Added Toggle Buttons:**
- Three vertical buttons stacked on the right side
- Button labels: "Teaching", "Book QA", "Board QA"
- Conditional rendering: Only shown when `viewMode` and `onViewModeChange` props are provided
- Active state styling for selected button

**Props Added:**
- `viewMode`: Current selected mode
- `onViewModeChange`: Callback to change mode

### 3. BottomNav.css
**Added Styles:**
- `.view-mode-toggles`: Container for toggle buttons
  - Vertical flex layout (`flex-direction: column`)
  - Positioned on right side with `margin-left: auto`
  - Responsive gap between buttons

- `.toggle-btn`: Individual toggle button styles
  - Semi-transparent blue background when inactive
  - Solid blue background when active
  - Smooth transitions and hover effects
  - Responsive sizing with `clamp()`
  - Minimum width for consistency

**Updated Existing Styles:**
- `.bottom-nav`: Added `justify-content: space-between` to position breadcrumbs on left and toggles on right

### 4. ChapterView.jsx
**Props Updated:**
- Added `viewMode` and `onViewModeChange` to component props
- Passed both props to `BottomNav` component

### 5. TopicView.jsx
**Props Updated:**
- Added `viewMode` and `onViewModeChange` to component props
- Passed both props to `BottomNav` component

## Visual Design

### Toggle Button States

**Inactive State:**
- Background: `rgba(59, 130, 246, 0.2)` (semi-transparent blue)
- Text Color: `#93c5fd` (light blue)
- Border: `1px solid rgba(59, 130, 246, 0.3)`

**Active State:**
- Background: `#3b82f6` (solid blue)
- Text Color: `white`
- Border: `#3b82f6` (solid blue)
- Box Shadow: `0 2px 8px rgba(59, 130, 246, 0.4)`

**Hover Effects:**
- Inactive: Slightly darker background, subtle left slide
- Active: Darker blue background
- All: Scale down on click for tactile feedback

### Layout
```
┌─────────────────────────────────────────────────────────┐
│ Bottom Navigation                                       │
├─────────────────────────────────────────────────────────┤
│ [Home] [6. Science] [1. Chapter]        [Teaching]     │
│                                          [Book QA]      │
│                                          [Board QA]     │
└─────────────────────────────────────────────────────────┘
```

## Responsive Design
- All button sizes use `clamp()` for fluid scaling
- Minimum width: 80px
- Maximum width: 100px
- Font size: 0.75rem to 0.875rem
- Padding and gaps scale with viewport

## User Experience
1. **Default Behavior**: "Teaching" is selected when user first selects a subject
2. **Mutual Exclusivity**: Only one button can be active at a time
3. **Persistence**: Selection persists when navigating between chapters and topics
4. **Reset**: Selection resets to "Teaching" when returning to subject selection
5. **Visual Feedback**: Clear active state with color change and shadow
6. **Smooth Transitions**: All state changes are animated

## Future Integration
The `viewMode` state is now available in both `ChapterView` and `TopicView` components, ready to be used for:
- Loading different data sources (concept.json vs qa.json)
- Filtering Q&A by exercise type (book vs board)
- Switching between teaching content and Q&A displays
