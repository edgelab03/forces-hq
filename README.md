# Forces HQ V0.1

An independent educational **demonstration** app for exploring military career planning and financial concepts. Not affiliated with the Ministry of Defence.

## Launch on Streamlit Community Cloud
1. Create a **new, separate** GitHub repository called `forces-hq` (do not use your EdgeLab repository).
2. Upload `app.py`, `requirements.txt`, and the `.streamlit/config.toml` settings file (optional; app runs without the last file).
3. Go to https://share.streamlit.io and select **Create app → Yup, I have an app**.
4. Choose your `forces-hq` repository, branch `main`, main file `app.py`, then deploy.
5. To share your demo, ensure its sharing settings permit public viewing. Never enter sensitive information.

## Local run
`pip install -r requirements.txt`

`streamlit run app.py`

## What works
- Demo military profile
- Custom MPAR / SJAR / OJAR milestone tracking (session only)
- Achievement log and evidence-based structured draft (not generative AI)
- Budget and savings calculators
- Official policy links

## Important
- This is a proof of concept, not a policy eligibility engine, financial advice, a pension calculator, or a secure MOD system.
- No back-end persistence: inputs may disappear on refresh/restart, and should be fictional or non-sensitive.
- Do not upload service identifiers, real personnel records, official appraisal text, restricted documents or real finance data.
