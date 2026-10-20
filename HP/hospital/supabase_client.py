from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from django.conf import settings


@dataclass
class SupabaseResult:
    ok: bool
    data: Any = None
    error: str = ''
    table_missing: bool = False


def _table_missing_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return 'does not exist' in text or 'relation' in text and 'does not exist' in text or 'table' in text and 'not found' in text


def get_supabase_client():
    if not settings.SUPABASE_URL:
        return None
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
    if not key:
        return None
    try:
        from supabase import create_client
        return create_client(settings.SUPABASE_URL, key)
    except Exception:
        return None


def safe_select(table: str, query: str = '*', filters: Optional[Dict[str, Any]] = None) -> SupabaseResult:
    client = get_supabase_client()
    if client is None:
        return SupabaseResult(ok=False, data=[], error='Supabase API client not configured')
    try:
        req = client.table(table).select(query)
        for key, value in (filters or {}).items():
            req = req.eq(key, value)
        response = req.execute()
        return SupabaseResult(ok=True, data=response.data)
    except Exception as exc:
        return SupabaseResult(ok=False, data=[], error=str(exc), table_missing=_table_missing_error(exc))


def safe_insert(table: str, payload: Dict[str, Any]) -> SupabaseResult:
    client = get_supabase_client()
    if client is None:
        return SupabaseResult(ok=False, data=None, error='Supabase API client not configured')
    try:
        response = client.table(table).insert(payload).execute()
        return SupabaseResult(ok=True, data=response.data)
    except Exception as exc:
        return SupabaseResult(ok=False, data=None, error=str(exc), table_missing=_table_missing_error(exc))


def safe_update(table: str, payload: Dict[str, Any], filters: Dict[str, Any]) -> SupabaseResult:
    client = get_supabase_client()
    if client is None:
        return SupabaseResult(ok=False, data=None, error='Supabase API client not configured')
    try:
        req = client.table(table).update(payload)
        for key, value in filters.items():
            req = req.eq(key, value)
        response = req.execute()
        return SupabaseResult(ok=True, data=response.data)
    except Exception as exc:
        return SupabaseResult(ok=False, data=None, error=str(exc), table_missing=_table_missing_error(exc))


def safe_delete(table: str, filters: Dict[str, Any]) -> SupabaseResult:
    client = get_supabase_client()
    if client is None:
        return SupabaseResult(ok=False, data=None, error='Supabase API client not configured')
    try:
        req = client.table(table).delete()
        for key, value in filters.items():
            req = req.eq(key, value)
        response = req.execute()
        return SupabaseResult(ok=True, data=response.data)
    except Exception as exc:
        return SupabaseResult(ok=False, data=None, error=str(exc), table_missing=_table_missing_error(exc))
