"""Centralized Dark Mode and Light Mode theme definitions for Streamlit.

Author: Akash Das
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ThemeMode(str, Enum):
    """Supported dashboard appearance modes."""

    DARK = "dark"
    LIGHT = "light"


@dataclass(frozen=True)
class ThemePalette:
    """Color tokens for a coherent, accessible dashboard theme."""

    mode: ThemeMode
    plotly_template: str
    app_bg: str
    sidebar_bg: str
    card_bg: str
    card_border: str
    text_primary: str
    text_secondary: str
    accent: str
    accent_hover: str
    button_bg: str
    button_text: str
    primary_button_text: str
    input_bg: str
    input_border: str
    divider_color: str
    tab_bg: str
    tab_active_bg: str
    info_bg: str
    info_border: str
    success_bg: str
    success_border: str
    warning_bg: str
    warning_border: str
    error_bg: str
    error_border: str


DARK_PALETTE = ThemePalette(
    mode=ThemeMode.DARK,
    plotly_template="plotly_dark",
    app_bg="#0b1220",
    sidebar_bg="#111c2d",
    card_bg="#152238",
    card_border="#263854",
    text_primary="#f1f5f9",
    text_secondary="#cbd5e1",
    accent="#38bdf8",
    accent_hover="#0ea5e9",
    button_bg="#1e293b",
    button_text="#f1f5f9",
    primary_button_text="#082f49",
    input_bg="#0f172a",
    input_border="#334155",
    divider_color="#24344d",
    tab_bg="#111c2d",
    tab_active_bg="#1e293b",
    info_bg="rgba(56, 189, 248, 0.14)",
    info_border="#38bdf8",
    success_bg="rgba(34, 197, 94, 0.14)",
    success_border="#22c55e",
    warning_bg="rgba(245, 158, 11, 0.16)",
    warning_border="#f59e0b",
    error_bg="rgba(239, 68, 68, 0.16)",
    error_border="#ef4444",
)

LIGHT_PALETTE = ThemePalette(
    mode=ThemeMode.LIGHT,
    plotly_template="plotly_white",
    app_bg="#f8fafc",
    sidebar_bg="#eef2f7",
    card_bg="#ffffff",
    card_border="#cbd5e1",
    text_primary="#0f172a",
    text_secondary="#334155",
    accent="#0284c7",
    accent_hover="#0369a1",
    button_bg="#ffffff",
    button_text="#0f172a",
    primary_button_text="#ffffff",
    input_bg="#ffffff",
    input_border="#94a3b8",
    divider_color="#cbd5e1",
    tab_bg="#e2e8f0",
    tab_active_bg="#ffffff",
    info_bg="rgba(2, 132, 199, 0.10)",
    info_border="#0284c7",
    success_bg="rgba(22, 163, 74, 0.10)",
    success_border="#16a34a",
    warning_bg="rgba(217, 119, 6, 0.12)",
    warning_border="#d97706",
    error_bg="rgba(220, 38, 38, 0.10)",
    error_border="#dc2626",
)


def get_theme_palette(dark_mode: bool = True) -> ThemePalette:
    """Return the ThemePalette corresponding to the selected appearance mode."""
    return DARK_PALETTE if dark_mode else LIGHT_PALETTE


def build_theme_css(palette: ThemePalette) -> str:
    """Build reusable CSS using theme tokens for native Streamlit components."""
    color_scheme = "dark" if palette.mode == ThemeMode.DARK else "light"
    return f"""
:root {{
    color-scheme: {color_scheme};
    --wx-app-bg: {palette.app_bg};
    --wx-sidebar-bg: {palette.sidebar_bg};
    --wx-card-bg: {palette.card_bg};
    --wx-card-border: {palette.card_border};
    --wx-text-primary: {palette.text_primary};
    --wx-text-secondary: {palette.text_secondary};
    --wx-accent: {palette.accent};
    --wx-accent-hover: {palette.accent_hover};
    --wx-button-bg: {palette.button_bg};
    --wx-button-text: {palette.button_text};
    --wx-primary-btn-text: {palette.primary_button_text};
    --wx-input-bg: {palette.input_bg};
    --wx-input-border: {palette.input_border};
    --wx-info-bg: {palette.info_bg};
    --wx-divider: {palette.divider_color};
}}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {{
    background-color: var(--wx-app-bg) !important;
    color: var(--wx-text-primary) !important;
}}

[data-testid="stHeader"] {{
    background-color: var(--wx-app-bg) !important;
    color: var(--wx-text-primary) !important;
}}

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {{
    background-color: var(--wx-sidebar-bg) !important;
    color: var(--wx-text-primary) !important;
    border-right: 1px solid var(--wx-divider);
}}

.stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp p, .stApp li, .stApp label,
[data-testid="stMarkdownContainer"] {{
    color: var(--wx-text-primary) !important;
}}

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {{
    color: var(--wx-text-secondary) !important;
}}

[data-testid="stMetric"] {{
    background-color: var(--wx-card-bg);
    border: 1px solid var(--wx-card-border);
    border-radius: 0.6rem;
    padding: 0.8rem 1rem;
}}

[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] {{
    color: var(--wx-text-secondary) !important;
}}

