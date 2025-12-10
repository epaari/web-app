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
python migration.py <standard> <subject> <input-file>

Example:
cd doc-to-json-converter
python migration.py 6 science 10.docx