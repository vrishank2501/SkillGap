import json
import logging
from typing import Optional, Dict, Any
from app.providers.base import BaseAIProvider

logger = logging.getLogger(__name__)

class DemoProvider(BaseAIProvider):
    """
    SkillBridge Built-in Demo Provider.
    Requires ZERO API keys or credits.
    Generates high-yield structured learning responses, mental models, code snippets,
    and diagnostic quizzes matching the SKILL.md specifications.
    """

    def __init__(self, api_key: Optional[str] = "demo-key", default_model: Optional[str] = "skillbridge-demo"):
        super().__init__(api_key=api_key or "demo-key", default_model=default_model or "skillbridge-demo")

    async def validate_connection(self) -> Dict[str, Any]:
        return {
            "valid": True,
            "provider": "demo",
            "model": "skillbridge-demo",
            "latency_ms": 12,
            "message": "Connected to SkillBridge Demo Mode (No API key required)"
        }

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        prompt_lower = prompt.lower()
        topic = "the requested topic"
        for line in prompt.split("\n"):
            if "topic:" in line.lower():
                topic = line.split(":", 1)[1].strip()
                break
            elif "learner request:" in line.lower():
                topic = line.split(":", 1)[1].strip()

        # Generate structured learning card matching SKILL.md
        return (
            f"### 💡 Core Intuition & Mental Model\n"
            f"Think of **{topic}** like an efficient orchestrator in a complex system. "
            f"Instead of doing everything simultaneously or getting blocked, it divides tasks into manageable, predictable units.\n\n"
            f"### 🔍 How It Works\n"
            f"1. **Initialization**: The system establishes the execution environment and binds references.\n"
            f"2. **Processing**: Operations execute predictably with isolation and state management.\n"
            f"3. **Resolution**: Outputs are evaluated, resources are cleaned up, and status is returned.\n\n"
            f"### 💻 Practical Example\n"
            f"```python\n"
            f"# Demonstration of {topic}\n"
            f"def execute_concept(data_input):\n"
            f"    \"\"\"Applies core principles cleanly with defensive error checks.\"\"\"\n"
            f"    if not data_input:\n"
            f"        raise ValueError('Invalid input provided')\n"
            f"    \n"
            f"    result = [item * 2 for item in data_input]\n"
            f"    return result\n\n"
            f"# Example call\n"
            f"output = execute_concept([10, 20, 30])\n"
            f"print('Processed output:', output)  # [20, 40, 60]\n"
            f"```\n\n"
            f"### ⚠️ Common Pitfalls\n"
            f"- **State Mutation**: Modifying shared references unexpectedly across callers.\n"
            f"- **Premature Optimization**: Adding complexity before profiling bottlenecks.\n\n"
            f"### 📌 Key Takeaways\n"
            f"- Keep abstractions simple and modular.\n"
            f"- Test edge cases early to prevent unexpected bugs.\n\n"
            f"*(Generated in SkillBridge Demo Mode)*"
        )

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        # Extract topic from prompt
        topic = "Core Fundamentals"
        if "on '" in prompt:
            try:
                topic = prompt.split("on '")[1].split("'")[0]
            except Exception:
                pass

        quiz_data = {
            "topic": topic,
            "difficulty": "intermediate",
            "total_questions": 3,
            "questions": [
                {
                    "id": 1,
                    "question": f"What is the primary architectural purpose of {topic}?",
                    "options": [
                        "A) To manage state and isolate complexity into predictable units",
                        "B) To compress binary files on disk",
                        "C) To bypass all database transactions",
                        "D) To replace network protocols completely"
                    ],
                    "correct_option": "A",
                    "explanation": f"A is correct because {topic} is designed to provide clean abstraction and predictable state management."
                },
                {
                    "id": 2,
                    "question": "Which of the following is considered a major pitfall when implementing this pattern?",
                    "options": [
                        "A) Writing automated unit tests",
                        "B) Uncontrolled mutation of shared references across threads",
                        "C) Using descriptive variable names",
                        "D) Returning explicit exit codes"
                    ],
                    "correct_option": "B",
                    "explanation": "Uncontrolled mutation leads to race conditions, silent corruption, and difficult-to-reproduce bugs."
                },
                {
                    "id": 3,
                    "question": "How should resource cleanup typically be handled?",
                    "options": [
                        "A) Leave handles open indefinitely",
                        "B) Through deterministic context managers or try...finally blocks",
                        "C) By terminating the entire operating system process",
                        "D) Relying exclusively on manual user intervention"
                    ],
                    "correct_option": "B",
                    "explanation": "Context managers and try...finally ensure resources (memory, file descriptors, sockets) are released even during exceptions."
                }
            ]
        }
        return json.dumps(quiz_data)

