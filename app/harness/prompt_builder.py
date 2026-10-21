from typing import List, Dict, Any, Optional

class PromptBuilder:
    """Constructs pedagogical prompt payloads for BYO-AI models."""

    BASE_SYSTEM_PROMPT = """You are SkillBridge AI, an expert technical mentor and pedagogical assistant.
Your goal is to bridge the learner's skill gaps through intuitive mental models, active recall, grounded citations, and concrete practice.
Always maintain clarity, encouragement, and strict adherence to provided document evidence.
Never fabricate source references or citations.
"""

    def build_system_instruction(
        self,
        skill_instructions: Optional[str] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> str:
        parts = [self.BASE_SYSTEM_PROMPT]

        if user_profile:
            profile_context = []
            if user_profile.get("target_skill_goal"):
                profile_context.append(f"- Target Goal: {user_profile['target_skill_goal']}")
            if user_profile.get("learning_style"):
                profile_context.append(f"- Preferred Learning Style: {user_profile['learning_style']}")
            if profile_context:
                parts.append("### Learner Profile:\n" + "\n".join(profile_context))

        if skill_instructions:
            parts.append("### Active Skill Workflow & Instructions:\n" + skill_instructions)

        return "\n\n".join(parts)

    def build_user_prompt(
        self,
        user_input: str,
        document_excerpts: Optional[List[Dict[str, Any]]] = None,
        parsed_params: Optional[Dict[str, Any]] = None,
    ) -> str:
        prompt_parts = []

        # Add document context if available
        if document_excerpts and len(document_excerpts) > 0:
            prompt_parts.append("### Retrieved Document Context (Grounded Evidence):")
            for i, chunk in enumerate(document_excerpts, 1):
                filename = chunk.get("filename", "Uploaded File")
                page = chunk.get("page_number", "Unknown")
                text = chunk.get("content", "").strip()
                prompt_parts.append(f"[{i}] File: {filename} | Page: {page}\nExcerpt: \"\"\"{text}\"\"\"\n")
            prompt_parts.append("Instructions: Ground your response strictly on the evidence above where applicable. Cite the exact file and page number.")

        if parsed_params:
            param_lines = [f"- {k}: {v}" for k, v in parsed_params.items() if k != "raw_args"]
            if param_lines:
                prompt_parts.append("### Extracted Parameters:\n" + "\n".join(param_lines))

        prompt_parts.append(f"### Learner Request:\n{user_input}")

        return "\n\n".join(prompt_parts)

prompt_builder = PromptBuilder()

