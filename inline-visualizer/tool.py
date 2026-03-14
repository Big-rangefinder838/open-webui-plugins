"""
title: Inline Visualizer
author: Classic298
version: 1.1.0
description: Renders interactive HTML/SVG visualizations inline in chat. For design system instructions, the model should call view_skill("visualize").
"""

from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse


# ---------------------------------------------------------------------------
# Injected CSS — Theme variables (light default, dark via data-theme)
# ---------------------------------------------------------------------------

THEME_CSS = """
:root {
  --color-text-primary: #1F2937;
  --color-text-secondary: #6B7280;
  --color-text-tertiary: #9CA3AF;
  --color-text-info: #2563EB;
  --color-text-success: #059669;
  --color-text-warning: #D97706;
  --color-text-danger: #DC2626;
  --color-bg-primary: #FFFFFF;
  --color-bg-secondary: #F9FAFB;
  --color-bg-tertiary: #F3F4F6;
  --color-border-tertiary: rgba(0,0,0,0.15);
  --color-border-secondary: rgba(0,0,0,0.3);
  --color-border-primary: rgba(0,0,0,0.4);
  --font-sans: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'SF Mono', Menlo, Consolas, monospace;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  /* --- Color ramp variables (light) --- */
  --ramp-purple-fill:#EEEDFE; --ramp-purple-stroke:#534AB7; --ramp-purple-th:#3C3489; --ramp-purple-ts:#534AB7;
  --ramp-teal-fill:#E1F5EE;   --ramp-teal-stroke:#0F6E56;   --ramp-teal-th:#085041;   --ramp-teal-ts:#0F6E56;
  --ramp-coral-fill:#FAECE7;  --ramp-coral-stroke:#993C1D;  --ramp-coral-th:#712B13;  --ramp-coral-ts:#993C1D;
  --ramp-pink-fill:#FBEAF0;   --ramp-pink-stroke:#993556;   --ramp-pink-th:#72243E;   --ramp-pink-ts:#993556;
  --ramp-gray-fill:#F1EFE8;   --ramp-gray-stroke:#5F5E5A;   --ramp-gray-th:#444441;   --ramp-gray-ts:#5F5E5A;
  --ramp-blue-fill:#E6F1FB;   --ramp-blue-stroke:#185FA5;   --ramp-blue-th:#0C447C;   --ramp-blue-ts:#185FA5;
  --ramp-green-fill:#EAF3DE;  --ramp-green-stroke:#3B6D11;  --ramp-green-th:#27500A;  --ramp-green-ts:#3B6D11;
  --ramp-amber-fill:#FAEEDA;  --ramp-amber-stroke:#854F0B;  --ramp-amber-th:#633806;  --ramp-amber-ts:#854F0B;
  --ramp-red-fill:#FCEBEB;    --ramp-red-stroke:#A32D2D;    --ramp-red-th:#791F1F;    --ramp-red-ts:#A32D2D;
}
:root[data-theme="dark"] {
  --color-text-primary: #E5E7EB;
  --color-text-secondary: #9CA3AF;
  --color-text-tertiary: #6B7280;
  --color-text-info: #60A5FA;
  --color-text-success: #34D399;
  --color-text-warning: #FBBF24;
  --color-text-danger: #F87171;
  --color-bg-primary: #1A1A1A;
  --color-bg-secondary: #262626;
  --color-bg-tertiary: #111111;
  --color-border-tertiary: rgba(255,255,255,0.15);
  --color-border-secondary: rgba(255,255,255,0.3);
  --color-border-primary: rgba(255,255,255,0.4);
  --ramp-purple-fill:#3C3489; --ramp-purple-stroke:#AFA9EC; --ramp-purple-th:#CECBF6; --ramp-purple-ts:#AFA9EC;
  --ramp-teal-fill:#085041;   --ramp-teal-stroke:#5DCAA5;   --ramp-teal-th:#9FE1CB;   --ramp-teal-ts:#5DCAA5;
  --ramp-coral-fill:#712B13;  --ramp-coral-stroke:#F0997B;  --ramp-coral-th:#F5C4B3;  --ramp-coral-ts:#F0997B;
  --ramp-pink-fill:#72243E;   --ramp-pink-stroke:#ED93B1;   --ramp-pink-th:#F4C0D1;   --ramp-pink-ts:#ED93B1;
  --ramp-gray-fill:#444441;   --ramp-gray-stroke:#B4B2A9;   --ramp-gray-th:#D3D1C7;   --ramp-gray-ts:#B4B2A9;
  --ramp-blue-fill:#0C447C;   --ramp-blue-stroke:#85B7EB;   --ramp-blue-th:#B5D4F4;   --ramp-blue-ts:#85B7EB;
  --ramp-green-fill:#27500A;  --ramp-green-stroke:#97C459;  --ramp-green-th:#C0DD97;  --ramp-green-ts:#97C459;
  --ramp-amber-fill:#633806;  --ramp-amber-stroke:#EF9F27;  --ramp-amber-th:#FAC775;  --ramp-amber-ts:#EF9F27;
  --ramp-red-fill:#791F1F;    --ramp-red-stroke:#F09595;    --ramp-red-th:#F7C1C1;    --ramp-red-ts:#F09595;
}
"""

