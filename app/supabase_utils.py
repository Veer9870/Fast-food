import os
from supabase import create_client, Client

_supabase_client = None

def get_supabase_client() -> Client:
    """
    Returns the Supabase client singleton.
    Initialize it if it hasn't been initialized yet.
    """
    global _supabase_client
    
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            # Return None or raise error depending on strictness.
            # For now, we return None if not configured, to allow local dev without Supabase.
            return None
            
        _supabase_client = create_client(url, key)
        
    return _supabase_client
