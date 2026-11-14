import 'server-only';
import { createHash, timingSafeEqual } from 'node:crypto';

function same(left: string, right: string) {
  return timingSafeEqual(createHash('sha256').update(left).digest(), createHash('sha256').update(right).digest());
}

/** Private preview protection, not a multi-user identity/account system. */
export function accessFailure(request: Request): Response | null {
  const username = process.env.FHQ_ACCESS_USERNAME;
  const password = process.env.FHQ_ACCESS_PASSWORD;
  if (!username || !password || password.length < 20) {
    return Response.json({ error: { code: 'access_not_configured' } }, { status: 503, headers: { 'Cache-Control': 'no-store' } });
  }
  const auth = request.headers.get('authorization') || '';
  let provided = '';
  if (auth.startsWith('Basic ') && auth.length <= 2048) {
    try { provided = Buffer.from(auth.slice(6), 'base64').toString('utf8'); } catch { /* Reject malformed credentials. */ }
  }
  if (!same(provided, `${username}:${password}`)) {
    return Response.json({ error: { code: 'unauthorised' } }, { status: 401, headers: { 'WWW-Authenticate': 'Basic realm="Forces HQ private foundation", charset="UTF-8"', 'Cache-Control': 'no-store' } });
  }
  return null;
}
