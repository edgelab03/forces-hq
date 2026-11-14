import type { Metadata, Viewport } from 'next';
import localFont from 'next/font/local';
import { Suspense } from 'react';
import { PrototypeProvider } from '@/components/prototype-provider';
import { AppShell } from '@/components/app-shell';
import { ProfileProvider } from '@/components/profile-provider';
import './globals.css';

const manrope = localFont({ src: '../node_modules/@fontsource-variable/manrope/files/manrope-latin-wght-normal.woff2', variable: '--font-manrope', display: 'swap' });

export const metadata: Metadata = {
  title: 'Forces HQ — Connected foundation',
  description: 'Your confirmed service profile, with user-controlled encrypted backup. Stage A foundation.',
  robots: { index: false, follow: false },
};

export const viewport: Viewport = { width: 'device-width', initialScale: 1, viewportFit: 'cover', themeColor: '#F7F7F2', interactiveWidget: 'resizes-content' };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" className={manrope.variable}><body>
    <ProfileProvider><PrototypeProvider><Suspense fallback={<div className="loading-screen">Opening Forces HQ…</div>}><AppShell>{children}</AppShell></Suspense></PrototypeProvider></ProfileProvider>
  </body></html>;
}
