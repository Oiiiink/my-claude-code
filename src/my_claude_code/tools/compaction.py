from my_claude_code.tools.contracts import ToolContext, ToolSpec, object_schema, ToolCheck, ToolCall
from my_claude_code.compaction.compaction import estimate_tokens

def compact(ctx: ToolContext, focus: str):
    return f"manual compaction triggered by {ctx.actor} at the context window of {estimate_tokens(ctx.runtime.history)} tokens."

SPECS = [
    ToolSpec(
        name="compact",
        description="Trigger manual conversation compression to reduce context window usage.",
        input_schema=object_schema({"focus": {"type": "string", "description": "what to preserve in the summary."}}, []),
        handler=compact,
    )
]