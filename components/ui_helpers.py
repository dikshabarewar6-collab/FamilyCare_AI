"""
Reusable UI helper components and design system elements for FamilyCare AI.
"""
import streamlit as st
from pathlib import Path

CSS_PATH = Path(__file__).resolve().parent.parent / "assets" / "custom.css"

def apply_custom_css():
    """Inject the custom healthcare glassmorphism CSS into the Streamlit session."""
    if CSS_PATH.exists():
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

def render_html(html_str: str):
    """Render HTML safely via st.markdown without triggering markdown code-block indentation."""
    lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    st.markdown("\n".join(lines), unsafe_allow_html=True)

def render_page_header(title: str, subtitle: str, icon: str = "🌸", badge: str = None):
    """Render a styled page header with glassmorphism flair."""
    badge_html = f'<span class="fc-badge completed" style="margin-left:0.75rem; font-size:0.75rem;">{badge}</span>' if badge else ""
    render_html(
        f"""
        <div style="margin-bottom: 1.5rem; padding-bottom: 0.75rem; border-bottom: 1px solid rgba(155, 134, 238, 0.2);">
            <div style="display:flex; align-items:center;">
                <span style="font-size: 2.2rem; margin-right: 0.75rem;">{icon}</span>
                <div>
                    <h1 style="font-size: 2rem; font-weight: 800; margin: 0; color: #0F172A; display:flex; align-items:center;">
                        {title} {badge_html}
                    </h1>
                    <p style="margin: 0.2rem 0 0 0; color: #64748B; font-size: 1rem; font-weight: 400;">
                        {subtitle}
                    </p>
                </div>
            </div>
        </div>
        """
    )

def render_metric_card(label: str, value: str, icon: str, color_class: str = "purple", sublabel: str = None):
    """Render a modern glassmorphic KPI metric card."""
    sublabel_html = f'<div style="font-size:0.75rem; color:#64748B; margin-top:2px;">{sublabel}</div>' if sublabel else ""
    return f"""
    <div class="fc-metric-card">
        <div class="fc-metric-icon {color_class}">
            {icon}
        </div>
        <div style="flex-grow: 1;">
            <div class="fc-metric-label">{label}</div>
            <div class="fc-metric-val">{value}</div>
            {sublabel_html}
        </div>
    </div>
    """

def render_status_badge(status: str) -> str:
    """Return an HTML status badge for check-in or medication statuses."""
    s = (status or "").lower()
    if s in ["checked in", "taken", "completed", "active"]:
        cls = "checked-in"
        icon = "✓"
    elif s in ["awaiting", "awaiting check-in", "pending"]:
        cls = "awaiting"
        icon = "⏳"
    elif s in ["missed", "missed check-in", "overdue", "skipped"]:
        cls = "missed"
        icon = "⚠"
    elif s in ["high"]:
        cls = "priority-high"
        icon = "🔥"
    elif s in ["medium"]:
        cls = "priority-med"
        icon = "⚡"
    elif s in ["low"]:
        cls = "priority-low"
        icon = "🌱"
    else:
        cls = "pending"
        icon = "•"
    return f'<span class="fc-badge {cls}">{icon} {status}</span>'

def render_disclaimer(message: str, title: str = "Medical Notice & Care Disclaimer"):
    """Render a prominent medical & legal disclaimer box."""
    render_html(
        f"""
        <div class="fc-disclaimer">
            <span style="font-size: 1.3rem;">ℹ️</span>
            <div>
                <strong>{title}:</strong> {message}
            </div>
        </div>
        """
    )

def render_ai_badge():
    """Render a prominent 'Powered by Google Gemini' badge."""
    return '<span style="display:inline-flex; align-items:center; gap:6px; background:linear-gradient(135deg, #7052E6 0%, #38BDF8 100%); color:white; padding:4px 12px; border-radius:12px; font-size:0.75rem; font-weight:700; letter-spacing:0.04em;"><span>✨</span> Powered by Google Gemini AI</span>'
