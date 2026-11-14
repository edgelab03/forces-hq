'use client';

import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { initialConversation, isConversation, sendMessage, type Conversation } from '@/lib/conversation';

type Context = {
  conversation: Conversation;
  draft: string;
  ready: boolean;
  setDraft: (text: string) => void;
  send: (text: string) => void;
  reset: () => void;
};
const PrototypeContext = createContext<Context | null>(null);
const storageKey = 'forces-hq-design-demo-v1';

export function PrototypeProvider({ children }: { children: ReactNode }) {
  const [conversation, setConversation] = useState(initialConversation);
  const [draft, setDraft] = useState('');
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(storageKey);
      if (raw) {
        const saved = JSON.parse(raw);
        if (isConversation(saved.conversation)) setConversation(saved.conversation);
        if (typeof saved.draft === 'string') setDraft(saved.draft.slice(0, 1000));
      }
    } catch { /* A storage-restricted tab can still use the in-memory demo. */ }
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    try { sessionStorage.setItem(storageKey, JSON.stringify({ conversation, draft })); }
    catch { /* No account or remote persistence is required. */ }
  }, [conversation, draft, ready]);

  function send(text: string) {
    if (!text.trim()) return;
    setConversation(current => sendMessage(current, text));
    setDraft('');
  }

  return <PrototypeContext.Provider value={{ conversation, draft, ready, setDraft, send, reset: () => { setConversation(initialConversation); setDraft(''); } }}>
    {children}
  </PrototypeContext.Provider>;
}

export function usePrototype() {
  const context = useContext(PrototypeContext);
  if (!context) throw new Error('PrototypeProvider is required');
  return context;
}
