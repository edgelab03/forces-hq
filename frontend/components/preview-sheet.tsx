'use client';

import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useRef } from 'react';
import { ArrowRight, Compass, GraduationCap, Landmark, UserRound, Wallet, X } from 'lucide-react';

const panels = {
  pay: { title: 'A clearer view of your pay', icon: Wallet, text: 'A future home for your pay breakdown and planning tools. This prototype shows the design direction; it does not calculate or retrieve pay.', detail: 'Sample monthly income', value: '£2,850.00' },
  money: { title: 'Your money, at a glance', icon: Wallet, text: 'A simple view of what comes in and what you set aside. These are fictional sample figures, not your financial information.', detail: 'Sample monthly savings', value: '£420.00' },
  pension: { title: 'Space to plan ahead', icon: Landmark, text: 'Your pension deserves more than guesswork. This preview introduces the future planning area. Existing Python pension calculations have not been connected or changed.', detail: 'Pension tools', value: 'Coming in a later phase' },
  learning: { title: 'Make room for what’s next', icon: GraduationCap, text: 'A future space for qualifications, courses and development goals. No Learning Credits eligibility or funding is assessed in this prototype.', detail: 'Learning & development', value: 'Explore the design direction' },
  explore: { title: 'Your next step starts here', icon: Compass, text: 'A future home for opportunities across service life. Try the home-buying conversation to see how a guided experience could feel.', detail: 'Personalised opportunities', value: 'Demonstration content only' },
  profile: { title: 'Hello, Alex.', icon: UserRound, text: 'Alex is a fictional demo profile. There is no account, service-record connection or saved financial profile. Chat progress stays in this browser tab and can be reset in Ask.', detail: 'Your profile', value: 'Fictional demonstration' },
};

export function PreviewSheet() {
  const params = useSearchParams();
  const router = useRouter();
  const dialog = useRef<HTMLDialogElement>(null);
  const key = params.get('panel');
  const panel = key && key in panels ? panels[key as keyof typeof panels] : null;

  useEffect(() => {
    if (panel && !dialog.current?.open) dialog.current?.showModal();
    if (!panel && dialog.current?.open) dialog.current.close();
  }, [panel]);

  function close() { router.push('/', { scroll: false }); }
  const Icon = panel?.icon ?? Compass;
  return <dialog ref={dialog} className="preview-sheet" aria-labelledby="sheet-title" onCancel={e => { e.preventDefault(); close(); }} onClick={e => { if (e.target === e.currentTarget) close(); }}>
    {panel && <div className="sheet-content"><div className="sheet-handle"/><div className="sheet-topline"><span className="preview-badge"><span/>Preview only</span><button className="icon-button" onClick={close} aria-label="Close preview"><X size={21}/></button></div><span className="sheet-icon"><Icon size={30} strokeWidth={1.5}/></span><h2 id="sheet-title">{panel.title}</h2><p>{panel.text}</p><div className="sheet-example"><small>{panel.detail}</small><strong>{panel.value}</strong></div><Link className="primary-button" href="/ask">Try the Ask demo <ArrowRight size={18}/></Link><button className="sheet-close text-link" onClick={close}>Back to Home</button></div>}
  </dialog>;
}
