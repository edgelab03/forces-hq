'use client';

import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useRef } from 'react';
import { ArrowRight, Compass, GraduationCap, Landmark, UserRound, Wallet, X } from 'lucide-react';

const panels = {
  pay: { title: 'Your pay connection', icon: Wallet, text: 'Python has a limited OR7 pay table. The API connection is Stage B; no pay is calculated in this foundation.', detail: 'Stage B', value: 'Not connected to this frontend' },
  money: { title: 'Your financial overview', icon: Wallet, text: 'Python budgets and future AFPS 15 models remain operational in Streamlit. Their API connection and charts follow in Stage B. No sample figures are shown.', detail: 'Stage B', value: 'Not connected to this frontend' },
  pension: { title: 'Plan with the right assumptions', icon: Landmark, text: 'Existing modelling covers future AFPS 15 accrual only. AFPS 05 reconstruction and EDP calculations do not exist. Python integration follows in Stage B.', detail: 'Stage B', value: 'Future AFPS 15 model only' },
  housing: { title: 'Your home-buying guide', icon: Compass, text: 'FHTB preparation and purchase budgets exist in Python. Guided frontend connection follows in Stage D. Restored journey progress remains in your encrypted backup.', detail: 'Stage D', value: 'Python journey not connected here' },
  learning: { title: 'Learning & development', icon: GraduationCap, text: 'Course and qualification planning exists in Python. The connection follows in Stage D. Learning Credits eligibility still requires development and policy review.', detail: 'Stage D', value: 'Learning Credits not assessed' },
  explore: { title: 'Explore service support', icon: Compass, text: 'Housing, claims, learning, family support and resettlement connect in Stages C–D. A profile alone never establishes eligibility.', detail: 'Stages C–D', value: 'Existing tools await connection' },
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
    {panel && <div className="sheet-content"><div className="sheet-handle"/><div className="sheet-topline"><span className="preview-badge"><span/>Not connected yet</span><button className="icon-button" onClick={close} aria-label="Close preview"><X size={21}/></button></div><span className="sheet-icon"><Icon size={30} strokeWidth={1.5}/></span><h2 id="sheet-title">{panel.title}</h2><p>{panel.text}</p><div className="sheet-example"><small>{panel.detail}</small><strong>{panel.value}</strong></div><Link className="primary-button" href="/me">Manage your profile <ArrowRight size={18}/></Link><button className="sheet-close text-link" onClick={close}>Back to Home</button></div>}
  </dialog>;
}
