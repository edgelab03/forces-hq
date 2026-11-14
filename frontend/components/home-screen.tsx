'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowRight, ArrowUpRight, ChevronRight, GraduationCap, House, Landmark, ShieldCheck, Sparkles, UserRound, Wallet } from 'lucide-react';
import { Brand } from './app-shell';
import { usePrototype } from './prototype-provider';
import { lunchPrompt } from '@/lib/conversation';
import { useProfile } from './profile-provider';
import { PreviewSheet } from './preview-sheet';

export function HomeScreen() {
  const router = useRouter();
  const { draft, setDraft, send, reset, ready } = usePrototype();
  const { saved, connectionError, reconnect } = useProfile();
  const profile = saved?.document.profile;
  const milestone = saved?.summary.milestones.find(item => item.date >= new Date().toISOString().slice(0, 10));
  const progress = saved?.document.benefits?.fhtb as { interested?: boolean; completed?: boolean; step?: string } | undefined;
  function ask(question: string) {
    reset();
    send(question);
    router.push('/ask');
  }

  return <>
    <header className="home-header"><Brand/><Link href="/me" className="profile-avatar" aria-label="Open your profile"><UserRound size={20} strokeWidth={1.6}/><span className="online-dot"/></Link></header>
    <main id="main-content" className="home-content" tabIndex={-1}>
      <section className="greeting"><div><p className="eyebrow">YOUR SERVICE. YOUR NEXT STEP.</p><h1>{profile ? 'Welcome back' : 'Make it yours'}<span>.</span></h1><p>{profile ? `${profile.rank} · ${profile.service}` : 'A little clarity starts with your service profile.'}</p></div><span className="preview-badge"><span/>Stage A</span></section>
      {connectionError && <div className="connection-alert" role="alert"><p>{connectionError}</p><button className="text-link" onClick={reconnect}>Retry connection</button></div>}
      {!profile && <section className="onboarding-card"><ShieldCheck size={23}/><div><h2>Your service, in one place</h2><p>Add your confirmed details or restore an encrypted profile. No example profile or financial figures.</p><Link href="/me" className="text-link">Set up your profile <ArrowRight size={16}/></Link></div></section>}
      <div className="home-grid">
        <div className="home-primary">
          <section className="ask-card" aria-labelledby="home-ask-title">
            <div className="ask-card-heading"><span className="ask-spark"><Sparkles size={20} strokeWidth={1.5}/></span><span className="ask-card-kicker">CONVERSATION DEMO · STAGE C TO CONNECT</span><ArrowUpRight size={19} strokeWidth={1.5}/></div>
            <h2 id="home-ask-title">Ask Forces HQ</h2><p>Your questions. A clearer way forward.</p>
            <form className="home-ask-form" onSubmit={event => { event.preventDefault(); if (draft.trim()) ask(draft); }}>
              <input aria-label="Your question" placeholder="What’s on your mind?" value={draft} onChange={e => setDraft(e.target.value)} maxLength={1000} disabled={!ready}/>
              <button aria-label="Send question to Ask" disabled={!ready || !draft.trim()} type="submit"><ArrowRight size={20}/></button>
            </form>
            <button className="example-question" onClick={() => ask(lunchPrompt)} disabled={!ready}>Try the lunch conversation demo <ChevronRight size={14}/></button>
          </section>
          <section className="quick-section" aria-labelledby="quick-title"><div className="section-heading"><h2 id="quick-title">Your essentials</h2><span>One place. Less admin.</span></div>
            <div className="quick-grid">
              <Link className="quick-card" href="/?panel=pay"><span className="quick-icon"><Wallet size={24} strokeWidth={1.5}/></span><span><strong>Pay</strong><small>Python connection · Stage B</small></span><ArrowUpRight size={16}/></Link>
              <Link className="quick-card" href="/?panel=housing"><span className="quick-icon"><House size={24} strokeWidth={1.5}/></span><span><strong>Housing</strong><small>Guided connection · Stage D</small></span><ArrowUpRight size={16}/></Link>
              <Link className="quick-card" href="/?panel=pension"><span className="quick-icon"><Landmark size={24} strokeWidth={1.5}/></span><span><strong>Pension</strong><small>Python connection · Stage B</small></span><ArrowUpRight size={16}/></Link>
              <Link className="quick-card" href="/?panel=learning"><span className="quick-icon"><GraduationCap size={24} strokeWidth={1.5}/></span><span><strong>Learning</strong><small>Career connection · Stage D</small></span><ArrowUpRight size={16}/></Link>
            </div>
          </section>
        </div>
        <div className="home-secondary">
          <section className="money-card"><div className="section-heading"><h2>Your confirmed context</h2><span className="demo-label">{profile ? 'USER-ENTERED' : 'NOT ENTERED'}</span></div>
            {profile ? <><p className="profile-summary-line">{profile.employment_type} · {profile.pension_schemes.join(', ')}</p>{profile.salary_verified && profile.verified_pensionable_salary ? <><span className="money-label">Annual pensionable earnings · your attestation</span><strong className="confirmed-salary">{new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 2 }).format(profile.verified_pensionable_salary)}</strong><p className="field-note">Not a pay calculation or independently verified amount.</p></> : <p className="field-note">No confirmed earnings entered. No pay figure is assumed.</p>}<Link className="text-link" href="/me">Review your details <ArrowRight size={15}/></Link></> : <><p className="field-note">Complete your profile to see your rank, service and confirmed circumstances here.</p><Link className="text-link" href="/me?section=backup">Restore an encrypted profile <ArrowRight size={15}/></Link></>}
          </section>
          <section className="opportunity-card"><span className="opportunity-art" aria-hidden="true"><ShieldCheck size={26} strokeWidth={1.4}/></span><div className="opportunity-copy"><span className="demo-label">{milestone ? 'YOUR SAVED MILESTONE' : 'YOU CONTROL WHAT IS SAVED'}</span><h2>{milestone ? milestone.label : 'Keep your profile with you'}</h2><p>{milestone ? milestone.date : 'Download an encrypted backup to keep your confirmed details after this page closes.'}</p><Link className="text-link" href="/me?section=backup">Save or restore <ArrowRight size={15}/></Link></div></section>
          {progress?.interested && <section className="money-card"><h2 className="saved-journey-title">Saved home-buying plan</h2><p className="field-note">{progress.completed ? 'Recorded completed by you' : `Saved step: ${progress.step}`} · Restored from your file. Guided frontend connection follows in Stage D.</p><Link href="/?panel=housing" className="text-link">About your saved journey <ArrowRight size={15}/></Link></section>}
          <p className="home-footnote"><ShieldCheck size={14}/>Memory-only profile · No automatic cloud sync.</p>
        </div>
      </div>
    </main>
    <PreviewSheet/>
  </>;
}
