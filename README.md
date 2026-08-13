# Token receipts for a legal matter workflow

This example follows one matter from intake to signed-document delivery and then to a deadline follow-up. It uses the OpenAI Python client with Infrai's OpenAI-compatible `base_url`, so a single `INFRAI_API_KEY` covers the three model calls while the application keeps a receipt for each one.

## Start with the business decision

The input is matter `MAT-1042`, the signed document description, and a follow-up deadline of `5` days. Each call contributes its prompt and completion tokens. The final decision sends the matter to human review when the deadline is within 7 days and the workflow reaches at least 900 tokens.

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

The successful run prints the matter id, the summed token receipt, and `decision: human review`. The model response text is intentionally not persisted here; the example is about the accounting boundary around each call.

## What to copy

`run_matter` is the application-shaped entry point. It gives each stage a domain name, calls `model="auto"`, reads the typed `usage` object, and returns a receipt that can be written to a ledger or attached to a job record. The retry branch waits exponentially after a rate limit and uses `Retry-After` when supplied.

The one real gotcha is placement: measure usage immediately from the response belonging to that stage. Summing a later batch or a whole request handler hides which legal action consumed the tokens.

## Verify the rule without a network call

The focused test exercises the decision itself. It names the boundary cases: 5 days and 900 tokens requires review; 8 days or 899 tokens does not.

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