[data-testid="stMetricValue"] {{
    color: var(--wx-text-primary) !important;
}}

[data-testid="stForm"] {{
    background-color: var(--wx-card-bg);
    border: 1px solid var(--wx-card-border);
    border-radius: 0.6rem;
    padding: 0.75rem;
}}

[data-testid="stTextInput"] input {{
    background-color: var(--wx-input-bg) !important;
    color: var(--wx-text-primary) !important;
    border: 1px solid var(--wx-input-border) !important;
}}

[data-testid="stSelectbox"] [role="group"] {{
    background-color: var(--wx-input-bg) !important;
    color: var(--wx-text-primary) !important;
    border: 1px solid var(--wx-input-border) !important;
}}

[data-testid="stSelectbox"] [role="group"]:focus-within {{
    border-color: var(--wx-accent) !important;
    box-shadow: 0 0 0 1px var(--wx-accent) !important;
}}

[data-testid="stSelectbox"] input[role="combobox"] {{
    color: var(--wx-text-primary) !important;
    caret-color: var(--wx-text-primary) !important;
}}

[data-testid="stSelectbox"] input[role="combobox"]::placeholder {{
    color: var(--wx-text-secondary) !important;
}}

[data-testid="stSelectbox"] button {{
    background-color: transparent !important;
    border: none !important;
    color: var(--wx-text-primary) !important;
}}

[data-testid="stSelectbox"] svg {{
    color: var(--wx-text-primary) !important;
}}

[data-testid="stSelectbox"] svg path:not([fill="none"]) {{
    fill: currentColor !important;
}}

[data-testid="stSelectboxVirtualDropdown"] {{
    background-color: var(--wx-card-bg) !important;
    color: var(--wx-text-primary) !important;
    border: 1px solid var(--wx-input-border) !important;
}}

[data-testid="stSelectboxVirtualDropdown"] [role="listbox"] {{
    background-color: var(--wx-card-bg) !important;
    color: var(--wx-text-primary) !important;
}}

[data-testid="stSelectboxVirtualDropdown"] [role="option"],
[data-testid="stSelectboxVirtualDropdown"] [role="option"] * {{
    color: var(--wx-text-primary) !important;
}}

[data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"] {{
    background-color: {palette.tab_active_bg} !important;
    font-weight: 600;
}}

[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-hovered] [data-item-hl],
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-focused] [data-item-hl],
[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover {{
    background-color: var(--wx-info-bg) !important;
}}

.stApp code {{
    background-color: var(--wx-card-bg) !important;
    color: var(--wx-text-primary) !important;
    border: 1px solid var(--wx-card-border);
}}

[data-testid="stButton"] button,
[data-testid="stDownloadButton"] button,
[data-testid="stFormSubmitButton"] button {{
    background-color: var(--wx-button-bg) !important;
    color: var(--wx-button-text) !important;
    border: 1px solid var(--wx-card-border) !important;
    border-radius: 0.5rem;
}}

[data-testid="stButton"] button:hover,
[data-testid="stDownloadButton"] button:hover,
[data-testid="stFormSubmitButton"] button:hover {{
    border-color: var(--wx-accent) !important;
}}

[data-testid="stButton"] button[kind="primary"] {{
    background-color: var(--wx-accent) !important;
    color: var(--wx-primary-btn-text) !important;
    border-color: var(--wx-accent) !important;
    font-weight: 600;
}}

[data-testid="stButton"] button[kind="primary"]:hover {{
    background-color: var(--wx-accent-hover) !important;
    border-color: var(--wx-accent-hover) !important;
}}

[data-testid="stTabs"] button[role="tab"] {{
    background-color: {palette.tab_bg};
    color: var(--wx-text-secondary) !important;
    border-radius: 0.4rem 0.4rem 0 0;
    padding: 0.35rem 0.85rem;
}}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
    background-color: {palette.tab_active_bg};
    color: var(--wx-text-primary) !important;
    border-bottom: 2px solid var(--wx-accent) !important;
}}

[data-testid="stDataFrame"],
[data-testid="stTable"] {{
    background-color: var(--wx-card-bg) !important;
    border: 1px solid var(--wx-card-border);
    border-radius: 0.5rem;
    overflow: hidden;
}}

[data-testid="stTable"] table {{
    background-color: var(--wx-card-bg) !important;
    color: var(--wx-text-primary) !important;
}}

[data-testid="stTable"] th {{
    background-color: var(--wx-sidebar-bg) !important;
    color: var(--wx-text-primary) !important;
    border-bottom: 1px solid var(--wx-card-border) !important;
}}

[data-testid="stTable"] td {{
    background-color: var(--wx-card-bg) !important;
    color: var(--wx-text-primary) !important;
    border-bottom: 1px solid var(--wx-divider) !important;
}}

[data-testid="stAlert"],
[data-testid="stAlert"] div[role="alert"],
[data-testid="stAlert"] [data-baseweb="notification"],
[data-testid="stAlertContainer"] {{
    background-color: var(--wx-card-bg) !important;
    border-radius: 0.5rem;
    color: var(--wx-text-primary) !important;
    border: 1px solid var(--wx-card-border) !important;
}}

hr {{
    border-color: var(--wx-divider) !important;
}}
"""
