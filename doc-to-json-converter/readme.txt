=====================
HOW THE SCRIPT WORKS?
=====================
1. Convert Chapter level word document to json.
2. Updates db/<standard>/<subject>.json file.
3. Uploads the images to content-images repository.
4. Pushes the files to content-images repository.
5. The input-file should be in the same folder as the script.
6. The input file name should be in the format <chapter>.docx
7. Do not include topic numbers in the input file name.

Command Line Usage:
python doc_to_json.py <standard> <subject> <input-file>

Example:
cd doc-to-json-converter
python doc_to_json.py 6 science 10.docx

===========
ACTION PLAN
===========
1. Question and answer extraction.
2. Equation extraction.
3. Full subject extraction.


==========================================
Git Commands for content-images Repository
No need to use these commands.
The script commits automatically.
==========================================
cd ../content-images
git status
git add .
git commit -m "Add images from document conversion"
git push


Please modify the "./doc-to-json-converter/word_to_json.py".
In process_word_document(), in addition to bullet1 and bullet2 add images also as follows:
1. Save the image to "./doc-to-json-converter/images"
2. Name the image as follows:
	- Use "label"	
	- Replace spaces by "-"
	- Remove ".", "?" or any other special characters.
3. Add the image as "content" as per the schema defined by "./db/json-schema.txt"
4. "url" format is "https://raw.githubusercontent.com/epaari/ezeescore_ai/main/<image-file-name>"

========================
CLAUD SONNET 4.5 PROMPTS
========================
I ran the script, it didn't extract any images from "./doc-to-json-converter/1.1.docx" document file.
I checked the images folder "./doc-to-json-converter/images". No images are present.
I checked the "./doc-to-json-converter/db-1.1.json" No image records are added.
Please fix this issue.

=============================
Avoiding-Errors-0.png (99.6 KB)
Avoiding-Errors-1.png (39.2 KB)
Avoiding-Errors-2.png (38.8 KB)
Tools-for-Measurement-3.png (66.5 KB)
Tools-for-Measurement-4.png (81.9 KB)
Tools-for-Measurement-5.png (121.6 KB)
Tools-for-Measurement-6.png (75.2 KB)
Tools-for-Measurement-7.png (38.2 KB)

While naming multiple images in a single node, follow the below guidelines:
1. Start the index at "1". Example: Instead of Avoiding-Errors-0.png, use Avoiding-Errors-1.png
2. After moving to the next Node, reset the index. Example: Instead of Tools-for-Measurement-3.png use Tools-for-Measurement-1.png

===============================
Amazing!. You are really helpful. Thanks!

===============================
In main(), we have "print(f"Successfully converted '{input_file}'")".
I don't want to print the input_file's path (example: ./1.1.docx).
I want to print only the file name without the extension. (example: 1.1).
Please modify the script.

===============================
In the output json file, I don't need
1. Opening brace at the start of the document
2. Closing brace at the end of the document
3. First level indent throughout the document.
Please change the script.

================================
The current behaviour is to extract the nodes and write the json data to the file "./output/db-<chapter>.json".
Instead I want you to extract the nodes and write the json data directly to the "../db/<standard>-<subject>-db.json" file.
Please modify the script as follows:
1. Get the standard and subject from the command line. (example: python doc_to_json.py 6 science 10.docx)
2. Locate the chapter in the "../db/<standard>-<subject>-db.json" file. The chapter number is the input file name without the extension. (example: 10.docx -> 10).
3. The location of the chapter in the "../db/<standard>-<subject>-db.json" file is found by looking at the "chapterNo" key.
4. Add the json data under the "nodes" key.
5. If already nodes exist, remove the nodes and add the new nodes.

================================
After updating the "../db/<standard>-<subject>-db.json" file, I want to upload the image files in "./doc-to-json-converter/output" to GitHub's public repository "https://github.com/epaari/images".
Get the user consent before uploading the image files to GitHub.

Please modify the script.

================================
After successful commit, delete the image files in "./doc-to-json-converter/output" folder.
Please modify the script.

================================
