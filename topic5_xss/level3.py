from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

FLAG = "FLAG{d0m_xss_r34l_w0rld}"

class TicketHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        
        if path == '/' or path == '/login':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(LOGIN_HTML.encode())
            return
        
        if path == '/tickets':
            cookie = self.headers.get('Cookie', '')
            if 'session' not in cookie:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(TICKET_HTML.encode())
            return
        
        if path == '/submit':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(SUBMIT_HTML.encode())
            return
            
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]
            
            if username == 'it_support' and password == 'helpdesk123':
                self.send_response(302)
                self.send_header('Set-Cookie', 'session=valid; Path=/')
                self.send_header('Location', '/tickets')
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(LOGIN_HTML.replace('<!-- ERROR_PLACEHOLDER -->', '<div style="color:red;text-align:center;margin-bottom:15px;">Invalid credentials</div>').encode())
        
        elif self.path == '/check_flag':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            submitted_flag = form_data.get('flag', [''])[0].strip()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            if submitted_flag == FLAG:
                self.wfile.write(CYBERPUNK_HTML.encode())
            else:
                self.wfile.write(SUBMIT_HTML.replace('{{MESSAGE}}', '<div style="color:#ff003c;text-shadow:0 0 10px #ff003c;font-size:20px;margin-top:20px;">[ ACCESS DENIED ] INVALID FLAG</div>').encode())

    def log_message(self, format, *args):
        pass

LOGIN_HTML = """<!DOCTYPE html>
<html>
<head><title>CityNet - IT Support Login</title></head>
<body style="font-family:sans-serif;background:#f0f2f5;margin:0;padding:40px;">
<div style="max-width:400px;margin:0 auto;background:white;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    <h1 style="color:#1e3a8a;text-align:center;">IT Support Portal</h1>
    <!-- ERROR_PLACEHOLDER -->
    <form method="POST" action="/login">
        <input type="text" name="username" placeholder="Username" style="width:100%;padding:10px;margin:10px 0;box-sizing:border-box;"><br>
        <input type="password" name="password" placeholder="Password" style="width:100%;padding:10px;margin:10px 0;box-sizing:border-box;"><br>
        <button type="submit" style="width:100%;padding:10px;background:#1e3a8a;color:white;border:none;">Login</button>
    </form>
    <p style="color:#999;font-size:12px;text-align:center;margin-top:20px;">Hint: it_support / helpdesk123</p>
</div>
</body>
</html>"""

TICKET_HTML = f"""<!DOCTYPE html>
<html>
<head><title>IT Support - Ticket Search</title></head>
<body style="font-family:sans-serif;background:#f8fafc;margin:0;padding:40px;">
<div style="max-width:800px;margin:0 auto;background:white;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
        <h1 style="color:#1e3a8a;margin:0;">Ticket Search System</h1>
        <a href="/submit" style="color:#fbbf24;font-weight:bold;text-decoration:none;">[ SUBMIT FLAG ]</a>
    </div>
    
    <p style="color:#64748b;">Search for internal IT support tickets by keyword.</p>
    
    <div style="background:#f1f5f9;padding:15px;border-radius:4px;margin-bottom:20px;">
        <input type="text" id="searchInput" placeholder="Enter ticket keyword..." style="width:70%;padding:10px;border:1px solid #cbd5e1;border-radius:4px;">
        <button onclick="performSearch()" style="padding:10px 20px;background:#1e3a8a;color:white;border:none;border-radius:4px;cursor:pointer;">Search</button>
    </div>

    <div id="results" style="min-height:100px;border:1px dashed #cbd5e1;padding:20px;color:#64748b;">
        Waiting for search query...
    </div>

    <script>
        // Debug token - contains sensitive data (DO NOT EXPOSE)
        var _dbg_token = "{FLAG}";
        
        // Client-side WAF: block script tags only (case-insensitive)
        function sanitizeInput(input) {{
            let sanitized = input;
            sanitized = sanitized.replace(/<script>/gi, '[BLOCKED]');
            sanitized = sanitized.replace(/<\\/script>/gi, '[BLOCKED]');
            return sanitized;
        }}
        
        function performSearch() {{
            const rawQuery = document.getElementById('searchInput').value;
            const sanitized = sanitizeInput(rawQuery);
            // VULNERABILITY: innerHTML with user input
            // Note: innerHTML does NOT execute <script> tags, but DOES execute inline event handlers
            document.getElementById('results').innerHTML = '<div style="padding:15px;">' + sanitized + '</div>';
        }}
    </script>
</div>
</body>
</html>"""

