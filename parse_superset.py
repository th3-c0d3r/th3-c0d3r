import requests
import re

def run():
    # 1. Fetching the raw structured markdown metadata endpoint directly
    res = requests.get("https://superset.sh")
    if res.status_code != 200:
        print(f"Failed to fetch data: {res.status_code}")
        return
    md = res.text

    # 2. Recreate Contribution Grid Line
    days_match = re.search(r'last year:\s*(\d+)', md)
    days = int(days_match.group(1)) if days_match else 52
    
    tokens_match = re.search(r'- Tokens:\s*(.*)', md)
    tokens_str = tokens_match.group(1).strip() if tokens_match else "4.84B all time"
    
    full_blocks = min(days // 4, 15)
    empty_blocks = max(15 - full_blocks, 0)
    grid_str = "🟧" * full_blocks + "⬛" * empty_blocks
    grid_html = f"<code>{grid_str}</code> {tokens_str} Over {days} Active Days"

    # 3. Recreate Models Bar Layout
    models_data = re.findall(r'\|\s*([a-zA-Z0-9_\-\.]+)\s*\|\s*([a-zA-Z0-9_\-\.]+)\s*\|\s*([0-9\.]+M|B)', md)
    total_tokens = 4840.0
    
    def to_mb(s):
        v = float(re.sub(r'[MB]', '', s))
        return v * 1000 if 'B' in s else v
    
    bar_html = "<h3>🤖 Model Share Breakdown</h3>\n<table>\n"
    for prov, name, tok in models_data:
        mb = to_mb(tok)
        pct = (mb / total_tokens) * 100
        width = max(int(pct * 2), 2)
        bar = "🟩" * (width // 10) if width >= 10 else "🟩"
        if pct > 0.5:
            bar_html += f"  <tr><td><b>{name}</b></td><td>{bar} {pct:.1f}% ({tok})</td></tr>\n"
    bar_html += "</table>"

    # 4. Inject back into README file safely
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
        
    out = f"<!-- SUPERSET-STATS:START -->\n<h3>🔥 Superset Activity</h3>\n{grid_html}\n<br><br>\n{bar_html}\n<!-- SUPERSET-STATS:END -->"
    updated = re.sub(r'<!-- SUPERSET-STATS:START -->.*?<!-- SUPERSET-STATS:END -->', out, content, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)
    print("README parsed and updated successfully.")

if __name__ == "__main__":
    run()
