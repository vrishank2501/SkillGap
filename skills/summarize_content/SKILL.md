---
name: summarize_content
command: /summarize
version: 1.0.0
description: Produces high-yield, structured revision notes, key concepts, terminology, and study questions from uploaded materials.
---

# Summarize Learning Content

## Inputs
- `document_context`: Full text or sampled passages from the user's uploaded document.
- `focus_area`: Optional topic or theme to focus the summary on.

## Instructions
1. Extract the core themes, architectural patterns, or key theoretical principles.
2. Formulate clear, concise definitions for critical terms and vocabulary.
3. Highlight high-yield points that frequently appear on exams or technical assessments.
4. Provide 3 diagnostic self-check questions at the end to reinforce active recall.

## Output Format
- `## 📋 High-Yield Summary`
- `### 🎯 Core Objectives & Themes`
- `### 🔑 Key Concepts & Definitions` (Bullet points or table)
- `### 💡 Crucial Takeaways`
- `### ❓ Self-Check Questions`
