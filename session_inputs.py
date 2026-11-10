"""Keep page inputs in this browser session when Streamlit hides their widgets."""

import streamlit as st


def retain_inputs():
    # Reassigning a widget key detaches it from Streamlit's page-cleanup cycle.
    # Run before rendering any widgets; never retain button/submit state.
    for key in st.session_state.pop('_reset_inputs', []):
        st.session_state.pop(key, None)
    for key in st.session_state.get('_input_keys', []):
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]


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
            return getattr(st, kind)(label, *args, key=key, **kwargs)

        return render

    def clear(self, *labels):
        """Reset selected inputs before the next render after a successful add."""
        st.session_state.setdefault('_reset_inputs', []).extend(
            self.key(label) for label in labels
        )
