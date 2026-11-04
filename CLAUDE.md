# Lunchbox Desk

Prices weekday lunchbox orders for Heicoders Catering and drafts quotations for Priya Menon (Sales and Events Lead) to approve. Nothing is ever sent to a customer.

## Files

- `rates-lunchbox.json`: the only source of prices, delivery fees, GST and the minimum order
- `terms.md`: what a quotation may and may not say
- `lunchlink-orders.csv`: this morning's order file from LunchLink (batch date 30 September 2026)
- `scripts/prepare_batch.py`: maps each order, calculates the quote and writes a prompt to `outputs/prompts/`
- `scripts/check_drafts.py`: checks drafts in `outputs/drafts/` against the calculator
- `.claude/agents/quote-drafter.md`: writes one draft quotation per prepared order
- `.claude/agents/quote-judge.md`: reviews drafts for claims the code check cannot see
- `staff/` and `reference/`: confidential internal files

## Commands

```
python3 scripts/prepare_batch.py lunchlink-orders.csv
python3 scripts/check_drafts.py outputs/drafts/
```
