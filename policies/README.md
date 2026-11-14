# Reviewed rules, not search snippets

`rules.json` deliberately contains no approved production decisions while primary-source access and review are unavailable. Test fixtures are not copied here. A missing pack is a functional safety outcome, not a completed entitlement service.

Before approving any FHTB, meals or mileage pack:

1. Obtain current official documents through `scripts/index_policies.py`. Inspect complete provisions, definitions, restrictions and exceptions. Read the actual document rather than a search snippet.
2. Record rule ID/category/version, publication version/effective period, reviewer, review date/expiry, `coverage_complete` and `exceptions_reviewed`. Approval requires substantive review, not filling flags to get a green check.
3. Each `evidence` item needs official URL, publication title, document version, SHA-256, actual printed chapter/section/paragraph, PDF page and exact quotation. The gate matches digest, URL, paragraph, page, chapter, section and quotation against indexed text, and requires a publication check within 30 days. Unnumbered passages are not a substitute for an approved paragraph reference.
4. Bind every condition to `evidence_index`. Supported comparisons: `eq`, `in`, `gte`, `lte`. Questions use `choice`, `number` or `date`. A conditional question can use `when: {"fact": "an.earlier.fact", "equals": "Yes"}`; its dependency must precede it. Encode real exceptions as conditions/branches, not only explanatory prose. Rank/Service/seniority alone are rejected. User-confirmed circumstances remain preliminary evidence, not official service-record verification.
5. Set FHTB financial terms only from verified current provisions, with `financials_evidence_index`, an explicit `salary_fact` and a reviewed `salary_basis`. Do not assume that a pensionable-pay field is the scheme salary basis. The engine must never recover monetary limits from legacy summaries or unit tests. Applicable salary basis, other financial charges and repayment restrictions require their own reviewed conditions/evidence; simple illustrations are not complete scheme-cost advice.
6. Supply `claim_steps` with individual `evidence_index` references and official resource URLs only when `claim_process_verified` is true. Otherwise the interface explicitly withholds detailed JPA instructions, forms and deadlines.
7. Test qualifying, failing, missing-data, exception, date-boundary, changed-document and stale-source cases for each actual approved rule. Synthetic tests exercise mechanics, not policy truth. Rules need independent policy review.
8. Run `python scripts/validate_rules.py`. It must fail while any initial category lacks a valid pack. A code-test pass is not a release approval. Re-run after document refreshes; a changed hash or expired check invalidates decisions.

The actual current schema is enforced by `decision_engine.py`; do not use arbitrary Python expressions or executable rules. `policies/rules.json` is version controlled. Generated public documents/indexes are local cache artifacts, not user storage.
