import pytest
from app.harness.skill_loader import skill_loader
from app.harness.command_router import command_router
from app.harness.prompt_builder import prompt_builder

def test_skill_loader():
    skills = skill_loader.list_skills()
    assert len(skills) >= 6
    assert "explain_concept" in skills
    assert "generate_quiz" in skills
    assert "answer_question" in skills

    explain_skill = skill_loader.get_skill_by_command("/explain")
    assert explain_skill is not None
    assert explain_skill.name == "explain_concept"

def test_command_router():
    cmd1 = command_router.parse("/quiz Python loops intermediate 5")
    assert cmd1.is_command is True
    assert cmd1.command == "/quiz"
    assert cmd1.parsed_params["question_count"] == 5
    assert cmd1.parsed_params["difficulty"] == "intermediate"
    assert "loops" in cmd1.parsed_params["topic"]

    cmd2 = command_router.parse("/explain binary search beginner")
    assert cmd2.is_command is True
    assert cmd2.command == "/explain"
    assert cmd2.parsed_params["difficulty"] == "beginner"
    assert "binary search" in cmd2.parsed_params["topic"]

    cmd3 = command_router.parse("What is polymorphism?")
    assert cmd3.is_command is False
    assert cmd3.raw_args == "What is polymorphism?"

def test_prompt_builder():
    instruction = prompt_builder.build_system_instruction(
        skill_instructions="Test instructions",
        user_profile={"target_skill_goal": "Full Stack Dev"}
    )
    assert "SkillBridge AI" in instruction
    assert "Full Stack Dev" in instruction

    prompt = prompt_builder.build_user_prompt(
        user_input="Explain recursion",
        document_excerpts=[{"filename": "code.pdf", "page_number": 3, "content": "Recursion calls itself."}]
    )
    assert "code.pdf" in prompt
    assert "Recursion calls itself" in prompt

