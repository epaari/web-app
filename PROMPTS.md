# Version 5.0.0
So far we were displaying only one chapter.
Now add a new screen "Chapters" before ChapterView.
List the 2 chapters from db.json.
The bottom navigation panel should show class and subject (example: "6. Science")
When the user selects a chapter, show the Nodes and Contents in ChapterView.

# Version 4.0.0
You are an expert python programmer.
I have a microsoft word file.
Write a python program to get the file name in the command line, extract the text and convert to JSON schema as follows:

JSON SCHEMA:
{
  "chapterNo": "string",
  "chapterTitle": "string",
  "nodes": [ Node ] ,
}

Node = {
  "id": "string", 			// 3 digits random number followed by label
  "nodeType": "title1|title2|title3",	// type of clickable node
  "label": "string", 			// what to display (title)
  "children"?: [ Node ], 		// clickable node that expands to show children
  "content"?: [ ContentItem ]		// leaf content shown when node clicked
}

ContentItem = {
  "type": "bullet1|bullet2|number1|number2|image|video",	// depending on type:
  "text"?: "string",                 				// for bullet1/bullet2/number1/number2
  "url"?: "string",                  				// for image/video
}

JSON DATA:
- "chapterNo" = 1
- "chapterTitle" = Measurements
- Paragraphs with "# Sub Topic - 1" style, add as a Node. Where "id" is a 3 digits random number followed by the paragraph text and nodeType = "title1".
- Paragraphs with "# Sub Topic - 2" style, add as a Node. Where "id" is a 3 digits random number followed by the paragraph text and nodeType = "title2".
- Paragraphs with "# Bullet-1" style, add as a ContentItem. Where type = bullet1. text = paragraph text. If a word is formatted as bold, add **word** markdown.
- Paragraphs with "# Bullet-2" style, add as a ContentItem. Where type = bullet2. text = paragraph text. If a word is formatted as bold, add **word** markdown.

Save the file as db-<file-name>.json

# Version 3.0.0
Create a static navigation panel at the bottom.
Display "./src/assets/home_icon.png" on the left of this panel.
Display "Class 10" button using the "./db/db.json" "class".
Display "Science" button using the "./db/db.json" "subject".
Display "3. Matter Around Us" button using the "./db/db.json" "chapterNo" and "chapterTitle".

I have attached a sample UI mock-up.
Prepare the implementation plan. I will review it before you proceed.

# Version 2.0.0
Responsive Typography
Please make the Chapter Title, Node Titles, Node Icons, Content Text, Image responsive. i.e. reduce the sizes proportionately with respect to the display size.
Prepare the implementation plan. I will review it before you proceed.

# Version 1.7.0
I would like to display maths equations to the user.
Add a sample LaTeX equation to db.json.
Render this equation to the user.

Done! LaTeX equation rendering is now set up. Here's what was added:
### Changes made:
index.html: Added MathJax CDN script with LaTeX configuration
db.json: Added sample equation E = mc^2 in "What is Matter?" section
TreeNode.jsx: Added equation type rendering and MathJax typesetting trigger
ChapterView.css: Added .content-equation styling

# Version 1.6.0
The image is currently displayed as thumbnail.
Remove thumbnail and display directly.
Position the image to the right.
Image width = 25% of the screen width.
Wrap text around the image.

# Version 1.5.0
@db.json Add some React markdowns to the following element:
{
  "type": "bullet1",
  "text": "Matter is everything around us—air, water, and the materials we use. It is anything that occupies space and has mass."
}

parseMarkdown() returns "strong" for bold text.
Please change the color of the text too.
---
I want to show additional information to some words in the content.
When the user clicks on those words, it should show extra information in a non-modal.
When the user clicks anywhere, the modal should close.

## Feature Behavior
Clickable words appear in purple with dashed underline
Click opens a modal with the word as header and info as content
Click anywhere outside the modal to close it
Press Escape to close the modal
Fully keyboard accessible (Tab + Enter)
---
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