"""
Parse HTB profile Nuxt data to extract stats.
Usage: python3 parse_htb.py [profile_url_or_html_file]
"""
import re, json, sys
from datetime import datetime

def extract_nuxt_data(html):
    """Extract the __NUXT_DATA__ JSON from HTB profile HTML."""
    m = re.search(r'<script type="application/json"[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', html)
    if not m:
        return None
    # Nuxt uses a special serialization format with JSON arrays
    raw = m.group(1)
    # The data is a JSON array — parse it
    return json.loads(raw)

def resolve_nuxt_refs(data, refs=None):
    """Resolve Nuxt's reference-heavy JSON format into a plain dict."""
    if refs is None:
        refs = {}
    
    if isinstance(data, list):
        # First element might be a type marker
        if data and isinstance(data[0], str) and data[0] in ('ShallowReactive', 'Reactive', 'Set', 'Map'):
            data = data[1:]
        result = []
        for item in data:
            result.append(resolve_nuxt_refs(item, refs))
        return result
    elif isinstance(data, dict):
        return {k: resolve_nuxt_refs(v, refs) for k, v in data.items()}
    elif isinstance(data, (int, float)):
        return data
    else:
        return data

def main():
    if len(sys.argv) > 1:
        source = sys.argv[1]
        if source.startswith('http'):
            import subprocess
            result = subprocess.run(['curl', '-sS', '-H', 'User-Agent: Mozilla/5.0', source], 
                                  capture_output=True, text=True, timeout=15)
            html = result.stdout
        else:
            with open(source) as f:
                html = f.read()
    else:
        html = sys.stdin.read()

    data = extract_nuxt_data(html)
    if not data:
        print(json.dumps({"error": "No __NUXT_DATA__ found", "streak": 0}))
        return

    # The Nuxt data is in a special format - let's try to find profile info
    # The raw JSON structure has data at specific indices
    result = {"streak": 0, "updated": datetime.utcnow().strftime("%Y-%m-%d")}
    
    # Extract what we can from the HTML
    raw_text = str(data)
    
    # Look for badges to count them
    badge_count = len(re.findall(r'"awarded":true', raw_text))
    result["badges"] = badge_count
    
    # Look for rank
    rank_m = re.search(r'"name":"([^"]+)","description":"Has reached the ([^"]+) rank', raw_text)
    if rank_m:
        result["rank"] = rank_m.group(2)
    
    # Look for full_name
    name_m = re.search(r'"full_name":"([^"]+)"', raw_text)
    if name_m:
        result["name"] = name_m.group(1)
    
    # Try to find streak in HTML — search for any streak-related data
    # The streak might be in the server-rendered HTML, not just the JSON
    streak_m = re.search(r'(\d+)\s*week\s*streak', html, re.IGNORECASE)
    if streak_m:
        result["streak"] = int(streak_m.group(1))
    
    # Also search for "Weekly streak" patterns
    streak_context = re.findall(r'.{0,200}weekly.{0,100}', html, re.IGNORECASE)
    for ctx in streak_context:
        nums = re.findall(r'(\d+)', ctx)
        for n in nums:
            n_int = int(n)
            if 0 <= n_int <= 520:  # reasonable streak range
                if 'week' in ctx.lower() or 'streak' in ctx.lower():
                    result["streak"] = n_int
                    break
    
    # Check if there's a "Weekly Streak:" or similar heading with a number nearby
    streak_num = re.search(r'Weekly Streak[:\s]*(\d+)', html)
    if streak_num:
        result["streak"] = int(streak_num.group(1))
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
