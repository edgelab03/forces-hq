'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { ArrowLeft, ArrowRight, Download, LockKeyhole, Plus, ShieldCheck, Trash2, Upload } from 'lucide-react';
import { useProfile } from './profile-provider';
import type { ProfileDocument, ServiceProfile } from '@/lib/profile-api';

const blank: ProfileDocument = { version: 1, events: [], benefits: null, profile: {
  service: '', rank: '', employment_type: 'Not specified', report: 'SJAR', transfer_history: 'None / not recorded', posting: 'Not specified', family: 'Not specified', accommodation_type: 'Not specified', years: 0, dependent_count: 0,
  pay_supplement: null, pay_increment: null, verified_pensionable_salary: null, salary_verified: false,
  join_date: null, dob: null, planned_exit: null, join_date_set: false, dob_set: false, planned_exit_set: false,
  pension_schemes: ['Not sure'], rank_history: [],
} };

export function ProfileScreen() {
  const { saved, options, connectionError, reconnect, save, restore, exportBackup, clear } = useProfile();
  const params = useSearchParams();
  const section = params.get('section') || 'service';
  const [draft, setDraft] = useState<ProfileDocument>(saved?.document || blank);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const [passphrase, setPassphrase] = useState('');
  const [restorePassphrase, setRestorePassphrase] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [promotionRank, setPromotionRank] = useState('');
  const [promotionDate, setPromotionDate] = useState('');
  const [confirmRestore, setConfirmRestore] = useState(false);
  const [confirmClear, setConfirmClear] = useState(false);
  useEffect(() => { setDraft(saved?.document || blank); }, [saved]);

  function update<K extends keyof ServiceProfile>(key: K, value: ServiceProfile[K]) {
    setDraft(current => ({ ...current, profile: { ...current.profile, [key]: value } }));
    setNotice('');
  }
  async function perform(action: () => Promise<void>, message: string) {
    setBusy(true); setError(''); setNotice('');
    try { await action(); setNotice(message); }
    catch (problem) { setError(problem instanceof Error ? problem.message : 'The profile could not be updated.'); }
    finally { setBusy(false); setPassphrase(''); setRestorePassphrase(''); }
  }
  function select(label: string, key: keyof ServiceProfile, choices?: string[]) {
    return <label className="profile-field">{label}<select aria-label={label} value={String(draft.profile[key] ?? '')} onChange={e => update(key, e.target.value as never)} required={key === 'rank' || key === 'service'}>
      {(key === 'rank' || key === 'service') && <option value="">Choose {label.toLowerCase()}</option>}
      {(choices || options?.choices[key] || []).map(choice => <option key={choice}>{choice}</option>)}
    </select></label>;
  }
  function dateField(label: string, key: 'join_date' | 'dob' | 'planned_exit') {
    return <label className="profile-field">{label}<input type="date" value={draft.profile[key] || ''} min={key === 'dob' ? '1940-01-01' : '1960-01-01'} max={key === 'planned_exit' ? '2080-12-31' : new Date().toISOString().slice(0, 10)} onChange={e => {
      const value = e.target.value || null;
      setDraft(current => ({ ...current, profile: { ...current.profile, [key]: value, [key + '_set']: value !== null } }));
    }}/></label>;
  }

  return <>
    <header className="chat-header"><Link className="icon-button" href="/" aria-label="Back to Home"><ArrowLeft size={22}/></Link><span className="chat-heading-mark"><ShieldCheck size={21}/></span><div><h1>Your service profile</h1><p>One profile. A more useful Forces HQ.</p></div></header>
    <main className="profile-scroll" id="main-content">
      <div className="profile-intro"><span className="preview-badge"><span/>Connected foundation · Stage A</span><h2>{saved ? 'Make it work for you.' : 'Start with your service.'}</h2><p>Confirm your details to personalise Home. Your information stays in this page’s memory until you choose an encrypted backup. Reloading clears it.</p></div>
      <nav className="profile-sections" aria-label="Profile sections">{[['service', 'Service'], ['context', 'Circumstances'], ['history', 'History'], ['backup', 'Backup']].map(([key, label]) => <Link key={key} href={`/me?section=${key}`} aria-current={section === key ? 'page' : undefined}>{label}</Link>)}</nav>
      {connectionError && <div className="connection-alert" role="alert"><p>{connectionError}</p><button className="text-link" onClick={reconnect}>Retry connection</button></div>}
      {error && <p className="connection-alert" role="alert">{error}</p>}
      {notice && <p className="saved-notice" role="status">{notice}</p>}
      {section === 'backup' ? <div className="profile-form">
        <section className="profile-card"><span className="sheet-icon"><LockKeyhole size={27}/></span><h2>Keep it in your hands</h2><p>Downloads use the existing Python .fhq encryption. Compatible Streamlit files retain their structured profile, career dates and home-buying progress. No automatic cloud saving.</p>
          <form onSubmit={e => { e.preventDefault(); void perform(() => exportBackup(passphrase), 'Encrypted backup downloaded. Keep the file and its passphrase separately.'); }}>
            <label className="profile-field">Backup passphrase<input type="password" autoComplete="new-password" minLength={12} maxLength={512} value={passphrase} onChange={e => setPassphrase(e.target.value)} required/></label>
            <button className="primary-button" disabled={busy || !saved}><Download size={18}/>Download encrypted profile</button>
          </form>
        </section>
        <section className="profile-card"><h2>Restore an encrypted profile</h2><p>Your current profile is replaced only after the Python service decrypts and validates the file. No names, service numbers, posting locations or free-text notes are imported.</p>
          <form onSubmit={e => { e.preventDefault(); if (file && confirmRestore) void perform(() => restore(file, restorePassphrase), 'Encrypted profile restored and confirmed. Home now uses these details.'); }}>
            <label className="profile-field">Encrypted profile file<input type="file" accept=".fhq" onChange={e => setFile(e.target.files?.[0] || null)} required/></label>
            <label className="profile-field">Restore passphrase<input type="password" autoComplete="off" maxLength={512} value={restorePassphrase} onChange={e => setRestorePassphrase(e.target.value)} required/></label>
            <label className="profile-check"><input type="checkbox" checked={confirmRestore} onChange={e => setConfirmRestore(e.target.checked)}/>Replace my current profile with the validated backup.</label>
            <button className="primary-button" disabled={busy || !file || !confirmRestore}><Upload size={18}/>Restore encrypted profile</button>
          </form>
        </section>
        {saved && <section className="profile-card"><h2>Clear this session</h2><label className="profile-check"><input type="checkbox" checked={confirmClear} onChange={e => setConfirmClear(e.target.checked)}/>I have saved any backup I want to keep.</label><button className="text-link" disabled={!confirmClear || busy} onClick={() => { clear(); setNotice('Profile cleared from this page. Downloaded files are unchanged.'); setConfirmClear(false); }}><Trash2 size={16}/>Clear profile from this page</button></section>}
      </div> : <form className="profile-form" onSubmit={e => { e.preventDefault(); void perform(() => save(draft), 'Profile confirmed. Home now uses your details. Export a backup to keep them after reload.'); }}>
        <fieldset disabled={busy || !options}>
          {section === 'service' && <section className="profile-card"><h2>Your service</h2><p>These are your confirmed entries, not verified service records.</p><div className="profile-grid">
            {select('Service', 'service')}{select('Rank', 'rank')}{select('Service type', 'employment_type')}{select('Appraisal type', 'report')}
            {dateField('Date joined (optional)', 'join_date')}{dateField('Date of birth (optional)', 'dob')}{dateField('Planned leaving date (optional)', 'planned_exit')}
            <label className="profile-field">Qualifying years (self-reported)<input type="number" min={0} max={45} step={1} value={draft.profile.years} onChange={e => update('years', Number(e.target.value))}/></label>
          </div><p className="field-note">Calendar service alone does not establish qualifying pension service or entitlement.</p></section>}
          {section === 'context' && <>
            <section className="profile-card"><h2>Your circumstances</h2><div className="profile-grid">{select('Service history', 'transfer_history')}{select('Posting circumstances', 'posting')}{select('Accommodation', 'accommodation_type')}
              <label className="profile-field">Number of dependants<input type="number" min={0} max={12} step={1} value={draft.profile.dependent_count} onChange={e => { update('dependent_count', Number(e.target.value)); }}/></label>
            </div></section>
            <section className="profile-card"><h2>Pension & earnings context</h2><p>Membership and earnings are your entries. No pension or pay calculation runs in Stage A.</p><div className="scheme-options">{options?.pension_schemes.map(scheme => <label className="profile-check" key={scheme}><input type="checkbox" checked={draft.profile.pension_schemes.includes(scheme)} onChange={e => {
              const named = draft.profile.pension_schemes.filter(value => value !== 'Not sure' && value !== scheme);
              update('pension_schemes', scheme === 'Not sure' ? ['Not sure'] : e.target.checked ? [...named, scheme] : named.length ? named : ['Not sure']);
            }}/>{scheme}</label>)}</div>
              <label className="profile-field">Annual pensionable earnings (£, optional)<input type="number" min={1} max={300000} step="0.01" value={draft.profile.verified_pensionable_salary ?? ''} onChange={e => update('verified_pensionable_salary', e.target.value ? Number(e.target.value) : null)}/></label>
              <label className="profile-check"><input type="checkbox" checked={draft.profile.salary_verified} onChange={e => update('salary_verified', e.target.checked)}/>I checked this pensionable earnings figure against my official documentation.</label>
              <p className="field-note">This records your attestation; Forces HQ has not independently verified the figure.</p>
            </section>
          </>}
          {section === 'history' && <section className="profile-card"><h2>Your promotion history</h2><p>Record confirmed dates. This does not reconstruct historic pay or pension entitlement.</p><div className="profile-grid">
            <label className="profile-field">Rank attained<select aria-label="Rank attained" value={promotionRank} onChange={e => setPromotionRank(e.target.value)}><option value="">Choose rank</option>{options?.choices.rank.map(rank => <option key={rank}>{rank}</option>)}</select></label>
            <label className="profile-field">Effective date<input type="date" min="1960-01-01" max={new Date().toISOString().slice(0, 10)} value={promotionDate} onChange={e => setPromotionDate(e.target.value)}/></label>
          </div><button type="button" className="text-link" disabled={!promotionRank || !promotionDate} onClick={() => { update('rank_history', [...draft.profile.rank_history, { rank: promotionRank, date: promotionDate }]); setPromotionDate(''); setPromotionRank(''); }}><Plus size={17}/>Add promotion</button>
            <ul className="profile-timeline">{draft.profile.rank_history.map((item, index) => <li key={index}><span><strong>{item.rank}</strong><small>{item.date}</small></span><button type="button" className="icon-button" aria-label={`Remove promotion ${index + 1}`} onClick={() => update('rank_history', draft.profile.rank_history.filter((_, i) => i !== index))}><Trash2 size={17}/></button></li>)}</ul>
            {draft.events.length > 0 && <><h3>Career dates from your backup</h3><ul className="profile-timeline">{draft.events.map((item, index) => <li key={index}><span><strong>{item.label}</strong><small>{item.date}</small></span></li>)}</ul></>}
          </section>}
          <button className="primary-button" type="submit" disabled={!draft.profile.service || !draft.profile.rank}>{busy ? 'Checking your profile…' : 'Confirm profile'}<ArrowRight size={18}/></button>
          <p className="field-note">Save changes before switching sections. No names, service numbers or operational information.</p>
        </fieldset>
      </form>}
    </main>
  </>;
}
