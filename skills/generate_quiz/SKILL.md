---
name: generate_quiz
command: /quiz
version: 1.0.0
description: Generates diagnostic multiple-choice or short-answer assessment questions testing applied understanding and returns a validated JSON structure for grading.
---

# Generate Assessment

## Inputs
- `topic`: Topic to assess.
- `difficulty`: Difficulty level (`beginner`, `intermediate`, `advanced`).
- `question_count`: Number of questions (default 3 to 5).
- `document_context`: Excerpts from uploaded study materials.

## Instructions
1. Focus on applied understanding and scenario-based thinking rather than trivial trivia.
2. If `document_context` is provided, prioritize questions that assess concepts directly covered in the material.
3. For multiple-choice questions, provide 4 options (A, B, C, D) with plausible distractors that diagnose common misunderstandings.
4. Provide a clear explanation for why the correct option is right and why distractors are wrong.
5. Return the result STRICTLY as a JSON object matching the output schema. Do NOT enclose in markdown conversational fluff outside the JSON block.

## Output Schema (JSON)
```json
{
  "topic": "string",
  "difficulty": "beginner | intermediate | advanced",
  "total_questions": 3,
  "questions": [
    {
      "id": 1,
      "question": "string",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_option": "A",
      "explanation": "string explaining why A is correct and why other choices fail",
      "source_reference": "Optional file/page reference"
    }
  ]
}
```
