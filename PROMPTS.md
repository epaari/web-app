## 1.1.0
Please fix the following issue. 
Currently I am able to open multiple nodes and all nodes are in expanded state and content are visible.
I want the following behaviour:
1. When a level1 node is opened, show the list of level2 labels. This is working now.
2. When I open level2 node, show the content. This is working now.
3. When I open another level2 node, collapse the first level2 node and show the content of second level2 node. This is NOT working now.
4. When I open a second level1 node, collapse first level1 node and show the list of level2 nodes under second level node. This is NOT working now.

Don't test yourself. I will do manual testing myself.

## 1.0.0
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