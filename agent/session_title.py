"""Resolve the current session title without letting a cached hint outrank SQLite."""


def current_session_title(agent) -> str:
    """Use a persisted row (including its empty title); hint only for unpersisted sessions.

    A live agent can outlive a rename made through REST or ``hermes sessions rename``.
    Do not write the DB value back to the hint: it is construction-time context and
    unrelated provider state must change only at a safe session boundary.
    """
    db = getattr(agent, "_session_db", None)
    sid = getattr(agent, "session_id", None)
    if db is not None and sid:
        try:
            title = str(db.get_session_title(sid) or "").strip()
            if title:
                return title
            get_row = getattr(db, "get_session", None)
            if get_row is not None and get_row(sid) is not None:
                return ""  # A persisted clear must not resurrect the old hint.
        except Exception:
            pass
    return str(getattr(agent, "_session_title_hint", "") or "").strip()
