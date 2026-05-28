from my_claude_code.config import (
    KEEP_RECENT,
    PRESERVE_RESULT_TOOLS,
    TRANSCRIPT_DIR,
    bcolors,
)
import json
import time
from anthropic import Anthropic

def estimate_tokens(messages: list) -> int:
    return len(str(messages)) // 4

def micro_compact(messages: list):
    tool_name_map = {}
    tool_results = []

    for msg in messages:
        if msg["role"] == "assistant" and isinstance(msg.get("content"), list):
            for block in msg["content"]:
                if getattr(block, "type", None) == "tool_use":
                    tool_name_map[block.id] = block.name

        if msg["role"] == "user" and isinstance(msg.get("content"), list):
            for block in msg["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    tool_results.append(block)

    for result in tool_results[:-KEEP_RECENT]:
        content = result.get("content", "")
        tool_name = tool_name_map.get(result.get("tool_use_id"), "")

        if (
            tool_name
            and isinstance(content, str)
            and len(content) > 100
            and tool_name not in PRESERVE_RESULT_TOOLS
        ):
            result["content"] = f"[Previous: used {tool_name}]"

def auto_compact(
    messages: list, 
    client: Anthropic, 
    model_id: str, max_token: int, 
    focus: str|None=None,
    ) -> list:
    focus = "no focus" if not focus else focus
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(json.dumps(msg, default=str) for msg in messages))

    print(bcolors.OKBLUE + f"transcript saved in {transcript_path}" + bcolors.ENDC)

    conversation_text = json.dumps(messages, default=str)[-80000:]
    response = client.messages.create(
        model=model_id,
        max_tokens=max_token,
        messages=[{"role":"user", "content":
                    "Summarize this conversation for continuity. Include: "
                    "1) What was accomplished, 2) Current state, 3) Key decisions made. 4) What to do next"
                    f"Focus: {focus}. Be concise but preserve critical details.\n\n" + conversation_text}]
    )

    summary = next((block.text for block in response.content if hasattr(block, "text")), "")
    if not summary:
        summary = "(no summary)"
    return [{"role": "user", "content": f"[Conversation compressed] transcript path:{transcript_path}\n\n{summary}"}]