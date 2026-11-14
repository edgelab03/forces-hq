'use client';

import Link from 'next/link';
import { useEffect, useRef } from 'react';
import { ArrowLeft, ArrowUp, Check, ChevronRight, Info, RotateCcw, Sparkles } from 'lucide-react';
import { usePrototype } from './prototype-provider';
import { suggestedAnswers } from '@/lib/conversation';

export function AskScreen() {
  const { conversation, draft, setDraft, send, reset, ready } = usePrototype();
  const scroller = useRef<HTMLElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);
  const choices = suggestedAnswers(conversation);
  const complete = conversation.flow && choices.length === 0;

  useEffect(() => {
    const element = scroller.current;
    if (element) element.scrollTo({ top: element.scrollHeight, behavior: 'instant' });
  }, [conversation, ready]);

  // Resizing the visual viewport (including an Android keyboard) keeps the latest
  // response inside the scroll area while the composer remains in normal layout.
  useEffect(() => {
    const observer = new ResizeObserver(() => {
      const element = scroller.current;
      if (element) element.scrollTop = element.scrollHeight;
    });
    if (scroller.current) observer.observe(scroller.current);
    return () => observer.disconnect();
  }, []);

  return <>
    <header className="chat-header"><Link href="/" className="icon-button" aria-label="Back to Home"><ArrowLeft size={22} strokeWidth={1.6}/></Link><span className="chat-heading-mark"><Sparkles size={21} strokeWidth={1.5}/></span><div><h1>Ask Forces HQ</h1><p>A little clarity. One step at a time.</p></div><button className="icon-button reset-button" onClick={reset} aria-label="Start a new demo conversation" title="Start a new demo conversation"><RotateCcw size={18}/></button></header>
    <div className="demo-notice"><Info size={15}/><p><strong>Demonstration flow</strong><span> · No eligibility decision or verified policy.</span></p></div>
    <main id="main-content" className="conversation-scroll" ref={scroller} tabIndex={-1}>
      <div className="conversation-inner"><p className="conversation-date">YOUR SPACE TO ASK</p>
        <div role="log" aria-label="Conversation" aria-live="polite" aria-relevant="additions text" className="message-list">
          {conversation.messages.map(message => <div className={`message-row ${message.role}`} key={message.id}>
            {message.role === 'assistant' && <span className="assistant-avatar" aria-label="Forces HQ"><Sparkles size={17} strokeWidth={1.5}/></span>}
            <div className="message-bubble"><span className="visually-hidden">{message.role === 'user' ? 'You: ' : 'Forces HQ: '}</span><p>{message.text}</p>{message.role === 'user' && <Check size={12} className="message-check" aria-label="Added to demo conversation"/>}</div>
          </div>)}
        </div>
        {choices.length > 0 && <div className="suggestions"><p>{conversation.flow ? 'CHOOSE OR TYPE YOUR ANSWER' : 'A FEW IDEAS TO GET STARTED'}</p><div>{choices.map(choice => <button key={choice} className={conversation.flow ? 'answer-button' : 'prompt-button'} onClick={() => send(choice)} disabled={!ready}>{choice}<ChevronRight size={15}/></button>)}</div></div>}
        {complete && <section className="conversation-summary" aria-label="Your demo context"><span className="demo-label">YOUR DEMO CONTEXT</span><h2>Ready for a real policy check</h2><ul>{conversation.answers.map((answer, i) => <li key={i}><span>{i + 1}</span>{answer}</li>)}</ul><p>This summary records your answers. It is not an approval, claim submission or policy assessment.</p><button className="text-link" onClick={reset}>Try another demonstration <RotateCcw size={14}/></button></section>}
      </div>
    </main>
    <div className="composer-area"><form className="composer" onSubmit={event => { event.preventDefault(); send(draft); input.current?.focus({ preventScroll: true }); }}>
      <label className="visually-hidden" htmlFor="chat-message">Your message</label>
      <textarea ref={input} id="chat-message" placeholder="Tell me a little more…" rows={1} maxLength={1000} value={draft} disabled={!ready} onChange={e => setDraft(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); send(draft); } }}/>
      <button className="send-button" type="submit" aria-label="Send message" disabled={!ready || !draft.trim()}><ArrowUp size={21}/></button>
    </form><p className="composer-note">Scripted demo · No AI API · Use fictional details only</p></div>
  </>;
}
