import json
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Header
from app.core.config import settings
from app.core.supabase import get_supabase_client
from app.providers import get_provider
from app.harness.command_router import command_router
from app.harness.prompt_builder import prompt_builder
from app.documents.search import document_search
from app.progress.supabase_progress import supabase_progress

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str
    provider: Optional[str] = "gemini"
    api_key: Optional[str] = None
    model: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = "dev-user-01"

class ChatResponse(BaseModel):
    response: str
    command_used: Optional[str] = None
    skill_name: Optional[str] = None
    citations: List[Dict[str, Any]] = []
    structured_data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

@router.post("/", response_model=ChatResponse)
async def handle_chat(request: ChatRequest, x_user_id: Optional[str] = Header(None)):
    uid = x_user_id or request.user_id or "dev-user-01"
    provider_name = (request.provider or "gemini").lower()
    
    # 1. Resolve API key
    api_key = (request.api_key or "").strip()
    if api_key in ["••••••••••••••••", "AIzaSy...", "sk-..."]:
        api_key = ""

    if not api_key:
        if "gemini" in provider_name:
            api_key = settings.DEFAULT_GEMINI_API_KEY
        else:
            api_key = settings.DEFAULT_OPENAI_API_KEY

    # 2. Parse command via Command Router
    parsed = command_router.parse(request.message)
    cmd = parsed.command
    skill = parsed.skill

    # 3. Direct /progress command handler
    if cmd == "/progress":
        summary = await supabase_progress.get_user_progress_summary(uid)
        markdown_resp = (
            f"## 📊 Your Learning Progress\n\n"
            f"- **Topics Studied**: {summary['total_topics_studied']}\n"
            f"- **Completed Topics**: {', '.join(summary['completed_topics']) if summary['completed_topics'] else 'None yet'}\n"
            f"- **Quizzes Attempted**: {summary['quizzes_attempted']}\n"
            f"- **Average Accuracy**: {summary['average_score']}%\n"
            f"- **Active Study Streak**: 🔥 {summary['active_streak_days']} days\n\n"
            f"Keep up the momentum! Type `/quiz [topic]` or `/recommend` for your next challenge."
        )
        return ChatResponse(
            response=markdown_resp,
            command_used=cmd,
            skill_name="get_learning_progress",
            structured_data=summary,
            session_id=request.session_id,
        )

    # 4. Direct /recommend command handler
    if cmd == "/recommend":
        rec = await supabase_progress.get_recommendation(uid)
        markdown_resp = (
            f"## 🎯 Recommended Next Lesson\n\n"
            f"**Focus Topic:** `{rec['topic']}`\n\n"
            f"**Why this topic?** {rec['reason']}\n\n"
            f"**Recommended Action:** Run `{rec['suggested_command']}`"
        )
        return ChatResponse(
            response=markdown_resp,
            command_used=cmd,
            skill_name="recommend_next_lesson",
            structured_data=rec,
            session_id=request.session_id,
        )

    # If calling LLM is required, ensure API key is present (unless demo mode)
    if provider_name != "demo" and not api_key:
        raise HTTPException(
            status_code=400,
            detail=f"Please enter your {provider_name.upper()} API key in the top navigation bar to start chatting.",
        )

    try:
        ai_provider = get_provider(provider_name, api_key=api_key, model=request.model)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to initialize {provider_name.upper()} provider: {str(e)}")

    # 5. Handle /quiz command
    if cmd == "/quiz":
        topic = parsed.parsed_params.get("topic", "the subject")
        difficulty = parsed.parsed_params.get("difficulty", "intermediate")
        count = parsed.parsed_params.get("question_count", 3)

        # Retrieve relevant excerpts for grounded quiz questions
        excerpts = await document_search.search(query=topic, user_id=uid, top_k=3)
        system_instruction = prompt_builder.build_system_instruction(
            skill_instructions=skill.instructions if skill else None
        )
        quiz_prompt = (
            f"Generate a {difficulty} diagnostic quiz on '{topic}' with {count} questions.\n"
            f"Output must strictly be valid JSON conforming to the output schema in your instructions.\n"
        )
        user_prompt = prompt_builder.build_user_prompt(
            user_input=quiz_prompt,
            document_excerpts=excerpts,
            parsed_params=parsed.parsed_params
        )

        try:
            raw_json = await ai_provider.generate_structured(
                prompt=user_prompt,
                system_instruction=system_instruction,
                temperature=0.2
            )
            # Clean JSON if LLM returned markdown code fences
            cleaned_json = raw_json.strip()
            if cleaned_json.startswith("```json"):
                cleaned_json = cleaned_json[7:]
            if cleaned_json.startswith("```"):
                cleaned_json = cleaned_json[3:]
            if cleaned_json.endswith("```"):
                cleaned_json = cleaned_json[:-3]
            
            quiz_data = json.loads(cleaned_json.strip())
            display_text = f"### 📝 Diagnostic Quiz: {topic.capitalize()} ({difficulty.capitalize()})\nTest your understanding below:"
            
            return ChatResponse(
                response=display_text,
                command_used=cmd,
                skill_name="generate_quiz",
                citations=excerpts,
                structured_data=quiz_data,
                session_id=request.session_id,
            )
        except Exception as e:
            logger.error(f"Error generating quiz JSON: {e}")
            try:
                fallback_text = await ai_provider.generate_text(
                    prompt=user_prompt,
                    system_instruction=system_instruction
                )
                return ChatResponse(
                    response=fallback_text,
                    command_used=cmd,
                    skill_name="generate_quiz",
                    citations=excerpts,
                    session_id=request.session_id,
                )
            except Exception as e2:
                err_str = str(e2)
                raise HTTPException(status_code=400, detail=f"{provider_name.upper()} API error: {err_str}")

    # 6. General /explain, /answer, /summarize, or natural chat
    search_query = parsed.parsed_params.get("topic") or parsed.parsed_params.get("query") or request.message
    excerpts = await document_search.search(query=search_query, user_id=uid, top_k=4)

    system_instruction = prompt_builder.build_system_instruction(
        skill_instructions=skill.instructions if skill else None
    )
    user_prompt = prompt_builder.build_user_prompt(
        user_input=request.message,
        document_excerpts=excerpts,
        parsed_params=parsed.parsed_params
    )

    try:
        ai_text = await ai_provider.generate_text(
            prompt=user_prompt,
            system_instruction=system_instruction,
            temperature=0.7
        )
    except Exception as e:
        err_str = str(e)
        logger.error(f"Error calling {provider_name}: {err_str}")
        if "insufficient_quota" in err_str.lower() or "exceeded your current quota" in err_str.lower():
            clean_err = (
                "OpenAI Quota Notice: Your OpenAI developer account has $0 prepaid balance. "
                "OpenAI API requires prepaid credits at platform.openai.com/settings/organization/billing (ChatGPT Plus does not include API credits). "
                "👉 Solution: 1) Switch to Google Gemini (Free at aistudio.google.com), or 2) Switch to Demo Mode above to test all skills immediately."
            )
        elif "invalid_api_key" in err_str.lower() or "incorrect api key" in err_str.lower() or "api_key_invalid" in err_str.lower():
            clean_err = f"Invalid {provider_name.upper()} API key. Please check the key in the top navigation bar."
        elif "rate limit" in err_str.lower():
            clean_err = f"{provider_name.upper()} rate limit reached. Please wait a moment and try again."
        else:
            clean_err = f"{provider_name.upper()} API error: {err_str}"
        raise HTTPException(status_code=400, detail=clean_err)

    # Save to Supabase messages if client connected
    client = get_supabase_client()
    if client and request.session_id:
        try:
            client.table("messages").insert([
                {"session_id": request.session_id, "role": "user", "content": request.message, "command_used": cmd},
                {"session_id": request.session_id, "role": "assistant", "content": ai_text, "command_used": cmd}
            ]).execute()
        except Exception as e:
            logger.warning(f"Could not persist messages to Supabase: {e}")

    return ChatResponse(
        response=ai_text,
        command_used=cmd,
        skill_name=skill.name if skill else None,
        citations=excerpts,
        session_id=request.session_id,
    )