SUBMIT_HTML = """<!DOCTYPE html>
<html>
<head><title>Submit Flag</title></head>
<body style="font-family:monospace;background:#0a0a0a;color:#00ff41;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;">
<div style="background:#111;padding:40px;border:2px solid #00ff41;border-radius:8px;box-shadow:0 0 20px #00ff41;width:500px;text-align:center;">
    <h1 style="color:#00ff41;text-shadow:0 0 10px #00ff41;margin:0;">[ FLAG SUBMISSION TERMINAL ]</h1>
    <p style="color:#00ff41;font-size:14px;margin:20px 0;">> Enter extracted flag to verify access_</p>
    <form method="POST" action="/check_flag">
        <input type="text" name="flag" placeholder="FLAG{...}" style="width:90%;padding:12px;background:#000;color:#00ff41;border:1px solid #00ff41;font-family:monospace;font-size:16px;margin:10px 0;">
        <br><button type="submit" style="width:90%;padding:12px;background:#00ff41;color:#000;border:none;font-family:monospace;font-weight:bold;font-size:16px;cursor:pointer;margin-top:10px;">>> SUBMIT <<</button>
    </form>
    {{MESSAGE}}
    <p style="color:#666;font-size:12px;margin-top:30px;"><a href="/tickets" style="color:#666;">[ RETURN TO DASHBOARD ]</a></p>
</div>
</body>
</html>"""

CYBERPUNK_HTML = """<!DOCTYPE html>
<html>
<head><title>ACCESS GRANTED</title>
<style>
@keyframes flicker { 0%, 100% { opacity: 1; } 50% { opacity: 0.8; } }
@keyframes glitch { 0% { transform: translate(0); } 20% { transform: translate(-2px, 2px); } 40% { transform: translate(-2px, -2px); } 60% { transform: translate(2px, 2px); } 80% { transform: translate(2px, -2px); } 100% { transform: translate(0); } }
body { margin: 0; background: #0a0a0a; font-family: 'Courier New', monospace; color: #00ff41; overflow: hidden; display: flex; justify-content: center; align-items: center; height: 100vh; position: relative; }
body::before { content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: repeating-linear-gradient(0deg, rgba(0, 255, 65, 0.03) 0px, rgba(0, 255, 65, 0.03) 1px, transparent 1px, transparent 2px); pointer-events: none; z-index: 10; }
.container { text-align: center; z-index: 5; animation: flicker 2s infinite; }
.skull { font-size: 120px; color: #ff003c; text-shadow: 0 0 20px #ff003c, 0 0 40px #ff003c; margin: 0; animation: glitch 0.3s infinite; line-height: 1; }
.title { font-size: 48px; color: #00ff41; text-shadow: 0 0 10px #00ff41; margin: 20px 0; letter-spacing: 8px; }
.subtitle { font-size: 18px; color: #ff003c; text-shadow: 0 0 8px #ff003c; margin: 10px 0; letter-spacing: 4px; }
.flag-box { margin-top: 30px; padding: 20px; border: 2px dashed #00ff41; background: rgba(0, 255, 65, 0.05); display: inline-block; }
.flag-text { font-size: 24px; color: #00ff41; text-shadow: 0 0 10px #00ff41; letter-spacing: 2px; }
</style>
</head>
<body>
<div class="container">
    <div class="skull">💀</div>
    <div class="title">GREAT JOB, HACKER</div>
    <div class="subtitle">[ DOM XSS EXPLOITATION SUCCESSFUL ]</div>
    <div class="flag-box">
        <div style="font-size:12px;color:#666;margin-bottom:10px;letter-spacing:2px;">EXTRACTED FLAG:</div>
        <div class="flag-text">FLAG{d0m_xss_r34l_w0rld}</div>
    </div>
</div>
</body>
</html>"""

if __name__ == '__main__':
    httpd = HTTPServer(('', 8003), TicketHandler)
    print("=" * 50)
    print("Topic 5 - Level 3: DOM-based XSS (Real World)")
    print("Open: http://localhost:8003")
    print("=" * 50)
    httpd.serve_forever()
