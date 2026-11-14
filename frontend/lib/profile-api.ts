export type ServiceProfile = {
  service: string; rank: string; employment_type: string; report: string; transfer_history: string;
  posting: string; family: string; accommodation_type: string; years: number; dependent_count: number;
  pay_supplement: number | null; pay_increment: number | null; verified_pensionable_salary: number | null;
  salary_verified: boolean; join_date: string | null; dob: string | null; planned_exit: string | null;
  join_date_set: boolean; dob_set: boolean; planned_exit_set: boolean; pension_schemes: string[];
  rank_history: { rank: string; date: string }[];
};
export type ProfileDocument = { version: 1; profile: ServiceProfile; events: { label: string; date: string }[]; benefits: Record<string, unknown> | null };
export type ProfileResponse = {
  schema_version: '1'; document: ProfileDocument;
  provenance: { profile: 'user_confirmed'; salary: 'user_attested' | 'not_confirmed'; policy: 'not_assessed' };
  storage: string;
  summary: { service: string; rank: string; employment_type: string; milestones: { label: string; date: string }[] };
};
export type ProfileOptions = { choices: Record<string, string[]>; pension_schemes: string[]; milestone_labels: string[] };

export async function callApi(path: string, method = 'GET', data?: unknown): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(`/api/backend/${path}`, { method, credentials: 'same-origin', cache: 'no-store', headers: data === undefined ? {} : { 'Content-Type': 'application/json' }, body: data === undefined ? undefined : JSON.stringify(data) });
  } catch { throw new Error('The profile service could not be reached. Your confirmed profile has not been changed. Please try again.'); }
  if (!response.ok) {
    if (response.status === 422) throw new Error('Check your profile dates, selections and backup passphrase. Your saved profile has not been changed.');
    if (response.status === 413) throw new Error('This file or profile is too large. The maximum backup file is 128 KB.');
    throw new Error('The secure profile service is unavailable. Your current profile has not been changed. Please try again.');
  }
  return response;
}
