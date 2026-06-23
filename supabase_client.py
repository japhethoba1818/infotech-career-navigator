"""
supabase_client.py
==================
Single Supabase connection shared across the whole app.
Reads credentials from .streamlit/secrets.toml (local)
or Streamlit Cloud secrets (production).
"""

import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_supabase() -> Client:
    """
    Returns a cached Supabase client.
    Called once — reused for every subsequent request.
    """
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)