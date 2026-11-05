```mermaid
flowchart TD
    CSV[/"lunchlink-orders.csv<br/>untrusted notes column"/]
    RATES[("rates-lunchbox.json<br/>tiers · fees · GST · min 20")]
    BRIEF[("brief.md<br/>rules + 3 reference cases")]
    TERMS[("terms.md<br/>what a quote may say")]

    CSV --> OR["order-reader agent"]
    OR --> OJ[/"outputs/orders/&lt;order&gt;.json<br/>note.role = data_only"/]

    CSV --> PB["prepare_batch.py<br/>map boxes · date · area"]
    PB --> V{"Valid data?<br/>known area · date ≥ RUN_DATE<br/>· boxes ≥ 20"}
    V -- "No / error" --> OPEN["Open item for Priya<br/>no quote, no prompt"]
    V -- Yes --> CALC["Deterministic calculator<br/>Decimal · one tier price · GST half-up"]
    RATES -.-> CALC
    BRIEF -. "reference cases<br/>tests/test_reference_cases.py" .-> CALC

    CALC --> G{"guardrail.py check_note()<br/>Suspicious note?"}
    G -- Yes --> FLAG["FLAGGED FOR PRIYA<br/>real calculation kept<br/>no drafter prompt · no customer output"]
    G -- "No: valid order" --> PR[/"outputs/prompts/&lt;order&gt;.txt<br/>+ outputs/prepared.json<br/>note excluded"/]

    PR --> QD["quote-drafter agent"]
    QD --> DR[/"outputs/drafts/&lt;order&gt;.json"/]
    DR --> CD{"check_drafts.py<br/>total & price_per_box match?<br/>required phrases present?"}
    CD -- "FAIL, exit 1" --> PRIYA
    CD -- PASS --> QJ{"quote-judge agent<br/>unsupported claims?"}
    TERMS -.-> QJ
    RATES -.-> QJ
    QJ --> JR[/"outputs/judge-report.md<br/>PASS / FAIL per draft"/]

    OPEN --> PRIYA
    FLAG --> PRIYA
    JR --> PRIYA{{"Priya Menon<br/>human review & approval"}}
    PRIYA --> STOP["Nothing sent automatically<br/>Priya sends any approved quote herself"]
```

Some notes on how I drew it:
- **order-reader is a side branch.** `prepare_batch.py` reads the CSV directly. It doesn't read the order-reader's JSON files, so the diagram doesn't connect the two.
- **The order is: check the data, then calculate, then run the guardrail.** That's the order the code runs in, which is why a flagged order still has its real figures.
- **brief.md has a dotted link to the calculator.** No code reads it at runtime. Its reference cases are what the tests check the calculator against.
- **A failed check goes to Priya, not back to the drafter.** Nothing currently retries automatically.
- **The open-item check covers today's behaviour.** It catches unknown area names (e.g. `Sentosa Cove`), dates read wrongly as month-first, and orders under 20 boxes.
