#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

# FLAG FOR LEVEL 3 (Verified and tested)
FLAG = "FLAG{spl1t_fl4g_ch4ll3ng3}"

class CTFHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CTFdpk Arena - Topic 1: Level 3</title>
    <style>
        :root {
            --bg-color: #0f172a; --card-bg: #1e293b; --text-main: #f8fafc;
            --text-muted: #94a3b8; --accent: #3b82f6; --accent-hover: #2563eb;
            --success: #10b981; --danger: #ef4444; --border: #334155;
            /* Part 2: fl4g_ */
        }
        body { font-family: 'Segoe UI', sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 0; line-height: 1.6; }
        header { background-color: var(--card-bg); border-bottom: 1px solid var(--border); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        header h1 { margin: 0; font-size: 1.5rem; color: var(--accent); }
        .container { max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
        .challenge-card { background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 2rem; margin-bottom: 1.5rem; }
        .challenge-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem; }
        .challenge-title { font-size: 1.5rem; margin: 0; }
        .challenge-meta { color: var(--text-muted); font-size: 0.9rem; }
        .description { margin-bottom: 1.5rem; }
        details { background-color: rgba(0,0,0,0.2); border: 1px solid var(--border); border-radius: 6px; margin-bottom: 0.5rem; overflow: hidden; }
        summary { padding: 1rem; cursor: pointer; font-weight: 600; list-style: none; display: flex; justify-content: space-between; align-items: center; }
        summary::-webkit-details-marker { display: none; }
        summary::after { content: '+'; font-size: 1.2rem; color: var(--accent); }
        details[open] summary::after { content: '-'; }
        details[open] summary { border-bottom: 1px solid var(--border); }
        .hint-content { padding: 1rem; color: var(--text-muted); }
        .submit-section { display: flex; gap: 1rem; margin-top: 2rem; }
        input[type="text"] { flex: 1; padding: 0.75rem; background-color: var(--bg-color); border: 1px solid var(--border); border-radius: 6px; color: var(--text-main); font-size: 1rem; }
        input[type="text"]:focus { outline: 2px solid var(--accent); border-color: transparent; }
        button { padding: 0.75rem 1.5rem; background-color: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 1rem; }
        button:hover { background-color: var(--accent-hover); }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: var(--card-bg); padding: 2rem; border-radius: 8px; text-align: center; max-width: 400px; border: 1px solid var(--border); }
        .modal.success { border-top: 4px solid var(--success); }
        .modal.error { border-top: 4px solid var(--danger); }
    </style>
</head>
<body>
    <header>
        <h1>CTFdpk Arena</h1>
        <div class="user">Logged in as: <strong>Guest</strong></div>
    </header>

    <div class="container">
        <!-- data-part1="FLAG{spl1t_" -->
        <div class="challenge-card">
            <div class="challenge-header">
                <div>
                    <h2 class="challenge-title">Topic 1: View Source - Level 3</h2>
                    <div class="challenge-meta">Category: Web Exploitation | Difficulty: Medium</div>
                </div>
            </div>

            <div class="description">
                <p>Impressive work on Level 2, agent. But the developers have escalated their game.</p>
                <p>They've split the flag into multiple pieces and scattered them throughout the source code. No single location contains the complete flag.</p>
                <p><strong>Your Objective:</strong> Find all the flag fragments and assemble them in the correct order. Format: <code>FLAG{...}</code></p>
            </div>

            <div class="hints-section">
                <h3 style="color: var(--accent); margin-bottom: 1rem;">💡 Need Help? (Hints)</h3>
                <details>
                    <summary>Hint 1</summary>
                    <div class="hint-content">The flag is split into 4 parts. Each part is hidden in a different location in the source code.</div>
                </details>
                <details>
                    <summary>Hint 2</summary>
                    <div class="hint-content">Look for HTML attributes (like <code>data-*</code>), CSS comments (<code>/* */</code>), JavaScript variables, and HTML comments (<code>&lt;!-- --&gt;</code>).</div>
                </details>
                <details>
                    <summary>Hint 3</summary>
                    <div class="hint-content">The parts are labeled "Part 1", "Part 2", "Part 3", "Part 4". Find them all and concatenate in order.</div>
                </details>
            </div>

            <div class="submit-section">
                <input type="text" id="flag-input" placeholder="Enter complete flag here (e.g., FLAG{...})">
                <button id="submit-btn">Submit Flag</button>
            </div>
        </div>
    </div>

    <div id="result-modal" class="modal">
        <div id="modal-content" class="modal-content">
            <h2 id="modal-title"></h2>
            <p id="modal-message"></p>
            <button onclick="document.getElementById('result-modal').style.display='none'">Close</button>
        </div>
    </div>

    <script>
        var part3 = "ch4ll";
        var debug_info = "System initialized";
        
        document.getElementById('submit-btn').addEventListener('click', async () => {
            const flag = document.getElementById('flag-input').value.trim();
            if (!flag) return;
            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ flag: flag })
                });
                const data = await response.json();
                const modal = document.getElementById('result-modal');
                const content = document.getElementById('modal-content');
                modal.style.display = 'flex';
                if (data.success) {
                    content.className = 'modal-content success';
                    document.getElementById('modal-title').innerText = '🎉 Correct!';
                    document.getElementById('modal-message').innerText = data.message;
                } else {
                    content.className = 'modal-content error';
                    document.getElementById('modal-title').innerText = '❌ Incorrect';
                    document.getElementById('modal-message').innerText = data.message;
                }
            } catch (error) { alert('Error submitting flag.'); }
        });
    </script>
    
    <!-- Part 4: 3ng3} -->
</body>
</html>
"""
            self.wfile.write(html_content.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                submitted_flag = data.get('flag', '')
                if submitted_flag == FLAG:
                    response = {"success": True, "message": "Level 3 Cleared! Excellent detective work!"}
                else:
                    response = {"success": False, "message": "Incorrect flag. Did you find all 4 parts and put them in the right order?"}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[SERVER LOG] {format % args}")

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CTFHandler)
    print("=" * 50)
    print(" CTFdpk Arena - Topic 1, Level 3 Started!")
    print(" Open: http://localhost:8000")
    print("=" * 50)
    httpd.serve_forever()
