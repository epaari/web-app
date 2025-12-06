# Version 5.0.0
User Flow:
User sees the Chapters screen listing both chapters (1. Measurements and 3. Matter Around Us)
Bottom navigation shows "6. Science"
When user clicks a chapter, they navigate to ChapterView
ChapterView displays the nodes and content for that specific chapter
Bottom navigation updates to show the full breadcrumb trail

# Version 2.0.0
## Make Chapter View Responsive
Implement responsive typography and sizing for Chapter Title, Node Titles, Node Icons, Content Text, and Images using CSS clamp() function for fluid scaling.

Current Fixed Sizes
Element	Current Size
Chapter Title	4rem
Node Title 1	4rem
Node Title 2	3.5rem
Node Title 3	3rem
Expand Icon 1	3rem
Expand Icon 2	2.5rem
Expand Icon 3	2rem
Content Bullet	3rem
Equation	2.5rem
Info Popover	2rem
Image Width	25%
Depth Indentation	4rem - 4.5rem

## Proposed Changes
ChapterView.css
Use CSS clamp(min, preferred, max) for fluid responsive sizing:

min: Smallest readable size (for mobile ~320px)
preferred: Viewport-relative size using vw
max: Maximum size (current desktop value)
Changes:
Element	New Responsive Value	Explanation
Chapter Title	clamp(1.5rem, 4vw, 4rem)	Scales from 1.5rem to 4rem
Node Title 1	clamp(1.5rem, 4vw, 4rem)	Scales from 1.5rem to 4rem
Node Title 2	clamp(1.25rem, 3.5vw, 3.5rem)	Scales from 1.25rem to 3.5rem
Node Title 3	clamp(1rem, 3vw, 3rem)	Scales from 1rem to 3rem
Expand Icon 1	clamp(1.25rem, 3vw, 3rem)	Scales proportionally
Expand Icon 2	clamp(1rem, 2.5vw, 2.5rem)	Scales proportionally
Expand Icon 3	clamp(0.875rem, 2vw, 2rem)	Scales proportionally
Icon Width	clamp(1.5rem, 4vw, 4rem)	Scales with content
Content Bullet	clamp(1rem, 3vw, 3rem)	Scales from 1rem to 3rem
Equation	clamp(1rem, 2.5vw, 2.5rem)	Scales from 1rem to 2.5rem
Info Popover	clamp(0.875rem, 2vw, 2rem)	Scales from 0.875rem to 2rem
Node Gap	clamp(0.5rem, 2vw, 2rem)	Responsive gap
Depth 1 Margin	clamp(1rem, 4.5vw, 4.5rem)	Responsive indent
Depth 2/3 Margin	clamp(0.75rem, 4vw, 4rem)	Responsive indent
Image Width	clamp(120px, 25%, 300px)	Min 120px, max 300px

## Verification Plan
Since this is purely visual CSS styling, the user will verify by:

Desktop View: Open the app in a full-width browser window and confirm all elements display at their maximum sizes
Resize Test: Slowly resize the browser window from wide to narrow and observe smooth, proportional scaling of all text elements
Mobile View: Use browser DevTools (F12 → Device Toolbar) to test on mobile viewport sizes (e.g., 375px width) and verify text remains readable but smaller
Tablet View: Test at ~768px width to see mid-range scaling
