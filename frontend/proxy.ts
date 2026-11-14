import { NextResponse, type NextRequest } from 'next/server';
import { accessFailure } from '@/lib/server-access';

export function proxy(request: NextRequest) {
  const rejected = accessFailure(request);
  if (rejected) return rejected;
  const response = NextResponse.next();
  response.headers.set('Cache-Control', 'no-store, private');
  response.headers.set('Referrer-Policy', 'no-referrer');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  return response;
}

export const config = { matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'] };
