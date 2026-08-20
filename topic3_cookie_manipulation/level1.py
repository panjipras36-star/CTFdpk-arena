#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
import json
import urllib.parse

FLAG = "FLAG{cyb3r_c00k13_m4st3r}"

class CTFHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/':
            cookie_header = self.headers.get('Cookie', '')
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            
            is_admin = False
            if 'role' in cookie:
                if cookie['role'].value == 'admin':
                    is_admin = True
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            
            if 'role' not in cookie:
                self.send_header('Set-Cookie', 'role=guest; Path=/; HttpOnly')
            self.end_headers()
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CTFdpk Arena - Topic 3: Level 1</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        
        body {{
            margin: 0;
            padding: 0;
            background-color: #050510;
            color: #e0e0e0;
            font-family: 'Share Tech Mono', monospace;
            overflow-x: hidden;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        /* Binary Rain Background */
        #matrix-bg {{
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: 0;
            opacity: 0.3;
        }}

        /* Main Dashboard Panel */
        .dashboard {{
            position: relative;
            z-index: 1;
            background: rgba(10, 10, 20, 0.95);
            border: 2px solid #00ffff;
            box-shadow: 0 0 20px #00ffff, inset 0 0 20px rgba(0, 255, 255, 0.2);
            padding: 30px;
            width: 800px;
            max-width: 90%;
            border-radius: 5px;
        }}

        .header {{
            border-bottom: 2px solid #ff00ff;
            padding-bottom: 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .header h1 {{
            margin: 0;
            color: #00ffff;
            text-shadow: 0 0 10px #00ffff;
            font-size: 1.8rem;
        }}

        .status-badge {{
            background: #ff00ff;
            color: #000;
            padding: 5px 15px;
            font-weight: bold;
            border-radius: 3px;
            box-shadow: 0 0 10px #ff00ff;
        }}

        .status-badge.admin {{
            background: #00ff00;
            box-shadow: 0 0 10px #00ff00;
        }}

        .content {{
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 20px;
        }}

        .highlight {{ color: #00ffff; font-weight: bold; }}
        .danger {{ color: #ff3333; font-weight: bold; text-shadow: 0 0 5px #ff3333; }}

        .flag-container {{
            background: rgba(0, 255, 255, 0.1);
            border: 1px dashed #00ffff;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            display: {'block' if is_admin else 'none'};
        }}

        .flag-text {{
            font-size: 1.5rem;
            color: #ffff00;
            text-shadow: 0 0 10px #ffff00;
            margin: 10px 0;
        }}

        .input-group {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }}

        input[type="text"] {{
            flex: 1;
            background: #000;
            border: 1px solid #00ffff;
            color: #00ffff;
            padding: 10px;
            font-family: 'Share Tech Mono', monospace;
            font-size: 1.1rem;
            outline: none;
        }}

        input[type="text"]:focus {{
            box-shadow: 0 0 10px #00ffff;
        }}

        button {{
            background: #ff00ff;
            color: #fff;
            border: none;
            padding: 10px 20px;
            font-family: 'Share Tech Mono', monospace;
            font-size: 1.1rem;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }}

        button:hover {{
            background: #fff;
            color: #ff00ff;
            box-shadow: 0 0 15px #ff00ff;
        }}

        details {{
            margin-top: 20px;
            border-top: 1px solid #333;
            padding-top: 10px;
        }}

        summary {{
            color: #00ffff;
            cursor: pointer;
            font-size: 1.1rem;
        }}

        summary:hover {{ text-shadow: 0 0 5px #00ffff; }}

        .hint-text {{
            color: #aaa;
            margin-top: 10px;
            font-size: 1rem;
        }}
    </style>
</head>
<body>
    <canvas id="matrix-bg"></canvas>

    <div class="dashboard">
        <div class="header">
            <h1>NETRUNNER ACCESS TERMINAL</h1>
            <div class="status-badge {'admin' if is_admin else ''}">
                {'AUTHORIZED' if is_admin else 'GUEST ACCESS'}
            </div>
        </div>

        <div class="content">
            <p>> SYSTEM STATUS: <span class="highlight">ONLINE</span></p>
            <p>> USER IDENTIFICATION: <span class="highlight">{cookie['role'].value if 'role' in cookie else 'UNKNOWN'}</span></p>
            <p>> CLEARANCE LEVEL: <span class="{'highlight' if is_admin else 'danger'}">{'OMEGA' if is_admin else 'RESTRICTED'}</span></p>
            
            {'<p>> ACCESSING CLASSIFIED DATABASE...</p>' if is_admin else '<p class="danger">> ERROR: INSUFFICIENT PRIVILEGES. FLAG ENCRYPTED.</p>'}
        </div>

        <div class="flag-container">
            <p>> DECRYPTION SUCCESSFUL. FLAG EXTRACTED:</p>
            <div class="flag-text">{FLAG}</div>
        </div>

        <div class="input-group">
            <input type="text" id="flag-input" placeholder="ENTER FLAG TO VERIFY...">
            <button id="submit-btn">TRANSMIT</button>
        </div>

        <details>
            <summary>[?] DECRYPT HINT PROTOCOL</summary>
            <div class="hint-text">
                > HINT 1: The server identifies you using a small data packet stored in your browser's memory.<br>
                > HINT 2: Open Developer Tools (F12). Navigate to the 'Application' or 'Storage' tab. Inspect the Cookies for this domain.
            </div>
        </details>
    </div>

    <script>
        // Binary Rain Effect (Cyberpunk Style)
        const canvas = document.getElementById('matrix-bg');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const chars = '01';
        const fontSize = 14;
        const columns = canvas.width / fontSize;
        const drops = [];
        for (let i = 0; i < columns; i++) drops[i] = 1;

        function drawMatrix() {{
            ctx.fillStyle = 'rgba(5, 5, 16, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#00ffff';
            ctx.font = fontSize + 'px monospace';

            for (let i = 0; i < drops.length; i++) {{
                const text = chars.charAt(Math.floor(Math.random() * chars.length));
                // Hanya gambar di sisi kiri dan kanan (20% masing-masing)
                if (i < columns * 0.2 || i > columns * 0.8) {{
                    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                }}
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }}
        }}
        setInterval(drawMatrix, 50);

        // Submit Logic
        document.getElementById('submit-btn').addEventListener('click', async () => {{
            const flag = document.getElementById('flag-input').value.trim();
            if (!flag) return;
            try {{
                const response = await fetch('/submit', {{ 
                    method: 'POST', 
                    headers: {{ 'Content-Type': 'application/json' }}, 
                    body: JSON.stringify({{ flag: flag }}) 
                }});
                const data = await response.json();
                if (data.success) {{
                    alert('[+] TRANSMISSION SUCCESSFUL. FLAG VERIFIED.');
                }} else {{
                    alert('[!] TRANSMISSION FAILED: ' + data.message);
                }}
            }} catch (error) {{ alert('[!] SYSTEM ERROR'); }}
        }});
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
                    response = {"success": True, "message": "Level 1 Cleared!"}
                else:
                    response = {"success": False, "message": "Invalid flag sequence."}
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
    print("CTFdpk Arena - Topic 3, Level 1 (Cyberpunk) Started!")
    print("Open: http://localhost:8000")
    print("=" * 50)
    httpd.serve_forever()
