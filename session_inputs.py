"""Keep page inputs in this browser session when Streamlit hides their widgets."""

import streamlit as st


def retain_inputs():
    # Start this render and apply resets before creating any widgets.
    for key in st.session_state.pop('_reset_inputs', []):
        st.session_state.pop(key, None)
    st.session_state['_previous_input_keys'] = st.session_state.get('_rendered_input_keys', [])
    st.session_state['_rendered_input_keys'] = []


def retain_hidden_inputs():
    # Detach only hidden widgets from Streamlit's cleanup cycle. Reassigning
    # active inputs forces their old values back to the browser during a rerun
    # and can overwrite edits made while that rerun is still in flight.
    rendered = set(st.session_state.get('_rendered_input_keys', []))
    for key in st.session_state.get('_input_keys', []):
        if key not in rendered and key in st.session_state:
            st.session_state[key] = st.session_state[key]


def rerun_with_retained_inputs():
    # An explicit rerun can exit before the end-of-page retention call.
    retain_hidden_inputs()
    st.rerun()


class SessionInputs:
    """Native Streamlit inputs with stable, page-scoped keys (no disk storage)."""

    types = {'checkbox', 'date_input', 'multiselect', 'number_input', 'radio',
             'selectbox', 'slider', 'text_area', 'text_input'}

    def __init__(self, page):
        self.page = page

    def key(self, label):
        return f'input:{self.page}:{label}'

    def __getattr__(self, kind):
        if kind not in self.types:
            raise AttributeError(kind)

        def render(label, *args, **kwargs):
            key = self.key(kwargs.pop('key', label))
            if kind == 'date_input':
                kwargs.setdefault('format', 'DD/MM/YYYY')
            keys = st.session_state.setdefault('_input_keys', [])
            if key not in keys:
                keys.append(key)
            if key not in st.session_state.get('_previous_input_keys', []) and key in st.session_state:
                # A returning widget needs its retained value sent to the client.
                st.session_state[key] = st.session_state[key]
            st.session_state['_rendered_input_keys'].append(key)
            return getattr(st, kind)(label, *args, key=key, **kwargs)

        return render

    def clear(self, *labels):
        """Reset selected inputs before the next render after a successful add."""
        st.session_state.setdefault('_reset_inputs', []).extend(
            self.key(label) for label in labels
        )
