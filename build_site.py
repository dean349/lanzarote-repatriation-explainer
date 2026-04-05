import os
import json
import base64
import urllib.request
import urllib.parse
import re
from pathlib import Path

GLOBAL_SKILLS_DIR = r"C:\Users\Dean Harrison\.gemini\antigravity\skills"
LOCAL_SKILLS_DIR = r"c:\DAD\UK_Lanzarote_Repatriation\.agent\skills"

GLOBAL_MCP_FILE = r"C:\Users\Dean Harrison\.gemini\antigravity\mcp_config.json"
LOCAL_MCP_FILE = r"c:\DAD\UK_Lanzarote_Repatriation\.agent\mcp\mcp-config.json"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "REMOVED")
REPO_OWNER = "dean349"
REPO_NAME = "antigravity-capabilities"

def parse_skill_file(path):
    try:
        content = open(path, "r", encoding="utf-8").read()
        match = re.search(r"---(.*?)---", content, re.DOTALL)
        if match:
            yaml_content = match.group(1)
            name_match = re.search(r"name:\s*(.+)", yaml_content)
            desc_match = re.search(r"description:\s*((?:.|\n)*)", yaml_content)
            
            name = name_match.group(1).strip() if name_match else os.path.basename(os.path.dirname(path))
            desc = desc_match.group(1).strip() if desc_match else "No description available."
            return {"name": name, "description": desc}
    except Exception as e:
        print(f"Error reading {path}: {e}")
    return None

def get_skills(dir_path):
    skills = []
    if os.path.exists(dir_path):
        for entry in os.listdir(dir_path):
            full_path = os.path.join(dir_path, entry)
            skill_md = os.path.join(full_path, "SKILL.md")
            if os.path.isdir(full_path) and os.path.exists(skill_md):
                skill = parse_skill_file(skill_md)
                if skill:
                    skills.append(skill)
    return skills

def get_mcp_servers():
    servers = {"global": {}, "local": {}}
    
    if os.path.exists(GLOBAL_MCP_FILE):
        with open(GLOBAL_MCP_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            servers["global"] = data.get("mcpServers", {})
            
    if os.path.exists(LOCAL_MCP_FILE):
        with open(LOCAL_MCP_FILE, 'r', encoding='utf-8') as f:
            # removing comments is tricky in standard json, but the local config has no comments except string tags.
            # wait, the local config IS json, it just has keys starting with _
            # actually it might have trailing commas. Let's try simple parsing.
            content = f.read()
            import ast
            try:
                data = ast.literal_eval(content)
                servers["local"] = data.get("mcpServers", {})
            except:
                try:
                    data = json.loads(content)
                    servers["local"] = data.get("mcpServers", {})
                except Exception as e:
                    print("Error parsing local MCP config", e)
    return servers

def generate_html(global_skills, local_skills, mcp_servers):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity Capabilities | Dean Harrison</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.2);
            --border: #334155;
            --local-accent: #10b981;
        }
        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        header {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 4rem 2rem;
            text-align: center;
            border-bottom: 1px solid var(--border);
        }
        h1 {
            font-size: 3rem;
            margin: 0;
            background: -webkit-linear-gradient(#38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        header p {
            color: var(--text-muted);
            font-size: 1.2rem;
            max-width: 800px;
            margin: 1rem auto;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }
        .section-header {
            font-size: 2rem;
            margin-bottom: 2rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-bottom: 4rem;
        }
        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 25px var(--accent-glow);
            border-color: var(--accent);
        }
        .card.local {
            border-left: 4px solid var(--local-accent);
        }
        .card.global {
            border-left: 4px solid var(--accent);
        }
        .card h3 {
            margin-top: 0;
            font-size: 1.25rem;
            color: var(--text-main);
            display: flex;
            justify-content: space-between;
        }
        .badge {
            font-size: 0.75rem;
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        .badge.global { background: rgba(56, 189, 248, 0.1); color: var(--accent); }
        .badge.local { background: rgba(16, 185, 129, 0.1); color: var(--local-accent); }
        .desc {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }
        pre {
            background: rgba(0,0,0,0.3);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.85rem;
            color: #d1d5db;
        }
    </style>
</head>
<body>

<header>
    <h1>Antigravity Capabilities</h1>
    <p>A comprehensive overview of all global and workspace-scoped skills, agents, and MCP servers actively powering Dean Harrison's environment.</p>
</header>

<div class="container">
    
    <h2 class="section-header">🛠 Local Workspace Skills <span class="badge local">UK Lanzarote Repatriation</span></h2>
    <div class="grid">
"""
    for skill in local_skills:
        html += f"""
        <div class="card local">
            <h3>{skill['name']} <span class="badge local">Local</span></h3>
            <div class="desc">{skill['description']}</div>
        </div>
"""
    
    html += """
    </div>
    
    <h2 class="section-header">🌐 Global Skills (Agent Arsenal)</h2>
    <div class="grid">
"""
    for skill in global_skills:
        html += f"""
        <div class="card global">
            <h3>{skill['name']} <span class="badge global">Global</span></h3>
            <div class="desc">{skill['description']}</div>
        </div>
"""

    html += """
    </div>
    
    <h2 class="section-header">🔌 MCP Servers (Model Context Protocol)</h2>
    <div class="grid">
"""
    for name, config in mcp_servers.get('global', {}).items():
         html += f"""
        <div class="card global">
            <h3>{name} <span class="badge global">Global</span></h3>
            <div class="desc"><strong>Command:</strong> <code>{config.get('command')} {' '.join(config.get('args', []))}</code></div>
        </div>
"""
    for name, config in mcp_servers.get('local', {}).items():
         desc = config.get('_description', '')
         if desc:
            desc_html = f"<div class='desc'>{desc}</div>"
         else:
            desc_html = ""
         html += f"""
        <div class="card local">
            <h3>{name} <span class="badge local">Local</span></h3>
            {desc_html}
            <div class="desc"><strong>Command/URL:</strong> <code>{config.get('command', config.get('type', ''))}</code></div>
        </div>
"""

    html += """
    </div>
</div>

</body>
</html>
"""
    return html

def push_to_github(content):
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/index.html"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "python-script"
    }

    # get sha of existing file
    req = urllib.request.Request(api_url, headers=headers)
    sha = None
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            sha = data['sha']
    except urllib.error.URLError as e:
        print("File doesn't exist yet or error:", e)

    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    payload = {
        "message": "Auto-update Antigravity Capabilities with full skill catalogue",
        "content": encoded_content,
        "branch": "master"
    }
    if sha:
        payload["sha"] = sha
        
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(api_url, data=data, headers=headers, method="PUT")
    
    try:
        with urllib.request.urlopen(req) as response:
            print("Successfully updated index.html on GitHub.")
            return True
    except urllib.error.HTTPError as e:
        print("Failed to update index.html:", e.read().decode('utf-8'))
        return False

if __name__ == "__main__":
    g_skills = get_skills(GLOBAL_SKILLS_DIR)
    l_skills = get_skills(LOCAL_SKILLS_DIR)
    mcp = get_mcp_servers()
    
    html = generate_html(g_skills, l_skills, mcp)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        print("Wrote index.html locally.")
        
    push_to_github(html)
