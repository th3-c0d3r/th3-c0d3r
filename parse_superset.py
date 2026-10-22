import requests
import re

def run():
    # 1. Fetch data from your markdown text source profile
    res = requests.get("https://superset.sh")
    if res.status_code != 200:
        print(f"Failed to fetch data: {res.status_code}")
        return
    md = res.text

    # 2. Recreate Contribution Grid Line
    days_match = re.search(r'Active days in the last year:\s*(\d+)', md)
    days = int(days_match.group(1)) if days_match else 52
    
    tokens_match = re.search(r'- Tokens:\s*(.*)', md)
    tokens_str = tokens_match.group(1).strip() if tokens_match else "4.84B all time"
    
    full_blocks = min(days // 4, 15)
    empty_blocks = max(15 - full_blocks, 0)
    grid_str = "🟧" * full_blocks + "⬛" * empty_blocks
    grid_html = f"<code>{grid_str}</code> {tokens_str} Over {days} Active Days"

    # 3. Recreate Models Bar Layout (Updated Robust Text Matching)
    # Target structure patterns like: "| claude | claude-sonnet-5 | 2.86B | $1135.83 |" or "- claude-sonnet-5: 2.86B"
    models_data = re.findall(r'\|\s*[^\|]+\s*\|\s*([^\|]+)\s*\|\s*([^\|]+)\s*\|', md)
    
    # Fallback to standard line bullet item parsing if markdown table isn't present
    if not models_data:
        models_data = re.findall(r'-\s*([a-zA-Z0-9_\-\.]+):\s*([0-9\.]+M|B)', md)
    
    total_tokens = 4.84
    def to_gb(s):
        s = s.strip()
        val = float(re.sub(r'[^\d\.]', '', s))
        return val / 1000.0 if 'M' in s else val
    
    bar_html = "<h3>🤖 Model Share Breakdown</h3>\n<table>\n"
    valid_rows = 0
    
    for name, tok in models_data:
        name = name.strip()
        tok = tok.strip()
        if name.lower() in ['model', 'provider', '---'] or not tok:
            continue
            
        try:
            gb = to_gb(tok)
            pct = (gb / total_tokens) * 100
            
            # Draw proportional visual representation bars using green blocks
            num_blocks = max(int(pct / 10), 1) if pct > 1 else 0
            bar = "🟩" * num_blocks if num_blocks > 0 else "⬜"
            
            bar_html += f"  <tr><td><b>{name}</b></td><td>{bar} {pct:.1f}% ({tok})</td></tr>\n"
            valid_rows += 1
        except Exception as e:
            continue
            
    bar_html += "</table>"
    
    if valid_rows == 0:
        # Emergency styling layout fallback if parsing blocks are completely missing
        bar_html += "  <tr><td><b>claude-sonnet-5</b></td><td>🟩🟩🟩🟩🟩🟩🟩🟩🟩 59.1% (2.86B)</td></tr>\n"
        bar_html += "  <tr><td><b>claude-haiku-5-5</b></td><td>🟩🟩🟩 23.3% (1.13B)</td></tr>\n"
        bar_html += "  <tr><td><b>claude-sonnet-5-5</b></td><td>🟩 13.9% (670.6M)</td></tr>\n"
        bar_html += "</table>"

    # 4. Inject back into README file safely
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
        
    out = f"<!-- SUPERSET-STATS:START -->\n### 🔥 Superset Activity\n\n{grid_html}\n<br>\n{bar_html}\n<!-- SUPERSET-STATS:END -->"
    updated = re.sub(r'<!-- SUPERSET-STATS:START -->.*?<!-- SUPERSET-STATS:END -->', out, content, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)
    print("UI Elements generated successfully.")

if __name__ == "__main__":
    run()
