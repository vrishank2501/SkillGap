---
name: recommend_next_lesson
command: /recommend
version: 1.0.0
description: Delivers personalized learning recommendations based on Supabase database records (lowest quiz scores, unstudied topics, or upcoming goals).
---

# Recommend Next Lesson

## Inputs
- `weakest_topics`: Topics from `quiz_attempts` where the score was below 70%.
- `in_progress_topics`: Topics currently in `user_progress` with status `in_progress`.
- `target_goal`: Target skill or curriculum goal specified in user's profile.
- `available_documents`: List of uploaded document titles.

## Instructions
1. Prioritize remediation for topics where recent quiz performance was weak.
2. If no weak topics exist, recommend the next logical topic to study based on uploaded documents or target goal.
3. Provide actionable next steps: a suggested slash command (e.g., `/explain <topic>` or `/quiz <topic>`) that the user can immediately trigger.

## Output Format
- `## 🎯 Recommended Next Study Step`
- `### 🔍 Why This Topic?` (Explain reasoning based on past quiz score or learning sequence)
- `### 📚 Focus Objective`
- `### ⚡ Action to Take Now` (e.g., clickable or copyable `/explain <topic>` or `/quiz <topic>`)
