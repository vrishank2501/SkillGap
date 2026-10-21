import re
from typing import Optional, Dict, Any, Tuple
from app.harness.skill_loader import skill_loader, SkillDefinition

class ParsedCommand:
    def __init__(
        self,
        is_command: bool,
        command: Optional[str] = None,
        skill: Optional[SkillDefinition] = None,
        raw_args: str = "",
        parsed_params: Optional[Dict[str, Any]] = None,
        original_text: str = ""
    ):
        self.is_command = is_command
        self.command = command
        self.skill = skill
        self.raw_args = raw_args
        self.parsed_params = parsed_params or {}
        self.original_text = original_text

    def __repr__(self):
        return f"<ParsedCommand is_cmd={self.is_command} cmd={self.command} params={self.parsed_params}>"

class CommandRouter:
    """Parses user input into recognized slash commands and structured parameters."""

    COMMAND_PATTERN = re.compile(r"^/([a-zA-Z0-9_-]+)(?:\s+(.*))?$", re.DOTALL)

    def parse(self, user_text: str) -> ParsedCommand:
        text = user_text.strip()
        match = self.COMMAND_PATTERN.match(text)
        if not match:
            # Regular natural language query, route to default explain or grounded answer
            return ParsedCommand(
                is_command=False,
                raw_args=text,
                original_text=text
            )

        cmd_name = match.group(1).lower()
        full_cmd = f"/{cmd_name}"
        raw_args = (match.group(2) or "").strip()
        skill = skill_loader.get_skill_by_command(full_cmd)

        parsed_params = self._extract_params(full_cmd, raw_args)

        return ParsedCommand(
            is_command=True,
            command=full_cmd,
            skill=skill,
            raw_args=raw_args,
            parsed_params=parsed_params,
            original_text=text
        )

    def _extract_params(self, cmd: str, args: str) -> Dict[str, Any]:
        params = {"raw_args": args}
        if not args:
            return params

        # /quiz [topic] [beginner|intermediate|advanced] [count]
        if cmd == "/quiz":
            # Check for count (e.g. 3 questions, 5, etc.)
            count_match = re.search(r"\b(\d+)\s*(?:questions?)?\b", args, re.IGNORECASE)
            if count_match:
                params["question_count"] = int(count_match.group(1))
                args = re.sub(r"\b\d+\s*(?:questions?)?\b", "", args, flags=re.IGNORECASE).strip()
            else:
                params["question_count"] = 3

            # Check for difficulty
            diff_match = re.search(r"\b(beginner|intermediate|advanced)\b", args, re.IGNORECASE)
            if diff_match:
                params["difficulty"] = diff_match.group(1).lower()
                args = re.sub(r"\b(beginner|intermediate|advanced)\b", "", args, flags=re.IGNORECASE).strip()
            else:
                params["difficulty"] = "intermediate"

            params["topic"] = args.strip() or "general concepts"

        # /explain [topic] [beginner|intermediate|advanced]
        elif cmd == "/explain":
            diff_match = re.search(r"\b(beginner|intermediate|advanced)\b", args, re.IGNORECASE)
            if diff_match:
                params["difficulty"] = diff_match.group(1).lower()
                args = re.sub(r"\b(beginner|intermediate|advanced)\b", "", args, flags=re.IGNORECASE).strip()
            else:
                params["difficulty"] = "beginner"
            params["topic"] = args.strip() or "the concept"

        # /answer [query]
        elif cmd == "/answer":
            params["query"] = args

        # /summarize [focus]
        elif cmd == "/summarize":
            params["focus_area"] = args if args else "all key topics"

        return params

command_router = CommandRouter()

