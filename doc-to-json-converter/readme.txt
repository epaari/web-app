What this script does:
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

python doc_to_json.py 6 science 10.docx

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