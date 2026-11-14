/** Scripted design demonstration. No policy engine, inference or eligibility award. */
export type Message = { id: string; role: 'user' | 'assistant'; text: string };
export type Flow = 'meal' | 'housing' | 'mileage';
export type Conversation = {
  messages: Message[];
  flow: Flow | null;
  step: number;
  answers: string[];
};

export const lunchPrompt = 'Can I claim my lunch from yesterday?';
export const homePrompt = 'I’m thinking about buying a home.';
export const openingPrompts = [lunchPrompt, homePrompt];
export const initialConversation: Conversation = {
  messages: [{ id: 'welcome', role: 'assistant', text: 'Hi Alex. What can I help you with today? We can work through it, one step at a time.' }],
  flow: null,
  step: 0,
  answers: [],
};

const flows: Record<Flow, { questions: string[]; options: string[][] }> = {
  meal: {
    questions: [
      'Let’s start with the circumstances. Were you away from your normal place of duty when you bought lunch?',
      'Thanks, that helps. Was the journey or temporary duty authorised for work?',
      'One more detail: was a meal provided, or was one already included with your duty?',
    ],
    options: [
      ['Yes, I was away', 'No, my usual place', 'I’m not sure'],
      ['Yes, it was authorised', 'No', 'I’m not sure'],
      ['No meal was provided', 'A meal was available', 'I’m not sure'],
    ],
  },
  housing: {
    questions: [
      'An exciting next step. Where are you in your home-buying plans?',
      'What would be most useful to organise first?',
    ],
    options: [
      ['Just exploring', 'Saving a deposit', 'Found a property'],
      ['My purchase budget', 'Questions for my lender', 'What to ask unit admin'],
    ],
  },
  mileage: {
    questions: [
      'Let’s put the journey in context. Was it for work or your normal commute?',
      'Was using your own vehicle authorised for that journey?',
    ],
    options: [
      ['A work journey', 'My normal commute', 'I’m not sure'],
      ['Yes, it was authorised', 'No', 'I’m not sure'],
    ],
  },
};

export function suggestedAnswers(state: Conversation): string[] {
  if (!state.flow) return openingPrompts;
  return flows[state.flow].options[state.step] ?? [];
}

export function sendMessage(state: Conversation, input: string): Conversation {
  const text = input.trim().slice(0, 1000);
  if (!text) return state;
  const sequence = (Number.parseInt(state.messages.at(-1)?.id ?? '', 10) || 0) + 1;
  const messages: Message[] = [...state.messages, { id: `${sequence}-user`, role: 'user', text }];
  let { flow, step, answers } = state;
  let response: string;
  if (!flow) {
    flow = /\b(lunch|meal|breakfast|dinner)\b/i.test(text) ? 'meal'
      : /\b(home|house|housing|property|buying)\b/i.test(text) ? 'housing'
      : /\b(mileage|travel|journey|vehicle)\b/i.test(text) ? 'mileage' : null;
    response = flow ? flows[flow].questions[0]
      : 'This demo can walk through a meal claim, a work journey or a home-buying plan. Which would you like to explore?';
  } else if (step < flows[flow].questions.length) {
    answers = [...answers, text];
    step += 1;
    response = flows[flow].questions[step] ?? 'That’s the context gathered for this demonstration. I haven’t assessed your eligibility or verified any policy. For a real decision, check the current official guidance and confirm the requirements with your unit admin before spending or submitting a claim.';
  } else {
    response = 'That would need a real policy check. Your earlier answers are still here to review. You can also start a new demo to explore another situation.';
  }
  messages.push({ id: `${sequence + 1}-assistant`, role: 'assistant', text: response });
  return { messages: messages.slice(-60), flow, step, answers };
}

export function isConversation(value: unknown): value is Conversation {
  if (!value || typeof value !== 'object') return false;
  const state = value as Conversation;
  return (state.flow === null || ['meal', 'housing', 'mileage'].includes(state.flow))
    && Number.isInteger(state.step) && state.step >= 0 && state.step <= 3
    && Array.isArray(state.answers) && state.answers.length <= 3 && state.answers.every(a => typeof a === 'string' && a.length <= 1000)
    && Array.isArray(state.messages) && state.messages.length > 0 && state.messages.length <= 60
    && state.messages.every(m => m && typeof m.id === 'string' && ['user', 'assistant'].includes(m.role) && typeof m.text === 'string' && m.text.length <= 2000);
}
