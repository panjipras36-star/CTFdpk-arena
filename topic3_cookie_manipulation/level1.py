from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

FLAG = "FLAG{c00k13_m0nst3r_b4s1cs}"

class CTFHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/':
            cookie_header = self.headers.get('Cookie', '')
            is_admin = 'role=admin' in cookie_header
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
          
            if 'role=' not in cookie_header:
                self.send_header('Set-Cookie', 'role=guest; Path=/')
            self.end_headers()
        
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CTFdpk Arena - Topic 3: Level 1</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
        
        body {{
            background-color: #050505;
            color: #00ff41;
            font-family: 'VT323', 'Courier New', monospace;
            font-size: 1.2rem;
            margin: 0;
            padding: 20px;
            overflow-x: hidden;
            text-shadow: 0 0 5px #00ff41;
        }}
        
        /* Efek Scanlines TV Tabung */
        body::before {{
            content: " ";
            display: block;
            position: absolute;
            top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
            z-index: 2;
            background-size: 100% 2px, 3px 100%;
            pointer-events: none;
        }}

        .terminal-window {{
            border: 2px solid #00ff41;
            border-radius: 10px;
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
            position: relative;
            z-index: 1;
        }}

        .header-bar {{
            border-bottom: 1px dashed #00ff41;
            padding-bottom: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
        }}

        .status {{ color: #ff3333; text-shadow: 0 0 5px #ff3333; }}
        .status.granted {{ color: #00ff41; }}
        
        .prompt {{ margin-bottom: 10px; }}
        .cursor {{ animation: blink 1s step-end infinite; }}
        
        @keyframes blink {{ 50% {{ opacity: 0; }} }}

        .flag-box {{
            border: 1px solid #00ff41;
            padding: 15px;
            margin-top: 20px;
            background: rgba(0, 255, 65, 0.1);
            display: {'block' if is_admin else 'none'};
        }}

        .access-denied {{
            color: #ff3333;
            text-shadow: 0 0 5px #ff3333;
            margin-top: 20px;
            display: {'none' if is_admin else 'block'};
        }}

        input[type="text"] {{
            background: #000;
            border: 1px solid #00ff41;
            color: #00ff41;
            font-family: 'VT323', monospace;
            font-size: 1.2rem;
            padding: 10px;
            width: 70%;
            outline: none;
        }}
        
        button {{
            background: #00ff41;
            color: #000;
            border: none;
            font-family: 'VT323', monospace;
            font-size: 1.2rem;
            padding: 10px 20px;
            cursor: pointer;
            font-weight: bold;
        }}
        button:hover {{ background: #fff; }}

        details {{ margin-top: 20px; border: 1px dashed #005500; padding: 10px; }}
        summary {{ cursor: pointer; color: #00aa00; }}
        summary:hover {{ color: #00ff41; }}
        .hint-content {{ color: #00aa00; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="terminal-window">
        <div class="header-bar">
            <span>ROOT@CTFDPK-SERVER:~# ./access_control.sh</span>
            <span>TOPIC 3: LEVEL 1</span>
        </div>

        <div class="prompt">
            > Initializing secure connection...<br>
            > Loading user profile...<br>
            > Current User Role: <strong>{'ADMINISTRATOR' if is_admin else 'GUEST'}</strong><br>
            > Clearance Level: <span class="{'granted' if is_admin else 'status'}">{'MAXIMUM' if is_admin else 'DENIED'}</span>
        </div>

        <div class="access-denied">
            [!] ERROR: Access Denied. You do not have sufficient privileges to view the classified flag.<br>
            [!] The system identifies users via a small data packet stored locally in your browser.<br>
            [!] Hint: Inspect your browser's storage mechanisms.
        </div>

        <div class="flag-box">
            [+] ACCESS GRANTED. WELCOME, ADMINISTRATOR.<br>
            [+] CLASSIFIED FLAG DECRYPTED:<br><br>
            <h2 style="margin:0;">{FLAG}</h2>
        </div>

        <div style="margin-top: 30px; border-top: 1px dashed #00ff41; padding-top: 20px;">
            <div class="prompt">> SUBMIT FLAG TO VERIFY:<span class="cursor">_</span></div>
            <div style="margin-top: 10px;">
                <input type="text" id="flag-input" placeholder="FLAG{{...}}">
                <button id="submit-btn">EXECUTE</button>
            </div>
        </div>

        <details>
            <summary>[?] DECRYPT HINT PROTOCOL (Click to expand)</summary>
            <div class="hint-content">
                > HINT 1: Websites use small text files to remember user state. These are not stored in the HTML source code.<br>
                > HINT 2: Open Developer Tools (F12). Look for a tab named "Application" or "Storage". Find the domain "localhost:8000".
            </div>
        </details>
    </div>

    <script>
        document.getElementById('submit-btn').addEventListener('click', async () => {{
            const flag = document.getElementById('flag-input').value.trim();
            if (!flag) return;
            try {{
                const response = await fetch('/submit', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ flag: flag }}) }});
                const data = await response.json();
                if (data.success) {{
                    alert('[+] SUCCESS: Flag verified. Level Cleared!');
                }} else {{
                    alert('[!] ERROR: ' + data.message);
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
    print("CTFdpk Arena - Topic 3, Level 1 (Retro Terminal) Started!")
    print("Open: http://localhost:8000")
    print("=" * 50)
    httpd.serve_forever()
