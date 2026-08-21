from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

FLAG = "FLAG{d0m_m4n1pul4t10n_m4st3r}"

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
    <title>CTFdpk Arena - Topic 1: Level 5</title>
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
                <div><h2 class="challenge-title">Topic 1: View Source - Level 5</h2><div class="challenge-meta">Category: Web Exploitation | Difficulty: Hard (DOM Manipulation)</div></div>
            </div>
            <div class="description">
                <p>Welcome to the final boss of Topic 1, agent. You have learned how to read the source code. Now, it is time to <strong>control</strong> it.</p>
                <p>The developers built a "Secret Admin Console" to store the flag. They didn't just hide it in the code; they used advanced CSS techniques to make it invisible and unreadable to regular users.</p>
                <p><strong>Your Objective:</strong> The flag is rendered in the DOM, but you cannot see it. Use your browser's Developer Tools (Inspector) to manipulate the page and reveal the flag. Format: <code>FLAG{...}</code></p>
                <p style="color: var(--danger);"><em>Hint: You cannot solve this just by reading. You must edit the live page in your browser.</em></p>
            </div>
            <div class="hints-section">
                <h3 style="color: var(--accent); margin-bottom: 1rem;">Need Help? (Hints)</h3>
                <details><summary>Hint 1</summary><div class="hint-content">The Admin Console exists in the HTML, but it has a CSS rule telling the browser not to display it. Open Inspector (F12) and search for "admin".</div></details>
                <details><summary>Hint 2</summary><div class="hint-content">Find the element with <code>style="display: none;"</code>. In the Styles pane on the right, uncheck or delete the <code>display: none</code> property to make it visible.</div></details>
                <details><summary>Hint 3</summary><div class="hint-content">Even after revealing the panel, the flag text looks blurry! Look at the inline style of the flag text element. Remove the <code>filter: blur(...)</code> property to read it clearly.</div></details>
            </div>
            <div class="submit-section">
                <input type="text" id="flag-input" placeholder="Enter flag here (e.g., FLAG{...})">
                <button id="submit-btn">Submit Flag</button>
            </div>
        </div>
    </div>

    <!-- THE HIDDEN ADMIN CONSOLE -->
    <div id="admin-console" style="display: none; background: #000; color: #0f0; padding: 20px; margin: 20px auto; max-width: 800px; font-family: monospace; border: 1px solid #0f0; border-radius: 8px;">
        <h3 style="color: #0f0; margin-top: 0;">[ ROOT ACCESS GRANTED ]</h3>
        <p>System Status: ONLINE</p>
        <p>Authorized Personnel Only.</p>
        <p>System Flag: <span id="flag-text" style="filter: blur(8px); user-select: none;">FLAG{d0m_m4n1pul4t10n_m4st3r}</span></p>
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
                    response = {"success": True, "message": "Level 5 Cleared! You are a DOM manipulation master. Topic 1 Complete!"}
                else:
                    response = {"success": False, "message": "Incorrect flag. Did you reveal and unblur the admin console?"}
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
    print("CTFdpk Arena - Topic 1, Level 5 (DOM) Started!")
    print("Open: http://localhost:8000")
    print("=" * 50)
    httpd.serve_forever()
