---
name: answer_question
command: /answer
version: 1.0.0
description: Answers domain-specific queries strictly grounded in uploaded source documents with exact file and page citations, and flags insufficient evidence.
---

# Answer from Learning Material

## Inputs
- `query`: The user's question.
- `document_context`: Retrieved document chunks containing text, filename, and page numbers.

## Instructions
1. Rely strictly on the evidence contained in `document_context`.
2. Cite the exact file name and page number for every factual claim (e.g., `[Handbook.pdf, Page 12]`).
3. If the retrieved material does NOT contain sufficient evidence to answer the question, clearly state:
   *"The uploaded materials do not contain sufficient information to answer this question."*
   Then offer a concise general explanation explicitly flagged as general knowledge rather than material fact.
4. Never hallucinate document titles, chapter names, or page numbers.

## Output Format
- Direct, clear answer synthesizing the evidence.
- `### 📖 Evidence & Citations`: List the cited passages with `[Filename, Page X]`.
- If evidence is missing or partial, include a callout banner `> [!NOTE] Insufficient Document Evidence`.
