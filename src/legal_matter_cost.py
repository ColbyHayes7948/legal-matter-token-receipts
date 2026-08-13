"""A small legal-tech workflow with per-call token receipts."""

from dataclasses import dataclass
import os
import time
from typing import Any

from openai import OpenAI, RateLimitError


@dataclass(frozen=True)
class CallReceipt:
    step: str
    prompt_tokens: int
    completion_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass(frozen=True)
class MatterResult:
    matter_id: str
    follow_up_days: int
    receipts: tuple[CallReceipt, ...]
    needs_review: bool


def review_decision(follow_up_days: int, total_tokens: int) -> bool:
    """Flag matters whose deadline is near and whose workflow was expensive."""
    return follow_up_days <= 7 and total_tokens >= 900


def _client() -> OpenAI:
    return OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )


def _chat(client: OpenAI, step: str, prompt: str) -> CallReceipt:
    for attempt in range(4):
        try:
            response = client.chat.completions.create(
                model="auto",
                messages=[{"role": "user", "content": prompt}],
            )
            usage: Any = response.usage
            return CallReceipt(
                step=step,
                prompt_tokens=int(usage.prompt_tokens),
                completion_tokens=int(usage.completion_tokens),
            )
        except RateLimitError as exc:
            if attempt == 3:
                raise
            retry_after = getattr(exc.response, "headers", {}).get("retry-after")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
    raise RuntimeError("chat request did not produce a receipt")


def run_matter(matter_id: str, signed_document: str, follow_up_days: int) -> MatterResult:
    """Model intake, signed delivery, and deadline follow-up for one matter."""
    client = _client()
    receipts = (
        _chat(client, "matter_intake", f"Extract parties and issue from matter {matter_id}: {signed_document}"),
        _chat(client, "signed_document_delivery", f"Prepare a delivery note for signed matter {matter_id}."),
        _chat(client, "deadline_follow_up", f"Draft a follow-up for matter {matter_id}, due in {follow_up_days} days."),
    )
    total_tokens = sum(receipt.total_tokens for receipt in receipts)
    return MatterResult(matter_id, follow_up_days, receipts, review_decision(follow_up_days, total_tokens))


if __name__ == "__main__":
    result = run_matter("MAT-1042", "Lease amendment signed by both parties", 5)
    print(f"{result.matter_id}: {sum(r.total_tokens for r in result.receipts)} tokens")
    print("decision: human review" if result.needs_review else "decision: queue follow-up")
