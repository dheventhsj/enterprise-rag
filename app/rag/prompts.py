"""Prompt templates for grounded generation."""

SYSTEM_PROMPT = """You are an enterprise knowledge assistant. Answer questions using ONLY the provided context.
If the context does not contain enough information, say you don't know and suggest uploading relevant documents.
Be concise, accurate, and professional. Do not invent facts."""

CONTEXT_TEMPLATE = """Context documents:
{context}

User question: {query}

Provide a clear, grounded answer based on the context above."""

STREAM_CONTEXT_TEMPLATE = CONTEXT_TEMPLATE


def build_context(chunks: list, max_tokens: int) -> str:
    """Assemble context string within token budget."""
    parts: list[str] = []
    total = 0
    for idx, chunk in enumerate(chunks, start=1):
        header = f"[Source {idx}: {chunk.original_filename}"
        if chunk.page_number:
            header += f", page {chunk.page_number}"
        header += f", chunk {chunk.chunk_index}]\n"
        block = header + chunk.content
        block_tokens = len(block.split())
        if total + block_tokens > max_tokens:
            break
        parts.append(block)
        total += block_tokens
    return "\n\n".join(parts)


def build_prompt(query: str, context: str) -> list[dict[str, str]]:
    """Build chat messages for the LLM."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": CONTEXT_TEMPLATE.format(context=context, query=query)},
    ]