# ---------------------------------------------------------------------------
# Injected CSS — SVG utility classes + color ramp selectors
# ---------------------------------------------------------------------------

SVG_CLASSES = """
/* --- Text --- */
.t  { font: 400 14px/1.4 var(--font-sans); fill: var(--color-text-primary); }
.ts { font: 400 12px/1.4 var(--font-sans); fill: var(--color-text-secondary); }
.th { font: 500 14px/1.4 var(--font-sans); fill: var(--color-text-primary); }

/* --- Shapes --- */
.box    { fill: var(--color-bg-secondary); stroke: var(--color-border-tertiary); stroke-width: 0.5; }
.node   { cursor: pointer; }
.node:hover { opacity: 0.85; }
.arr    { stroke: var(--color-border-secondary); stroke-width: 1.5; fill: none; }
.leader { stroke: var(--color-text-tertiary); stroke-width: 0.5; stroke-dasharray: 3 2; fill: none; }

/* --- Color ramp selectors (fill/stroke adapt via CSS vars) --- */
.c-purple>rect,.c-purple>circle,.c-purple>ellipse{fill:var(--ramp-purple-fill);stroke:var(--ramp-purple-stroke);stroke-width:.5}
.c-purple>.th{fill:var(--ramp-purple-th)} .c-purple>.ts{fill:var(--ramp-purple-ts)}
.c-teal>rect,.c-teal>circle,.c-teal>ellipse{fill:var(--ramp-teal-fill);stroke:var(--ramp-teal-stroke);stroke-width:.5}
.c-teal>.th{fill:var(--ramp-teal-th)} .c-teal>.ts{fill:var(--ramp-teal-ts)}
.c-coral>rect,.c-coral>circle,.c-coral>ellipse{fill:var(--ramp-coral-fill);stroke:var(--ramp-coral-stroke);stroke-width:.5}
.c-coral>.th{fill:var(--ramp-coral-th)} .c-coral>.ts{fill:var(--ramp-coral-ts)}
.c-pink>rect,.c-pink>circle,.c-pink>ellipse{fill:var(--ramp-pink-fill);stroke:var(--ramp-pink-stroke);stroke-width:.5}
.c-pink>.th{fill:var(--ramp-pink-th)} .c-pink>.ts{fill:var(--ramp-pink-ts)}
.c-gray>rect,.c-gray>circle,.c-gray>ellipse{fill:var(--ramp-gray-fill);stroke:var(--ramp-gray-stroke);stroke-width:.5}
.c-gray>.th{fill:var(--ramp-gray-th)} .c-gray>.ts{fill:var(--ramp-gray-ts)}
.c-blue>rect,.c-blue>circle,.c-blue>ellipse{fill:var(--ramp-blue-fill);stroke:var(--ramp-blue-stroke);stroke-width:.5}
.c-blue>.th{fill:var(--ramp-blue-th)} .c-blue>.ts{fill:var(--ramp-blue-ts)}
.c-green>rect,.c-green>circle,.c-green>ellipse{fill:var(--ramp-green-fill);stroke:var(--ramp-green-stroke);stroke-width:.5}
.c-green>.th{fill:var(--ramp-green-th)} .c-green>.ts{fill:var(--ramp-green-ts)}
.c-amber>rect,.c-amber>circle,.c-amber>ellipse{fill:var(--ramp-amber-fill);stroke:var(--ramp-amber-stroke);stroke-width:.5}
.c-amber>.th{fill:var(--ramp-amber-th)} .c-amber>.ts{fill:var(--ramp-amber-ts)}
.c-red>rect,.c-red>circle,.c-red>ellipse{fill:var(--ramp-red-fill);stroke:var(--ramp-red-stroke);stroke-width:.5}
.c-red>.th{fill:var(--ramp-red-th)} .c-red>.ts{fill:var(--ramp-red-ts)}
"""

# ---------------------------------------------------------------------------
# Injected CSS — Base resets & interactive element styles
# ---------------------------------------------------------------------------

