CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Hide sidebar completely */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* ── Header ── */
    .main-header {
        text-align: center;
        padding: 2.5rem 0 1rem 0;
    }

    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }

    .main-header p {
        color: #94a3b8;
        font-size: 1rem;
        margin: 0;
    }

    /* ── Chat header bar ── */
    .chat-header {
        display: flex;
        align-items: baseline;
        gap: 0.75rem;
        padding: 0.5rem 0;
    }

    .chat-header h1 {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        white-space: nowrap;
    }

    .home-badge {
        font-size: 0.82rem;
        color: #64748b;
        background: #f1f5f9;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        border: 1px solid #e2e8f0;
        white-space: nowrap;
    }

    .chat-divider {
        height: 1px;
        background: #e2e8f0;
        margin: 0.25rem 0 1rem 0;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
    }

    .empty-state p {
        color: #94a3b8;
        font-size: 1rem;
    }

    /* ── Tool trace ── */
    .tool-trace {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }

    .tool-trace-header {
        font-weight: 600;
        color: #7c3aed;
        margin-bottom: 0.25rem;
    }

    .tool-trace-content {
        color: #475569;
        font-family: 'Courier New', monospace;
        font-size: 0.8rem;
        white-space: pre-wrap;
        word-break: break-word;
    }

    /* ── Supervisor badge ── */
    .supervisor-badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-top: 0.35rem;
    }

    .supervisor-pass {
        background: #dcfce7;
        color: #166534;
    }

    .supervisor-fail {
        background: #fee2e2;
        color: #991b1b;
    }

    /* ── Chat messages polish ── */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
    }

    /* ── Button styling ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.55rem 1.5rem;
    }

    .stButton > button[kind="secondary"] {
        border-radius: 10px;
        font-weight: 500;
    }

    /* ── Chat input ── */
    [data-testid="stChatInput"] textarea {
        border-radius: 12px !important;
    }
</style>
"""
