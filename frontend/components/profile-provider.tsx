'use client';

import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from 'react';
import { callApi, type ProfileDocument, type ProfileOptions, type ProfileResponse } from '@/lib/profile-api';

type Context = {
  saved: ProfileResponse | null; options: ProfileOptions | null; connectionError: string;
  save: (document: ProfileDocument) => Promise<void>;
  restore: (file: File, passphrase: string) => Promise<void>;
  exportBackup: (passphrase: string) => Promise<void>; clear: () => void; reconnect: () => void;
};
const ProfileContext = createContext<Context | null>(null);

export function ProfileProvider({ children }: { children: ReactNode }) {
  const [saved, setSaved] = useState<ProfileResponse | null>(null);
  const [options, setOptions] = useState<ProfileOptions | null>(null);
  const [connectionError, setConnectionError] = useState('');
  const [attempt, setAttempt] = useState(0);
  const revision = useRef(0);
  useEffect(() => {
    let mounted = true;
    callApi('profile/options').then(r => r.json()).then(value => {
      if (mounted) { setOptions(value); setConnectionError(''); }
    }).catch(() => { if (mounted) setConnectionError('The profile service is not connected. You can retry; no demonstration profile will be substituted.'); });
    return () => { mounted = false; };
  }, [attempt]);

  async function save(document: ProfileDocument) {
    const version = ++revision.current;
    const response: ProfileResponse = await (await callApi('profile', 'PUT', document)).json();
    if (revision.current === version) setSaved(response);
  }
  async function restore(file: File, passphrase: string) {
    if (file.size > 128 * 1024) throw new Error('Choose an encrypted .fhq file no larger than 128 KB.');
    const version = ++revision.current;
    const bytes = new Uint8Array(await file.arrayBuffer());
    const encoded = btoa(Array.from(bytes, value => String.fromCharCode(value)).join(''));
    const response: ProfileResponse = await (await callApi('profile/backup/restore', 'POST', { encrypted_file: encoded, passphrase })).json();
    if (revision.current === version) setSaved(response);
  }
  async function exportBackup(passphrase: string) {
    if (!saved) throw new Error('Confirm your profile before exporting.');
    const response = await callApi('profile/backup/export', 'POST', { document: saved.document, passphrase });
    const url = URL.createObjectURL(await response.blob());
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'forces-hq-profile.fhq';
    document.body.appendChild(anchor); anchor.click(); anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return <ProfileContext.Provider value={{ saved, options, connectionError, save, restore, exportBackup, clear: () => { revision.current++; setSaved(null); }, reconnect: () => { setConnectionError(''); setAttempt(value => value + 1); } }}>{children}</ProfileContext.Provider>;
}

export function useProfile() {
  const state = useContext(ProfileContext);
  if (!state) throw new Error('ProfileProvider required');
  return state;
}
