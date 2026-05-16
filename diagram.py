import re
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from diagram_prompt import DIAGRAM_SYSTEM_PROMPT

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("GROQ_API_KEY is not set in your .env file.")

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _slugify(text: str) -> str:
    """Convert a string to a valid Mermaid node ID (camelCase, no spaces)."""
    words = re.sub(r"[^a-zA-Z0-9\s]", "", text).split()
    return (
        words[0].lower() + "".join(w.capitalize() for w in words[1:])
        if words
        else "node"
    )


def _strip_fences(raw: str) -> str:
    """Remove accidental markdown code fences the LLM adds."""
    raw = re.sub(r"^```(?:mermaid)?\n?", "", raw.strip(), flags=re.IGNORECASE)
    raw = re.sub(r"\n?```$", "", raw)
    return raw.strip()


def fix_mermaid_syntax(code: str) -> str:
    """Fix common Mermaid v10 syntax errors produced by LLMs."""
    lines = code.split("\n")
    fixed = []

    for line in lines:
        # Fix 1: bad arrow  -->|--> or -->|-->
        line = re.sub(r"-->\|-->", "-->", line)
        line = re.sub(r"-->\|[-]+>", "-->", line)

        # Fix 2: bad async arrow variants
        line = re.sub(r"-\.->.*?->", "-.->", line)

        # Fix 3: subgraph "string" ["Title"]  →  subgraph slugID ["Title"]
        line = re.sub(
            r'subgraph\s+"([^"]+)"\s+\["([^"]+)"\]',
            lambda m: f'subgraph {_slugify(m.group(1))} ["{m.group(2)}"]',
            line,
        )

        # Fix 4: subgraph ID [Title without quotes]  →  subgraph ID ["Title"]
        line = re.sub(
            r'subgraph\s+(\w+)\s+\[([^\]"]+)\]',
            r'subgraph \1 ["\2"]',
            line,
        )

        # Fix 5: node labels with spaces, not quoted  →  ["label"]
        line = re.sub(r'\[(?!")([^\]<>]+\s[^\]<>]+)(?<!")\]', r'["\1"]', line)

        # Fix 6: strip double-wrapping  ["\"label\""]  →  ["label"]
        line = re.sub(r'\["\\?"([^"]+)\\?"\]', r'["\1"]', line)

        fixed.append(line)

    result = "\n".join(fixed)

    # Fix 7: deduplicate node label definitions (same ID defined multiple times)
    seen_ids: dict = {}
    deduped = []
    for line in result.split("\n"):
        node_def = re.match(r'^\s{4}(\w+)\["([^"]+)"\]', line)
        if node_def:
            node_id, label = node_def.group(1), node_def.group(2)
            if node_id in seen_ids:
                line = line.replace(f'{node_id}["{label}"]', node_id)
            else:
                seen_ids[node_id] = label
        deduped.append(line)

    return "\n".join(deduped)


# ── Public API ─────────────────────────────────────────────────────────────────


def generate_mermaid(user_input: str, app_type: str, architecture_response: str) -> str:
    """Call the LLM and return cleaned, validated Mermaid diagram code."""
    try:
        messages = [
            SystemMessage(content=DIAGRAM_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"App Type: {app_type}\n\n"
                    f"User Idea: {user_input}\n\n"
                    f"Architecture Summary:\n{architecture_response[:1500]}\n\n"
                    "Generate the Mermaid system diagram now."
                )
            ),
        ]
        response = llm.invoke(messages)
        raw = _strip_fences(response.content)
        return fix_mermaid_syntax(raw)

    except Exception as e:
        return f'flowchart TD\n    error["Error: {str(e)}"]'


