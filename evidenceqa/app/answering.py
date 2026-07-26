"""Answer generation with retrieval-augmented generation (RAG)."""

import os
from dataclasses import dataclass
from typing import Protocol


@dataclass
class AnswerResult:
    answer: str
    sources: list[dict]


class AnswerProvider(Protocol):
    """Provider interface for answer generation from retrieved contexts."""

    def answer(self, question: str, contexts: list[dict]) -> AnswerResult:
        ...


class TemplateAnswerer:
    """Deterministic template-based answerer for offline development and testing."""

    def answer(self, question: str, contexts: list[dict]) -> AnswerResult:
        if not contexts:
            answer = "未找到相关文档来回答此问题。"
        else:
            first = contexts[0]
            snippet = first["content"][:150]
            if len(first["content"]) > 150:
                snippet += "..."
            answer = (
                f"根据检索到的文档内容：{snippet}\n\n"
                f"（这是模板回答，用于演示引用流程。配置 OPENAI_API_KEY 和 OPENAI_BASE_URL 环境变量可启用 LLM 回答。）"
            )
        return AnswerResult(answer=answer, sources=contexts)


class LLMAnswerer:
    """OpenAI-compatible LLM answerer with structured citation."""

    def __init__(self, api_key: str, base_url: str | None = None, model: str = "gpt-3.5-turbo"):
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def answer(self, question: str, contexts: list[dict]) -> AnswerResult:
        if not contexts:
            return AnswerResult(answer="未找到相关文档来回答此问题。", sources=[])

        context_text = "\n---\n".join(
            f"[文档片段 {i + 1}，来自《{ctx['title']}》]\n{ctx['content']}"
            for i, ctx in enumerate(contexts)
        )
        prompt = f"""你是一个专业的企业知识库助手。请仅根据下面提供的上下文回答用户问题。如果上下文中没有足够信息，请明确说明。

上下文：
{context_text}

问题：{question}

回答："""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        answer = response.choices[0].message.content or "（未生成回答）"
        return AnswerResult(answer=answer, sources=contexts)


def get_answer_provider() -> AnswerProvider:
    """Select answer provider based on environment configuration."""
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    if api_key:
        return LLMAnswerer(api_key=api_key, base_url=base_url, model=model)
    return TemplateAnswerer()
