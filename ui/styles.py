CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }

    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }

    .main-header p {
        color: #64748b;
        font-size: 1rem;
    }

    .onboarding-card {
        background: linear-gradient(135deg, #eff6ff, #f5f3ff);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 500px;
        border: 1px solid #e2e8f0;
    }

    .onboarding-card h2 {
        text-align: center;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }

    .onboarding-card p {
        text-align: center;
        color: #64748b;
        margin-bottom: 1.5rem;
    }

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

    .supervisor-badge {
        display: inline-block;
        padding: 0.2rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .supervisor-pass {
        background: #dcfce7;
        color: #166534;
    }

    .supervisor-fail {
        background: #fee2e2;
        color: #991b1b;
    }

    .preference-chip {
        display: inline-block;
        background: #eff6ff;
        color: #2563eb;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.8rem;
        margin: 0.15rem;
        border: 1px solid #bfdbfe;
    }

    .sidebar-section {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }

    .sidebar-section h4 {
        margin: 0 0 0.5rem 0;
        color: #1e293b;
        font-size: 0.9rem;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
    }
</style>
"""
