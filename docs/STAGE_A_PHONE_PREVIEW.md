# Stage A: protected preview from your Android phone

**Preparation is complete; account setup and hosted checks are manual.** No Render service, Vercel deployment, merge or Stage B change has been made. Use Chrome; enable its **Desktop site** menu option if dashboard controls are hidden.

## 1. Keep three credentials in your password manager

Generate a **64-character random ASCII API token**, a preview username, and a **32+ character random preview password**. The API token is shared only between Render and Vercel. Your future backup passphrase is separate. Never paste credentials into GitHub files, chat, URLs or screenshots.

## 2. Render — create the API

Open [Render Dashboard](https://dashboard.render.com) → **New → Web Service → Git Provider**. Connect GitHub if required and choose:

| Setting | Exact value |
| --- | --- |
| Repository | `edgelab03/forces-hq` |
| Branch | `feat/forces-hq-connected-foundation` |
| Service name | `forces-hq-api-stage-a` or an available staging name |
| Language/runtime | **Docker**, not native Python |
| Root Directory | **Leave empty**: repository root |
| Dockerfile Path | `./backend/Dockerfile` |
| Docker Build Context Directory | `.` (repository root) |
| Docker Command | Leave empty; use the image's existing `CMD` |
| Region | Frankfurt, if available and suitable for your organisation |
| Instance | A paid, always-on Starter instance for predictable tests; approve the displayed cost yourself |
| Health Check Path | `/healthz` |
| Persistent disk / database | None |
| Auto-Deploy | **Off** for controlled staging releases |

Under Environment, add **before the first deployment**:

- `FHQ_API_TOKEN` = your generated API token.
- `PORT` = `8000` (the existing image binds `0.0.0.0:8000`).

Create the service and wait for **Live**. Copy its real `https://…onrender.com` origin. Do not add `/v1`. Root must not be `backend/`: the image needs shared root Python files. The Dockerfile-scoped context filter excludes working-tree secrets/caches and does not affect Streamlit. [Render Docker settings](https://render.com/docs/docker), [root/context rules](https://render.com/docs/monorepo-support), [ports](https://render.com/docs/web-services#port-binding).

Free services can sleep; their wake-up can exceed the frontend's 20-second API deadline. If you choose Free, test with synthetic data and allow a cold-start/retry rather than removing security controls. [Free-service limitations](https://render.com/docs/free).

## 3. Vercel — preview only

Open the **existing frontend project**. Confirm its root is `frontend`, preset **Next.js**, install `npm ci`, build `npm run build`, default Next.js output, Node.js **22.x**. Keep its production branch/domain and current Streamlit deployment unchanged. If project settings differ, stop before changing shared live settings and arrange a separate staging project.

In **Settings → Deployment Protection**, enable **Vercel Authentication** for preview URLs (Standard Protection). Keep the app's own username/password gate too. Do not create public sharing/bypass links. Native password protection can require a paid plan; Vercel Authentication is the intended option here. [Protection settings](https://vercel.com/docs/deployment-protection).

In **Settings → Environment Variables**, scope every entry to **Preview → this specific branch**, not Production:

| Server-only variable | Value |
| --- | --- |
| `FHQ_API_URL` | Actual Render HTTPS origin, no path |
| `FHQ_API_TOKEN` | Same token as Render |
| `FHQ_ACCESS_USERNAME` | Your preview username |
| `FHQ_ACCESS_PASSWORD` | Your preview password |
| `FHQ_FRONTEND_ORIGIN` | The exact stable branch-preview HTTPS origin |

Do **not** set `FHQ_ALLOW_LOCAL_API` or any `NEXT_PUBLIC_` credential. Mark credentials Secret/Sensitive where offered. Environment changes require a new deployment. [Branch-scoped variables](https://vercel.com/docs/environment-variables).

If no branch URL exists yet, initially use `https://preview-not-selected.invalid` for `FHQ_FRONTEND_ORIGIN`; this intentionally blocks profile writes. Choose **Deployments → Create Deployment** (possibly under `…`), enter the full feature branch and confirm **Preview**. Copy the actual **Git branch URL**, replace the placeholder origin, then redeploy that branch. Use the stable branch URL thereafter, not each build's changing URL. Do not select **Promote to Production**. [Dashboard deployment](https://vercel.com/docs/git), [stable branch URLs](https://vercel.com/docs/deployments/generated-urls).

## 4. Check protection before entering a profile

Close all existing Incognito tabs, then open a fresh Chrome **Incognito** session with no saved credentials:

- Render `/healthz`: only `{"status":"ok","api_version":"1"}`. This is intentionally public.
- Render `/v1/profile/options` and `/v1/capabilities`: `unauthorised` (HTTP 401), never profile data. Do not enter the API token in your browser.
- Vercel preview `/`, `/me` and `/api/backend/profile/options`: must require Vercel/app authentication. A blank JSON error saying `access_not_configured` (503) is fail-closed, not a working setup.
- JavaScript/CSS can be public; they must contain no credentials or user data. Never treat a public URL alone as proof of a leak or of successful protection.

Check account logging/monitoring does not record bodies, passwords or Authorization headers. Configure staging traffic/abuse limits where available; this is a private single-tester preview, not a multi-user production release. If any private endpoint opens anonymously, **stop and keep personal data out**.

## 5. Android acceptance: use synthetic details first

Open the stable preview URL normally. Complete Vercel sign-in and the app's separate username/password prompt. In **Me**, confirm a synthetic profile; **Home** must show your entered rank/service without fictional financial defaults. Edit it and verify Home updates.

In **Me → Backup**, download an encrypted `.fhq` file with a new passphrase. Refresh: the memory-only profile should clear. Restore from Android Downloads; a wrong passphrase must fail without replacing existing confirmed details, and the correct one must restore them. Test keyboard clearance, Back, rotation and switching between Home/Me. Keep the file and passphrase separately. No cloud sync is implied.

Record only pass/fail, device/browser version and deployment IDs; redact screenshots. Ask remains a labelled demo; money/policy/guided-benefit connections are not part of this acceptance.

## 6. Stop or roll back safely

- Before testing, record deployment IDs/commit and save a backup you want to keep.
- Render: **Deploys → last successful release → Rollback**; keep auto-deploy off. Check the token still matches Vercel: rollback can restore that release's environment values. [Render rollback behaviour](https://render.com/docs/rollbacks).
- Vercel: redeploy the last known-good commit as **Preview** with the matching protected environment; verify the branch URL targets it. Do not promote to production or remove authentication to fix a 401/503.
- If there is no good staging release, suspend the new Render service and remove/disable the staging preview. Keep production and Streamlit untouched. Revoke exposed credentials and retire old previews that still use them if a secret was disclosed.

The local validation evidence and known build-environment limitation are in [the preparation record](STAGE_A_DEPLOYMENT_PREPARATION.md). Account configuration, billing approval, real hosted URLs, platform log settings and physical Android results remain yours to complete.
