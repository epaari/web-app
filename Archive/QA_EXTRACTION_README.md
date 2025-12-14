# Q&A Extraction Feature - Implementation Summary

## Overview
Added Q&A extraction functionality to the migration script to extract questions and answers from Word documents and build the `qa.json` database according to the schema defined in `database-schema.txt`.

## Changes Made to `migration.py`

### 1. New Function: `process_word_document_qa()`
**Location:** Lines 1041-1348

This function processes a Word document and extracts Q&A content to build the qa.json structure.

**Key Features:**
- Detects `<question>` and `<answer>` tags (style: "# Meta Data")
- Extracts metadata tags that appear after `<question>`:
  - `<book_exercise>` → exerciseType: "book"
  - `<additional_exercise>` or `<faq>` → exerciseType: "board"
  - `<type=1>` → questionType: "very-short"
  - `<type=2>` → questionType: "short"
  - `<type=3>` → questionType: "long"
  - `<type=4>` → questionType: "very-long"
  - `<exercise="string">` → reference: "string"
  - `<activity_quiz="string", answer="integer">` → mcqAnswer: integer

- Extracts question content (between `<question>` and `<answer>`)
- Extracts answer content (between `<answer>` and next `<question>` or end of document)
- Uses the same Content Schema as concepts (body, bullet1, bullet2, number1, number2, equations, images, etc.)
- Handles images with hash-based IDs (same as concepts)
- Supports all content types: body, bullets, numbering, highlights, equations, images

**State Management:**
- `processing_started`: Tracks if we've encountered the first `<question>` tag
- `in_question`: True when processing question content
- `in_answer`: True when processing answer content
- `finalize_qa()`: Helper function to complete current Q&A item and add to list

### 2. New Function: `process_single_file_qa()`
**Location:** Lines 1502-1575

Processes a single Word document and updates the qa.json database.

**Key Features:**
- Extracts chapter number from filename (e.g., "1.docx" → chapter 1)
- Calls `process_word_document_qa()` to get Q&A list
- Creates or updates chapter entry in qa.json
- Maintains chapter sorting by chapterNo
- Handles both new chapters and updates to existing chapters

**Note:** In qa.json, `chapterNo` is stored as a string (per schema), unlike concept.json where it's an integer.

### 3. New Function: `run_qa_exporter()`
**Location:** Lines 1739-1797

Interactive tool to run Q&A extraction on all .docx files in the input directory.

**Workflow:**
1. Prompts user for standard (e.g., "6")
2. Prompts user for subject (e.g., "science")
3. Finds all .docx files in `./input` directory
4. Gets subject ID from subjects.json
5. Creates/updates `db/{standard}-{subject}/qa.json`
6. Processes all files and reports success count

### 4. Updated Menu System
**Changes:**
- Added "3. Q&A Exporter" to menu display
- Updated main() to handle choice "3"
- Updated invalid choice message to "0 and 3"

## Database Schema Compliance

The implementation follows the qa.json schema exactly:

```json
Chapter = {
    "id": "string",
    "subjectId": "string",
    "chapterNo": "string",  // Note: string type
    "chapterName": "string",
    "qa": [ Qa ]
}

Qa = {
    "id": "string",
    "exerciseType": "book|board|extra",
    "questionType": "very-short|short|long|very-long",
    "reference": "string",
    "difficulty": "easy|medium|hard",
    "mcqAnswer"?: "integer",
    "question": [ Content ],
    "answer": [ Content ]
}
```

## Tag Processing Logic

The implementation follows the exact logic specified:

```
if <question> {
   if <book_exercise>
      "exerciseType": "book"
   else if <additional_exercise> and <faq>
      "exerciseType": "board"
   else
      "exerciseType": "extra"
   
   if <type=1>
      "questionType": "very-short"
   else if <type=2>
      "questionType": "short"
   else if <type=3>
      "questionType": "long"
   else if <type=4>
      "questionType": "very-long"
   
   if <exercise="string">
      "reference": "string"

   if <activity_quiz="string", answer="integer">
      "mcqAnswer"?: "integer"

   Extract the question using Content Schema.

else if <answer>
   Extract the answer using Content Schema.
```

## Usage Example

1. Place Word documents (1.docx, 2.docx, etc.) in `Tools/Migration/input/`
2. Run the migration script: `python migration.py`
3. Select option "3. Q&A Exporter"
4. Enter standard: "6"
5. Enter subject: "science"
6. Script will create/update `db/6-science/qa.json`

## Content Extraction

The Q&A extraction reuses all the existing content extraction functions:
- `extract_paragraph_content_in_order()` - Extracts text and equations in order
- `create_paragraph_wrapper()` - Creates paragraph wrappers for mixed content
- `extract_numbering_text()` - Extracts numbering labels
- Image extraction with hash-based IDs
- Full support for equations (OMML to LaTeX conversion)

## Default Values

When tags are not specified, the following defaults are used:
- `exerciseType`: "extra"
- `questionType`: "short"
- `difficulty`: "medium"
- `reference`: ""

## Error Handling

- Validates filename is numeric (chapter number)
- Handles missing tags gracefully with defaults
- Prints warnings for image extraction errors
- Full exception handling with traceback for debugging
- Skips files with invalid filenames
