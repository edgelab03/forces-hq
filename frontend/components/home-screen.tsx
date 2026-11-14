'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowDownLeft, ArrowRight, ArrowUpRight, ChevronRight, GraduationCap, House, Landmark, ShieldCheck, Sparkles, UserRound, Wallet } from 'lucide-react';
import { Brand } from './app-shell';
import { usePrototype } from './prototype-provider';
import { homePrompt, lunchPrompt } from '@/lib/conversation';
import { PreviewSheet } from './preview-sheet';

export function HomeScreen() {
  const router = useRouter();
  const { draft, setDraft, send, reset, ready } = usePrototype();
  function ask(question: string) {
    reset();
    send(question);
    router.push('/ask');
  }

  return <>
    <header className="home-header"><Brand/><Link href="/?panel=profile" className="profile-avatar" aria-label="Open demo profile"><UserRound size={20} strokeWidth={1.6}/><span className="online-dot"/></Link></header>
    <main id="main-content" className="home-content" tabIndex={-1}>
      <section className="greeting"><div><p className="eyebrow">YOUR EVERYDAY, A LITTLE EASIER</p><h1>Hello, Alex<span>.</span></h1><p>A little clarity for your next move.</p></div><span className="preview-badge"><span/>Demo</span></section>
      <div className="home-grid">
        <div className="home-primary">
          <section className="ask-card" aria-labelledby="home-ask-title">
            <div className="ask-card-heading"><span className="ask-spark"><Sparkles size={20} strokeWidth={1.5}/></span><span className="ask-card-kicker">HERE TO HELP</span><ArrowUpRight size={19} strokeWidth={1.5}/></div>
            <h2 id="home-ask-title">Ask Forces HQ</h2><p>Your questions. A clearer way forward.</p>
            <form className="home-ask-form" onSubmit={event => { event.preventDefault(); if (draft.trim()) ask(draft); }}>
              <input aria-label="Your question" placeholder="What’s on your mind?" value={draft} onChange={e => setDraft(e.target.value)} maxLength={1000} disabled={!ready}/>
              <button aria-label="Send question to Ask" disabled={!ready || !draft.trim()} type="submit"><ArrowRight size={20}/></button>
            </form>
            <button className="example-question" onClick={() => ask(lunchPrompt)} disabled={!ready}>Try “Can I claim yesterday’s lunch?” <ChevronRight size={14}/></button>
          </section>
          <section className="quick-section" aria-labelledby="quick-title"><div className="section-heading"><h2 id="quick-title">Your essentials</h2><span>One place. Less admin.</span></div>
            <div className="quick-grid">
              <Link className="quick-card" href="/?panel=pay"><span className="quick-icon"><Wallet size={24} strokeWidth={1.5}/></span><span><strong>Pay</strong><small>See the bigger picture</small></span><ArrowUpRight size={16}/></Link>
              <button className="quick-card" onClick={() => ask(homePrompt)} disabled={!ready}><span className="quick-icon"><House size={24} strokeWidth={1.5}/></span><span><strong>Housing</strong><small>Make your next move</small></span><ArrowUpRight size={16}/></button>
              <Link className="quick-card" href="/?panel=pension"><span className="quick-icon"><Landmark size={24} strokeWidth={1.5}/></span><span><strong>Pension</strong><small>Look ahead with clarity</small></span><ArrowUpRight size={16}/></Link>
              <Link className="quick-card" href="/?panel=learning"><span className="quick-icon"><GraduationCap size={24} strokeWidth={1.5}/></span><span><strong>Learning</strong><small>Invest in what’s next</small></span><ArrowUpRight size={16}/></Link>
            </div>
          </section>
        </div>
        <div className="home-secondary">
          <section className="money-card" aria-labelledby="money-title"><div className="section-heading"><h2 id="money-title">A moment for your money</h2><span className="demo-label">SAMPLE FIGURES</span></div>
            <div className="money-values"><div><span className="money-label"><ArrowDownLeft size={14}/>Monthly income</span><strong>£2,850<span>.00</span></strong></div><span className="money-divider"/><div><span className="money-label"><span className="saving-dot"/>Set aside</span><strong>£420<span>.00</span></strong></div></div>
            <Link className="text-link" href="/?panel=money">Your money, at a glance <ArrowRight size={15}/></Link>
          </section>
          <section className="opportunity-card" aria-labelledby="opportunity-title"><div className="opportunity-art" aria-hidden="true"><House size={26} strokeWidth={1.4}/><span/><span/></div><div className="opportunity-copy"><span className="demo-label">DEMO OPPORTUNITY</span><h2 id="opportunity-title">A place to call your own</h2><p>Start exploring your home-buying plans.</p><button className="text-link" onClick={() => ask(homePrompt)} disabled={!ready}>Let’s take a look <ArrowRight size={15}/></button></div></section>
          <p className="home-footnote"><ShieldCheck size={14}/>Independent design demo. Sample profile & figures.</p>
        </div>
      </div>
    </main>
    <PreviewSheet/>
  </>;
}
