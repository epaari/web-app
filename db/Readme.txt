========================
CLAUD SONNET 4.5 PROMPTS
========================

I want to add questions and answers to a new DB.
Following are my use cases:
1. Show questions and answers in an accordian style to user as follows:
  - very-short answer
    - Question-1
      - Answer
    - Question-2
      - Answer
  - short answer
    - Question-1
      - Answer
    - Question-2
      - Answer
  - long answer
    - Question-1
      - Answer
    - Question-2
      - Answer
  - very-long answer
    - Question-1
      - Answer
    - Question-2
      - Answer

2. Question paper generator
  - Display the questions in an accordian style, and allow user to select the questions.
  - Generate the question paper based on the selected questions.

3. Quiz
  - Show few randomly selected very-short answer questions and answers in an accordian style to user.
    - Question-1
      - Answer
    - Question-2
      - Answer
    - Question-3
      - Answer
    - Question-4
      - Answer
    - Question-5
      - Answer

The following is the DB schema I already use for the concepts module. This DB is used to display the chapter content to the user.
{
  "chapterNo": "string",
  "chapterTitle": "string",
  "nodes": [ Node ]
}

Node = {
  "id": "string", // 3 digits random number followed by sterilised label
  "nodeType": "title1|title2|title3", // type of clickable node
  "label": "string", // what to display (title)
  "children"?: [ Node ], // clickable node that expands to show children
  "content"?: [ ContentItem ] // leaf content shown when node clicked
}

ContentItem = {
  "type": "bullet1|bullet2|number1|number2|image|video", // depending on type:
  "text"?: "string", // for bullet1/bullet2/number1/number2
  "url"?: "string", // for image/video
}

Please suggest a db schema for the questions and answers. The following are my requirements:
1. Question and its answer should be saved separately.
2. Each question should have the following meta data:
   - exercise-type: "book" | "board"
   - question-type: "very-short" | "short" | "long" | "very-long"
   - reference: string
   - mcq-answer: number
   - faq: "yes" | "no"

