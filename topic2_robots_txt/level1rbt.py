from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

FLAG = "FLAG{r0b0ts_txt_1s_n0t_s3cur3}"

ROBOTS_TXT_CONTENT = """User-agent: *
Disallow: /admin/
Disallow: /classified-area/
"""

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
    <title>CTFdpk Arena - Topic 2: Level 1</title>
    <style>
        :root { --bg-color: #0f172a; --card-bg: #1e293b; --text-main: #f8fafc; --text-muted: #94a3b8; --accent: #3b82f6; --accent-hover: #2563eb; --success: #10b981; --danger: #ef4444; --border: #334155; }
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
    <header><h1>CTFdpk Arena</h1><div class="user">Logged in as: <strong>Guest</strong></div></header>
    <div class="container">
        <div class="challenge-card">
            <div class="challenge-header">
                <div><h2 class="challenge-title">Topic 2: Information Disclosure - Level 1</h2><div class="challenge-meta">Category: Robots.txt | Difficulty: Easy</div></div>
            </div>
            <div class="description">
                <p>Welcome to Topic 2, agent. In this topic, we will look at how websites communicate with search engines.</p>
                <p>Webmasters often leave a specific file at the root of their server to tell crawlers (like Googlebot) which pages they should not visit. However, this file is public.</p>
                <p><strong>Your Objective:</strong> Find the hidden directory that the webmaster tried to hide from search engines, and retrieve the flag. Format: <code>FLAG{...}</code></p>
            </div>
            <div class="hints-section">
                <h3 style="color: var(--accent); margin-bottom: 1rem;">Need Help? (Hints)</h3>
                <details><summary>Hint 1</summary><div class="hint-content">There is a standard file that lives at the root of almost every website, named after a famous 1990s protocol for excluding robots.</div></details>
                <details><summary>Hint 2</summary><div class="hint-content">Read the file carefully. It contains a <code>Disallow</code> rule pointing to a specific path. Visit that path to find the flag.</div></details>
            </div>
            <div class="submit-section">
                <input type="text" id="flag-input" placeholder="Enter flag here (e.g., FLAG{...})">
                <button id="submit-btn">Submit Flag</button>
            </div>
        </div>
    </div>
    <div id="result-modal" class="modal"><div id="modal-content" class="modal-content"><h2 id="modal-title"></h2><p id="modal-message"></p><button onclick="document.getElementById('result-modal').style.display='none'">Close</button></div></div>
    <script>
        document.getElementById('submit-btn').addEventListener('click', async () => {
            const flag = document.getElementById('flag-input').value.trim();
            if (!flag) return;
            try {
                const response = await fetch('/submit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ flag: flag }) });
                const data = await response.json();
                const modal = document.getElementById('result-modal');
                const content = document.getElementById('modal-content');
                modal.style.display = 'flex';
                if (data.success) { content.className = 'modal-content success'; document.getElementById('modal-title').innerText = 'Correct!'; document.getElementById('modal-message').innerText = data.message; }
                else { content.className = 'modal-content error'; document.getElementById('modal-title').innerText = 'Incorrect'; document.getElementById('modal-message').innerText = data.message; }
            } catch (error) { alert('Error submitting flag.'); }
        });
    </script>
</body>
</html>
"""
            self.wfile.write(html_content.encode())
            
        elif parsed_path.path == '/robots.txt':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(ROBOTS_TXT_CONTENT.encode())
            
        elif parsed_path.path == '/classified-area/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<h1>Classified Area</h1><p>Flag: {FLAG}</p>".encode())
            
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
                    response = {"success": True, "message": "Level 1 Cleared! Ready for Level 2?"}
                else:
                    response = {"success": False, "message": "Incorrect flag. Try again!"}
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
    print("CTFdpk Arena - Topic 2, Level 1 Started!")
    print("Open: http://localhost:8000")
    print("=" * 50)
    httpd.serve_forever()
