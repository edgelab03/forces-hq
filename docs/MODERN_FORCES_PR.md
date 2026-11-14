The existing dark dashboard and six text/radio destinations obscure the core actions. This Phase 1 update replaces them with the approved ivory/forest visual system, a compact home Ask panel, four connected quick-access cards and five native icon-button tabs: Home, Ask, Money, Explore, Me.

Presentation and routing are isolated in `modern_ui.py`, `modern_ui.css` and `ui_navigation.py`. An explicit Back action restores prior page/journey context. Existing field keys, policy safeguards, the merged TypeError hotfix, financial formulas, profile/benefit data and encrypted saving are preserved. Learning opens existing course/qualification planning; no Learning Credits entitlement content is added.

Validation and screenshots: `docs/MODERN_FORCES_PHASE1.md`. Automated tests cover legacy functionality and the new route history; browser checks cover 360/390/412/768px and desktop, with retained questions, cards/tabs, input clearance and saved journeys.

Known limitations: Streamlit routes the home draft on Enter/commit/arrow rather than on focus alone. The mic is disabled. Back is in-app; actual Android keyboard, toolbar, safe-area and browser-Back behaviour need physical testing. A targeted Next.js shell is proposed only for a later approved phase. Existing policy-source/review limits and manual encrypted persistence are unchanged.

No merge, publish or deployment performed. Review screenshots and the theme configuration, deploy the reviewed commit, then verify the hosted app independently.
