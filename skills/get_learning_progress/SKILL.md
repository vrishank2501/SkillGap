---
name: get_learning_progress
command: /progress
version: 1.0.0
description: Summarizes completed topics, quiz performance history, and active study days from the Supabase database.
---

# Report Learning Progress

## Inputs
- `progress_data`: JSON payload fetched directly from Supabase (`user_progress` and `quiz_attempts` tables) containing:
  - `total_topics_studied`: integer
  - `completed_topics`: list of topic names
  - `quizzes_attempted`: integer
  - `average_score`: percentage
  - `recent_attempts`: list of `{ topic, score, total_questions, date }`
  - `active_streak_days`: integer

## Instructions
1. Present the student's metrics clearly and encouragingly.
2. Highlight areas of strength (topics with $\ge 80\%$ scores).
3. Identify topics that need revision or have scores below $70\%$.
4. Suggest a direct next action to sustain learning momentum.

## Output Format
- `## 📊 Your Learning Progress`
- Metric summary table or bullet list (Topics Studied, Quizzes Completed, Average Accuracy, Current Streak).
- `### 🌟 Strengths & Mastered Topics`
- `### 🎯 Focus & Improvement Areas`
- `### 🚀 Recommended Next Step`