BASE_STYLES = """
* { box-sizing: border-box; margin: 0; font-family: var(--font-sans); }
html, body { overflow: hidden; }
body { background: transparent; color: var(--color-text-primary); line-height: 1.5; padding: 8px; }
h1 { font-size: 22px; font-weight: 500; color: var(--color-text-primary); margin-bottom: 12px; }
h2 { font-size: 18px; font-weight: 500; color: var(--color-text-primary); margin-bottom: 8px; }
h3 { font-size: 16px; font-weight: 500; color: var(--color-text-primary); margin-bottom: 6px; }
p  { font-size: 14px; color: var(--color-text-secondary); margin-bottom: 8px; }
button {
  background: transparent; border: 0.5px solid var(--color-border-secondary);
  border-radius: var(--radius-md); padding: 6px 14px; font-size: 13px;
  color: var(--color-text-primary); cursor: pointer; font-family: var(--font-sans);
}
button:hover { background: var(--color-bg-secondary); }
button.active { background: var(--color-bg-secondary); border-color: var(--color-border-primary); }
input[type="range"] {
  -webkit-appearance: none; width: 100%; height: 4px;
  background: var(--color-border-tertiary); border-radius: 2px; outline: none;
}
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none; width: 18px; height: 18px; border-radius: 50%;
  background: var(--color-bg-primary); border: 0.5px solid var(--color-border-secondary); cursor: pointer;
}
select {
  background: var(--color-bg-secondary); border: 0.5px solid var(--color-border-tertiary);
  border-radius: var(--radius-md); padding: 6px 10px; font-size: 13px;
  color: var(--color-text-primary); font-family: var(--font-sans);
}
code {
  font-family: var(--font-mono); font-size: 13px; background: var(--color-bg-tertiary);
  padding: 2px 6px; border-radius: 4px;
}
"""

# ---------------------------------------------------------------------------
# Injected JavaScript — theme detection, height reporting, bridges
# ---------------------------------------------------------------------------

INJECTED_SCRIPTS = """
<script>
// --- Theme detection ---
(function() {
  try {
    var p = parent.document.documentElement;
    var isDark = p.classList.contains('dark')
      || p.getAttribute('data-theme') === 'dark'
      || getComputedStyle(p).colorScheme === 'dark';
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  } catch(e) {
    // allowSameOrigin not enabled — fall back to OS preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  }
})();

// --- Height reporting ---
function reportHeight() {
  // Temporarily collapse body so scrollHeight reflects actual content,
  // not the iframe's previously set height (fixes shrink-on-collapse).
  var b = document.body;
  b.style.height = '0';
  var h = b.scrollHeight;
  b.style.height = '';
  parent.postMessage({ type: 'iframe:height', height: h }, '*');
}
window.addEventListener('load', reportHeight);
window.addEventListener('resize', reportHeight);
new ResizeObserver(reportHeight).observe(document.body);
// Explicitly handle <details> toggle — ResizeObserver misses this in some browsers
document.addEventListener('toggle', function() {
  setTimeout(reportHeight, 50);
}, true);

// --- sendPrompt bridge (requires iframe Sandbox Allow Same Origin) ---
function sendPrompt(text) {
  try {
    // Use Open WebUI's native postMessage protocol.
    // submitPrompt automatically queues the message if the AI is still generating.
    parent.postMessage({ type: 'input:prompt:submit', text: text }, '*');
  } catch(e) { /* iframe sandbox restriction */ }
}

// --- Open link in parent window ---
function openLink(url) {
  try { parent.window.open(url, '_blank'); }
  catch(e) { window.open(url, '_blank'); }
}
</script>
"""


def _build_html(content: str) -> str:
    """Wrap a user-provided HTML/SVG fragment in the full Rich UI shell."""
    return (
        "<!DOCTYPE html><html><head>"
        f"<style>{THEME_CSS}\n{SVG_CLASSES}\n{BASE_STYLES}</style>"
        f"</head><body>\n{content}\n{INJECTED_SCRIPTS}</body></html>"
    )


class Tools:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    def render_visualization(
        self,
        html_code: str,
        title: str = "Visualization",
    ) -> HTMLResponse:
        """
        Render an interactive HTML or SVG visualization inline in the chat.

        IMPORTANT: You MUST call view_skill("visualize") FIRST to load the design system
        before calling this tool. Never generate a visualization without reading the skill
        instructions first — they contain critical rules for colors, layout, SVG setup,
        chart patterns, and common failure points.

        The system automatically injects:
        - Theme CSS variables (auto-detected light/dark mode)
        - SVG utility classes: .t .ts .th .box .node .arr .leader
        - Color ramp classes: .c-purple .c-teal .c-coral .c-pink .c-gray .c-blue .c-green .c-amber .c-red
        - Base element styles (button, range, select, code, headings)
        - Height auto-sizing script
        - sendPrompt(text) function — sends a message to the chat (requires iframe Sandbox Allow Same Origin)
        - openLink(url) function — opens a URL in a new tab

        :param html_code: HTML or SVG content fragment. Do NOT include DOCTYPE, html, head, or body tags.
                          Structure: <style> first (prefer inline styles), visible content next, <script> last.
                          For charts, load Chart.js via <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>.
                          For complex visualizations, load D3 via <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>.
        :param title: Short descriptive title for the visualization.
        :return: Interactive rich embed rendered in the chat.
        """
        return HTMLResponse(
            content=_build_html(html_code),
            headers={"Content-Disposition": "inline"},
        )
