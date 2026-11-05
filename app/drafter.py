"""Ask Claude for a quotation draft built only from the calculated figures. Nothing is sent to a customer."""
import os

MODEL = "claude-sonnet-5"
MAX_TOKENS = 1024

RULES = """You are the quote drafter for the Heicoders Catering weekday lunchbox service.
Write a short quotation email to the customer using only the order details given by the user.

Rules:
- Use the figures in the order details exactly. Do not calculate or change them.
- Do not mention costs, margins, discounts, free items or offers.
- Start the email with "Dear <customer>," and end it with "Warm regards," followed by
  "Priya Menon", "Sales and Events Lead" and "Heicoders Catering" on separate lines.
- Show boxes x price per box, delivery, GST and a line that starts with "Total payable".
- Mention the delivery date.
- Write amounts in Singapore dollars as S$.
- Keep the email under 150 words.
- Return only the email text, with no subject line or commentary.
"""


def build_prompt(quote, customer):
    """The order details sent to Claude: calculated figures, delivery date and the greeting name only."""
    return "\n".join([
        "ORDER",
        f"customer: {customer}",
        f"boxes: {quote['boxes']}",
        f"delivery_date: {quote['delivery_date']}",
        f"area: {quote['area']}",
        f"price_per_box: {quote['price_per_box']}",
        f"boxes_total: {quote['boxes_total']}",
        f"delivery_fee: {quote['delivery_fee']}",
        f"gst ({quote['gst_rate']}%): {quote['gst']}",
        f"total_payable: {quote['total']}",
    ])


def unavailable(message):
    return {"status": "unavailable", "email": None, "message": message}


def draft_email(quote, customer):
    """Return {"status", "email", "message"}. A cut-off, declined or failed draft is never returned."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return {"status": "no_key", "email": None, "message": "No API key configured"}

    import anthropic

    try:
        response = anthropic.Anthropic().messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=RULES,
            messages=[{"role": "user", "content": build_prompt(quote, customer)}],
        )
    except anthropic.APIConnectionError:
        print("draft: could not reach the API")
        return unavailable("Draft unavailable")
    except anthropic.APIStatusError as err:
        print(f"draft: API returned status {err.status_code}")
        return unavailable("Draft unavailable")

    if response.stop_reason != "end_turn":
        print(f"draft: stop_reason {response.stop_reason}")
        return unavailable("Draft unavailable")
    email = "".join(block.text for block in response.content if block.type == "text").strip()
    if not email:
        return unavailable("Draft unavailable")
    return {"status": "ok", "email": email, "message": "Draft for Priya Menon's approval. Not sent."}
