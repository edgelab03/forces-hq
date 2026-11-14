# Forces HQ V1.0 product and architecture plan

## Product contract

ASK → ASSESS → EXPLAIN → EVIDENCE → ACT is the shared journey. A 19-year-old Private and a WO1 with identical circumstances receive the same underlying assessment. Rank or seniority alone must not award entitlement. Plain-English results appear first; exact evidence, exceptions, version dates and reasoning are available on demand. Missing evidence takes precedence over a plausible-looking result.

Initial implementation scope is **Forces Help to Buy, meals and duty mileage**. Refund of Legal Expenses (New Buyer) is a separate check within the home-buying plan; FHTB never implies eligibility for it. Existing budget, savings, career, achievement and limited pension capabilities remain available. Wider benefits do not expand until the initial journeys have verified end-to-end evidence.

## Personalised benefits requirements

Compare user-confirmed profile facts with current reviewed rules. Distinguish example data, user-confirmed facts, document-checked facts and assumptions. The benefits status vocabulary is:

- Appears eligible — supporting conditions verified, with a preliminary-assessment qualification.
- Potentially eligible — further information required.
- Not currently eligible — reason and relevant future milestones when supported by policy.
- Already claimed or completed — explicit user history, never official approval tracking.
- Policy verification required.

Explain why a benefit is suggested and what is still unknown. Do not repeatedly promote completed benefits. A home-buying goal can justify showing a planning guide; it cannot establish eligibility. The current production rule registry is empty pending source review, so the current interface correctly shows policy verification required, not an unsupported personalised award.

Every guided benefit must ultimately include: description; personal relevance; sourced financial values/restrictions; only necessary eligibility questions; verified application steps; forms/organisations/documents; deadlines; relevant calculators; exact policy evidence; persistent checklist progress. Do not imply JPA submission, retrieval of personnel records or official approval monitoring without an authorised integration.

## Forces Help to Buy priority

The implemented five-stage preparation flow is Start → Assess → Budget → Prepare → Progress. It connects the user's goal, source-gated assessment, purchase cashflow, separate legal-expense check, preparation tasks and encrypted cross-session restoration.

A completed production FHTB journey still requires current primary-source review of personal eligibility, salary basis and maximum advance, repayment and tax treatment, restrictions, application route, current JPA instructions/forms, approval/legal/completion sequence and deadlines. No numerical scheme limits have been invented or recovered from unverified legacy summaries. Those outputs stay unavailable until a reviewed rule pack passes its evidence gate.

The purchase planner keeps cash deposit, proposed advance, mortgage, property price, tax quote, legal/conveyancing, surveys, searches, registration and other costs separate. Generic repayment and mortgage amortisation illustrate user assumptions; they are not scheme terms or lender affordability approval. Tax routes distinguish England/Northern Ireland (HMRC SDLT), Scotland (Revenue Scotland LBTT) and Wales (Welsh Government LTT). Automatic current tax/relief calculations are **not implemented** without verified rates, effective dates and personal conditions. A solicitor/lender must confirm professional costs and acceptance of the funding arrangement. Refund of Legal Expenses remains a distinct evidence-gated assessment; it is not assumed to reduce the budget.

Checklist progress, completion history and structured budget assumptions can be saved in the existing password-encrypted `.fhq` profile file and restored in a new session. This is **explicit manual saving**, not automatic cross-device or cloud persistence. Clear this distinction in UI and review. Automatic durable saving requires identity and protected storage; it has not been disguised as an implemented feature.

## Learning Credits requirements — retained, deferred

Standard Learning Credits and Enhanced Learning Credits need **separate** verified eligibility rules, approved-course conditions, funding limits, personal contributions, deadlines, application steps/forms and exact current JSP 822 evidence. Use official MOD guidance and ELCAS. Do not infer eligibility from rank or service years, merge SLC/ELC into one entitlement, invent a contribution rate or assert that Forces HQ can submit an application. They remain requirements only until the initial FHTB, meals and mileage journeys have passed source and journey review. No new Learning Credits UI or award logic is shipped in this branch.

## Pay/pension contract

Useful saved-profile information comes before dedicated modelling controls. The money overview displays user-checked annual earnings and annual÷12 gross equivalent, declared pension scheme, entered service/exit dates and any last calculated AFPS 15 future-accrual scenario. It labels data provenance and excludes inferred net pay, undocumented specialist-pay treatment and calendar-time-as-qualifying-service assumptions.

Budget/savings, AFPS 15 future accrual and existing official-quote arithmetic remain intact. The inherited repository did **not** contain AFPS 05 reconstruction or EDP calculation logic, despite the desired product scope; do not invent those formulas or claim they were preserved and validated. Wider pension coverage requires source-backed reference fixtures and separate review.

## Streamlit assessment and migration proposal

Streamlit can support this bounded, deterministic assessment and guided preparation experience using native forms, containers, session state and `st.bottom`. The branch uses a stable bottom navigation and a small amount of scoped presentation CSS, with no fixed-position navigation scripts or framework rewrite.

Its limits remain material: server reruns, widget lifecycle, no native client-side route/back-stack model, no offline client, session loss after disconnect, limited control over mobile keyboard/resizing and no built-in application-specific automatic user storage. Manual encrypted export is not equivalent to a banking app's persistence. Real Android testing is mandatory; browser emulation cannot certify it.

A realistic migration, **not executed here**, is:

1. Keep the pure Python decision/evidence and arithmetic modules as the authoritative services, with versioned request/response schemas and contract tests.
2. Add a FastAPI service with explicit assessment sessions and structured evidence responses. Introduce identity and encrypted per-user progress storage only after threat/privacy/deletion review.
3. Build a Next.js mobile frontend with real routes, accessible navigation, draft persistence and deliberate back/return behaviour. Preserve the same rule result for both user personas.
4. Provide a separate ingestion/review administration path: immutable source hashes, policy version history, reviewer sign-off, regression fixtures and monitored refresh. Do not let a retrieved snippet automatically become a decision rule.
5. Migrate one journey at a time behind a feature flag, compare outputs with Streamlit, test Android, and retain rollback. No big-bang migration or new MOD integration without an approved plan.

## Release gate

This branch is **not a verified V1.0 entitlement release** while the production rule registry is empty. Outbound policy currently blocks official GOV.UK/MOD documents and GitHub's PR API. The saved network draft is not applied to the running environment. Source acquisition, reviewed FHTB/meal/mileage packs, verified application details, current tax/RLE coverage, physical Android and hosted deployment checks remain external/review gates. Passing synthetic rule tests does not approve policy. The rule-check CLI deliberately reports these gaps rather than a misleading completed release.
