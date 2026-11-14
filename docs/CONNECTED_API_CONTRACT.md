# Stage A data contract — version 1

The browser calls `/api/backend/...` on the Next.js origin. Next.js authenticates the preview user, checks mutation Origin/content type/body size, and forwards only allowlisted paths to Python `/v1/...` using a server-only Bearer credential. No credential, backup passphrase or profile travels in a query string. Python does not accept cross-origin browser access. Requests/responses containing profile information are `no-store, private`.

| Python endpoint | Next.js path suffix | Request | Response |
| --- | --- | --- | --- |
| `GET /healthz` | Not proxied | None | Minimal process health/version; no diagnostics |
| `GET /v1/capabilities` | `capabilities` | None | Connected Stage A capabilities and explicit deferred stages |
| `GET /v1/profile/options` | `profile/options` | None | Existing `profile_backup.CHOICES`, pension scheme values and milestone labels |
| `POST /v1/profile/validate` | `profile/validate` | ProfileDocument | ProfileResponse; validates without persistence |
| `PUT /v1/profile` | `profile` | ProfileDocument | ProfileResponse; **does not store a server profile** |
| `POST /v1/profile/backup/export` | `profile/backup/export` | `{document: ProfileDocument, passphrase: string}` | Binary existing `.fhq` file, fixed download filename |
| `POST /v1/profile/backup/restore` | `profile/backup/restore` | `{encrypted_file: base64_string, passphrase: string}` | ProfileResponse after authenticated decryption and validation |

Pay, pensions, benefit discovery, entitlement conversation, policy evidence and FHTB budget endpoints are **not implemented in Stage A**. No placeholder success response stands in for those services.

## ProfileDocument

Canonical `{version: 1, profile: ServiceProfile, events: Milestone[], benefits: {...}}`. `ServiceProfile` requires service and rank from the existing supported vocabulary. It accepts:

- Service type, appraisal type, service-history category, posting/family circumstances and accommodation category.
- Self-reported qualifying years (integer 0–45), dependant count (integer 0–12).
- Optional date joined, date of birth, planned exit (`YYYY-MM-DD`), date-presence flags derived from supplied dates.
- Scheme memberships: AFPS 75/05/15, RFPS 05, or `Not sure` alone.
- Optional legacy pay supplement/increment fields and annual pensionable earnings, with explicit user attestation.
- Promotion records `{rank, date}`. Birth must precede joining; promotion cannot precede joining or be in the future; leaving must follow joining.

The authoritative models are `backend/models.py`, backed by the unchanged `profile_backup.validate`; browser types live in `frontend/lib/profile-api.ts`. Unknown fields, boolean-as-number coercion, non-finite numbers and contradictory selections/dates are rejected. Missing optional fields are normalised, but no service/rank or salary is invented. No name, service number, detailed posting location, free-text note, achievement draft or question is accepted as profile data.

`events` and `benefits` preserve the existing validated milestone and FHTB backup structures. Stage A does not edit them or reassess their facts. No client-provided provenance can upgrade a field to independently verified information.

## ProfileResponse

```json
{
  "schema_version": "1",
  "document": {"version": 1, "profile": {}, "events": [], "benefits": {}},
  "provenance": {"profile": "user_confirmed", "salary": "not_confirmed", "policy": "not_assessed"},
  "storage": "browser_memory_with_explicit_encrypted_backup",
  "summary": {"service": "...", "rank": "...", "employment_type": "...", "milestones": []}
}
```

The empty objects above abbreviate the typed data. `salary` is `user_attested` only when the user confirms an entered amount. The legacy property name `salary_verified` retains compatibility; **the service has not independently checked a payslip**. No entitlement, monthly take-home pay or pension result is returned.

## Errors and privacy

Errors use `{error: {code: string, fields?: string[]}}`. Validation errors include field locations, never rejected values, raw JSON, passphrases or decrypted file content. Failed imports/updates leave the previously confirmed browser profile intact. Statuses: 400 query rejection, 401 missing/wrong auth, 403 origin rejection, 404 unsupported route, 413 size limit, 415 wrong content type, 422 invalid profile/backup, 503 unavailable/unconfigured upstream. Unknown backend/server failures are not rendered as internal diagnostics.

Both layers cap JSON bodies at 256 KB; existing backup import caps decrypted transport files at 128 KB. Passphrases are transient request secrets, cleared from the UI after the operation. Access logs are disabled for the API command; operators must also disable request-body/credential capture in gateways, hosting logs, monitoring and error collection. TLS is mandatory outside explicit loopback development. Proxy URLs are configured server-side, HTTPS-only outside explicit local mode, not derived from user input; redirects and arbitrary paths are refused.

No server database is introduced. React memory holds the confirmed document for navigation within the mounted app; reload/closing clears it. Personal profiles/drafts are not written to localStorage/sessionStorage. Users explicitly download and restore an encrypted file between sessions. The old demo plaintext session cache is removed on mount.
