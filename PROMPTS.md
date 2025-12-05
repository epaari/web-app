# Version 1.3.0
.chapter-view {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
  min-height: 100vh;
}
The chapter view max-width is 900px. Please increase the width to fill the whole screen width.
Keep the padding as 1rem.
Change the min-height to 90vh.

There is a triangle before every node. When the node is expanded, the triangle is rotated 90 degrees.
Increase the size of the triangle to match the font size of the node.

# Version 1.2.1
The top of the screen is shown as follows:
1. "CHAPTER 3" in a rounded box (.chapter-number)
2. "Matter Around Us" in a large font (font-size: 2.5rem;) (.chapter-title)

Change it as follows:
"3. Matter Around Us"
font-size: 5rem;

# Version 1.2.0
Do not display the full images in the content. Display only the small image thumbnail.
When the user clicks on the thumbnail, display the full image in a modal.
When the user clicks on the modal, close the modal.

## Changes Made:
TreeNode.jsx:
Images now display as small thumbnails (120x90px)
Clicking a thumbnail opens a full-size modal
Clicking the modal closes it
Added keyboard accessibility (Enter/Space to open)
Added a 🔍 zoom icon that appears on hover

ChapterView.css:
Thumbnail styling with hover effects (scale + glow)
Full-screen modal overlay with fade-in animation
Modal image with zoom-in animation and responsive sizing

# Version 1.1.0
Please fix the following issue. 
Currently I am able to open multiple nodes and all nodes are in expanded state and content are visible.
I want the following behaviour:
1. When a level1 node is opened, show the list of level2 labels. This is working now.
2. When I open level2 node, show the content. This is working now.
3. When I open another level2 node, collapse the first level2 node and show the content of second level2 node. This is NOT working now.
4. When I open a second level1 node, collapse first level1 node and show the list of level2 nodes under second level node. This is NOT working now.

Don't test yourself. I will do manual testing myself.

# Version 1.0.0
I want you to write a React web app to display hierarchical content to the user.
- The JSON data is available in ./db/db.json file.
- Display "chapterNo" and "chapterTitle".
- Display "nodes" hierarchically.
- When the user clicks on a node expand and show its "label" and "content".
- When the user clicks on some other node, collapse the open node and expand the clicked node.
- Apply click-to-lazy-load behavior (with keyboard accessibility and loading="lazy" for images).


Chapter header displays "3. Matter Around Us"
All tree nodes render with proper indentation
Clicking a node expands it and shows content
Clicking another node collapses the first, expands the new one
Images load lazily (check Network tab)
Tab through nodes and press Enter/Space to toggle


I have checked. When I click on a sub node, it is collapsing the main node. This results in not showing the content in sub node.
The correct behaviour is as follows:
When a level2 node is clicked, it should not collapse the level1 node.
Please fix this issue. Do not test yourself. I will do manual testing myself.