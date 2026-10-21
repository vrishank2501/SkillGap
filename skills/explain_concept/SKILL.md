---
name: explain_concept
command: /explain
version: 1.0.0
description: Explains a topic or concept tailored to the user's proficiency level with intuitive mental models, practical examples, common mistakes, and grounded document citations.
---

# Explain a Concept

## Inputs
- `topic`: The specific concept or subject to explain (e.g., "Python decorators", "Binary Search Trees").
- `difficulty`: Difficulty level (`beginner`, `intermediate`, `advanced`). Defaults to `beginner`.
- `document_context`: Relevant excerpts retrieved from the user's uploaded materials (if available).
- `learning_style`: Preferred explanation style (`practical`, `analogy-driven`, `academic`).

## Instructions
1. **Core Intuition / Mental Model**: Begin with a crisp 1-2 sentence real-world analogy or intuition. Avoid dense jargon at first.
2. **Step-by-Step Breakdown**: Explain the fundamental mechanics in clear, digestible stages.
3. **Practical Code / Concrete Example**: Provide a clean, minimal code block or walkthrough demonstrating how the concept works.
4. **Common Pitfalls & Misconceptions**: Detail 1-2 common bugs, mistakes, or misconceptions beginners run into.
5. **Key Takeaway Recap**: Conclude with a concise 2-3 bullet summary.
6. **Strict Source Attribution**: If `document_context` was provided, explicitly ground the explanation in those excerpts and cite the file and page number. Never invent facts.

## Output Format
Return clean GitHub-flavored markdown with the following sections:
- `### 💡 Core Intuition`
- `### 🔍 How It Works`
- `### 💻 Practical Example`
- `### ⚠️ Common Pitfalls`
- `### 📌 Recap`
- `### 📚 Sources` (only when retrieved excerpts were provided)