def ai_edit_diagram(current_mermaid: str, instruction: str) -> str:
    """Apply a natural-language edit instruction to an existing Mermaid diagram."""
    try:
        messages = [
            SystemMessage(content=AI_EDIT_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Current diagram:\n\n{current_mermaid}\n\n"
                    f"Instruction: {instruction}\n\n"
                    "Output the updated Mermaid code only."
                )
            ),
        ]
        response = llm.invoke(messages)
        raw = _strip_fences(response.content)
        return fix_mermaid_syntax(raw)

    except Exception as e:
        return current_mermaid  # fall back to original on error


def mermaid_to_html(mermaid_code: str) -> str:
    """Wrap Mermaid code in a self-contained HTML page for st.components.v1.html."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: sans-serif;
    background: #ffffff;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px;
    min-height: 100vh;
  }}
  #diagram {{
    width: 100%;
    max-width: 900px;
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }}
  #error-box {{
    display: none;
    background: #fff0f0;
    border: 1px solid #ffcccc;
    border-radius: 8px;
    padding: 12px 16px;
    color: #cc0000;
    font-size: 13px;
    width: 100%;
    max-width: 900px;
    margin-top: 12px;
    white-space: pre-wrap;
  }}
  #raw-toggle {{
    margin-top: 12px;
    font-size: 12px;
    color: #666;
    cursor: pointer;
    text-decoration: underline;
    background: none;
    border: none;
  }}
  #raw-box {{
    display: none;
    margin-top: 8px;
    background: #f6f8fa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 12px;
    font-family: monospace;
    font-size: 12px;
    white-space: pre-wrap;
    width: 100%;
    max-width: 900px;
    color: #333;
  }}
</style>
</head>
<body>
<div id="diagram">
  <div class="mermaid">
{mermaid_code}
  </div>
</div>
<div id="error-box"></div>
<button id="raw-toggle" onclick="toggleRaw()">show raw Mermaid code</button>
<pre id="raw-box">{mermaid_code}</pre>

<script>
  mermaid.initialize({{
    startOnLoad: false,
    theme: 'default',
    flowchart: {{ curve: 'basis', padding: 20 }},
    securityLevel: 'loose'
  }});

  mermaid.run({{
    nodes: document.querySelectorAll('.mermaid'),
    suppressErrors: false,
  }}).catch(function(err) {{
    document.getElementById('error-box').style.display = 'block';
    document.getElementById('error-box').textContent = 'Render error: ' + err.message + '\\n\\nCheck the raw code below for syntax issues.';
    document.getElementById('raw-box').style.display = 'block';
    document.getElementById('raw-toggle').textContent = 'hide raw Mermaid code';
  }});

  function toggleRaw() {{
    const box = document.getElementById('raw-box');
    const btn = document.getElementById('raw-toggle');
    if (box.style.display === 'none') {{
      box.style.display = 'block';
      btn.textContent = 'hide raw Mermaid code';
    }} else {{
      box.style.display = 'none';
      btn.textContent = 'show raw Mermaid code';
    }}
  }}
</script>
</body>
</html>"""


# ── AI edit prompt (kept here, close to its function) ─────────────────────────

AI_EDIT_SYSTEM_PROMPT = """
You are a Mermaid diagram editor.

The user will give you an existing Mermaid diagram and an instruction to modify it.

RULES:
1. Output ONLY the updated raw Mermaid code — no markdown fences, no explanation.
2. Preserve the existing structure unless the instruction changes it.
3. Keep node IDs stable — only change labels, do not shuffle IDs.
4. ALL node labels containing spaces MUST be double-quoted:
   CORRECT:  A["Web App"] --> B["Login Page"]
   WRONG:    A[Web App] --> B[Login Page]
5. Subgraph titles with spaces must be quoted:
   CORRECT:  subgraph client ["Client Layer"]
   WRONG:    subgraph client [Client Layer]
6. ONLY use these arrow forms:
   -->     -.->     ==>     -->|"label"|
   NEVER:  -->|-->  or any hybrid
7. Define each node label only once — reuse the bare ID on subsequent edges.
8. Start with: flowchart TD
"""
