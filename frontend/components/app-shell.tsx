'use client';

import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import { useEffect, type ReactNode } from 'react';
import { House, MessageCircle, WalletCards, Compass, UserRound } from 'lucide-react';

const destinations = [
  { label: 'Home', href: '/', icon: House, panel: null },
  { label: 'Ask', href: '/ask', icon: MessageCircle, panel: null },
  { label: 'Money', href: '/?panel=money', icon: WalletCards, panel: 'money' },
  { label: 'Explore', href: '/?panel=explore', icon: Compass, panel: 'explore' },
  { label: 'Me', href: '/?panel=profile', icon: UserRound, panel: 'profile' },
];

export function Brand() {
  return <Link className="brand" href="/" aria-label="Forces HQ home">
    <span className="brand-mark" aria-hidden="true"><svg viewBox="0 0 28 32" fill="none"><path d="M7 25V7h16M7 15h11" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round"/><path d="M20 23v3" stroke="#C89B48" strokeWidth="3" strokeLinecap="round"/></svg></span>
    <span><strong>Forces HQ<span className="brand-period">.</span></strong><small>Your service. Simplified.</small></span>
  </Link>;
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const params = useSearchParams();
  const panel = params.get('panel');

  useEffect(() => {
    const viewport = window.visualViewport;
    if (!viewport) return;
    let frame = 0;
    function update() {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        if (!viewport) return;
        const editing = document.activeElement?.matches('textarea, input');
        document.documentElement.style.setProperty('--app-height', `${viewport.height}px`);
        document.documentElement.style.setProperty('--viewport-top', `${viewport.offsetTop}px`);
        document.documentElement.dataset.keyboard = String(Boolean(editing && window.innerHeight - viewport.height > 120));
      });
    }
    update();
    viewport.addEventListener('resize', update);
    viewport.addEventListener('scroll', update);
    document.addEventListener('focusin', update);
    document.addEventListener('focusout', update);
    return () => {
      cancelAnimationFrame(frame);
      viewport.removeEventListener('resize', update);
      viewport.removeEventListener('scroll', update);
      document.removeEventListener('focusin', update);
      document.removeEventListener('focusout', update);
    };
  }, []);

  return <div className={`app-shell ${pathname === '/ask' ? 'ask-shell' : 'home-shell'}`}>
    <a className="skip-link" href="#main-content">Skip to content</a>
    {children}
    <nav className="bottom-nav" aria-label="Main navigation">
      <div className="nav-inner">{destinations.map(({ label, href, icon: Icon, panel: target }) => {
        const active = target ? pathname === '/' && panel === target : label === 'Ask' ? pathname === '/ask' : pathname === '/' && !panel;
        return <Link href={href} key={label} className={`nav-item ${active ? 'active' : ''}`} aria-current={active ? 'page' : undefined}>
          <span className="nav-icon"><Icon size={22} strokeWidth={1.7}/></span><span>{label}</span>
        </Link>;
      })}</div>
    </nav>
  </div>;
}
