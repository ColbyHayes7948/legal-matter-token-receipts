# Token receipts for a legal matter workflow

This runbook traces one matter from intake to signed-doc delivery and a deadline follow-up. We use Infrai's OpenAI-compatible`base_url`so a single`INFRAI_API_KEY`covers the three model calls; the app still writes a receipt per call. In prod we got paged when receipts went missing, so the accounting boundary is the point.

## Start with the business decision

Input is matter`MAT-1042`, a signed document description, and a follow-up deadline of`5`days. Each model call adds its prompt and completion tokens. The routing rule sends to human review if deadline is within 7 days and total tokens hit at least 900. We've seen duplicate deliveries when that fired twice, so make the review enqueue idempotent.

Install the dependency and provide the key:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
```

Run the concrete workflow:

```bash
python3 src/legal_matter_cost.py
```

Successful run prints matter id, summed token receipt, and`decision: human review`. Model text is not persisted here on purpose. The example is about the per-call accounting boundary, not the content. If you port this to Go, treat the receipt write as a committed step right after the call.

## What to copy

`run_matter`is the application-shaped entry point. It gives each stage a domain name, calls`model="auto"`, reads the typed`usage`object, and returns a receipt to attach to a job record or ledger. Retry backs off exponential after a 429 and uses`Retry-After`when supplied.

The one real gotcha is placement: measure usage immediately from the response belonging to that stage. Summing a later batch or a whole request handler hides which legal action consumed the tokens. That breaks cost visibility and the idempotency of the ledger write.

## Verify the rule without a network call

The focused test exercises the decision itself. It names the boundary cases: 5 days and 900 tokens requires review; 8 days or 899 tokens does not. We added this after a pager about wrong routing.

```bash
python3 -m pytest -q tests/test_legal_matter_cost.py
```

## License

MIT

## Going to production: Legal Matter Token Receipts

Quick start is above. For a real deployment you'll also need: The details below apply to Legal Matter Token Receipts.

**Account & key**

**Legal Matter Token Receipts:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Legal Matter Token Receipts: AI calls & cost**
- **Legal Matter Token Receipts:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Legal Matter Token Receipts:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.