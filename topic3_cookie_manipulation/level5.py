from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import base64
import html
import re

FLAG = "FLAG{jwt_w4f_byp4ss_m4st3r}"
SECRET_KEY = "netcorp_ultra_secret_2024"

USERS = {
    "guest": {"password": "guest123", "role": "guest"},
    "admin": {"password": "admin_secret_2024", "role": "admin"}
}

def b64url_encode(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def b64url_decode(data):
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)

def create_jwt(payload, alg="HS256"):
    header = {"alg": alg, "typ": "JWT"}
    h_b64 = b64url_encode(json.dumps(header, separators=(',', ':')))
    p_b64 = b64url_encode(json.dumps(payload, separators=(',', ':')))
    
    if alg.lower() == 'none':
        signature = ""
    else:
        signing_input = f"{h_b64}.{p_b64}"
        signature = base64.urlsafe_b64encode(
            base64.urlsafe_b64decode(h_b64 + '==') 
        ).decode() 
        import hashlib
        signature = b64url_encode(hashlib.sha256((signing_input + SECRET_KEY).encode()).digest())
        
    return f"{h_b64}.{p_b64}.{signature}"

def verify_jwt(token):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None, None, None
            
        header = json.loads(b64url_decode(parts[0]))
        payload = json.loads(b64url_decode(parts[1]))
        signature = parts[2]
        
        return header, payload, signature
    except Exception:
        return None, None, None


class WAF:
    @staticmethod
    def check_request(headers):
        """Simulasi Web Application Firewall."""
        cookie_header = headers.get('Cookie', '')
        
        match = re.search(r'auth=([^;]+)', cookie_header)
        if match:
            token = match.group(1)
            parts = token.split('.')
            if len(parts) >= 1:
                try:
                    header_raw = b64url_decode(parts[0])
                    if b'"alg":"none"' in header_raw:
                        return False
                except Exception:
                    pass
        return True 

class CTFHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/logout':
            self.send_response(302)
            self.send_header('Set-Cookie', 'auth=; Path=/; Max-Age=0')
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        if parsed_path.path == '/login' or parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(LOGIN_HTML.encode())
            return
        
        if parsed_path.path == '/dashboard':
            cookie_header = self.headers.get('Cookie', '')
            match = re.search(r'auth=([^;]+)', cookie_header)
            if not match:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            token = match.group(1)
            header, payload, sig = verify_jwt(token)
            
            if not payload or payload.get('role') not in ['guest', 'admin']:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            dashboard = DASHBOARD_HTML.replace('{{USERNAME}}', html.escape(payload.get('user', 'Unknown')))
            dashboard = dashboard.replace('{{ROLE}}', payload.get('role', 'unknown'))
            self.wfile.write(dashboard.encode())
            return
        
        if parsed_path.path == '/admin':
            if not WAF.check_request(self.headers):
                self.send_response(403)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(WAF_BLOCK_HTML.encode())
                return
            
            cookie_header = self.headers.get('Cookie', '')
            match = re.search(r'auth=([^;]+)', cookie_header)
            if not match:
                self.send_response(403)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(ACCESS_DENIED_HTML.encode())
                return
            
            token = match.group(1)
            header, payload, sig = verify_jwt(token)
            
            if not header or not payload:
                self.send_response(403)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(ACCESS_DENIED_HTML.encode())
                return
            
        
            alg = header.get('alg', '').lower().strip()
            
            if alg == 'none':
                if payload.get('role') == 'admin':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    admin_html = ADMIN_HTML.replace('{{FLAG}}', FLAG)
                    self.wfile.write(admin_html.encode())
                    return
                else:
                    self.send_response(403)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(ACCESS_DENIED_HTML.encode())
                    return
            else:
               
                self.send_response(403)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(ACCESS_DENIED_HTML.encode())
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
            
            if username in USERS and USERS[username]['password'] == password:
                payload = {"user": username, "role": USERS[username]['role'], "iat": 1724140800}
                token = create_jwt(payload, alg="HS256")
                
                self.send_response(302)
                self.send_header('Set-Cookie', f'auth={token}; Path=/')
                self.send_header('Location', '/dashboard')
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_html = LOGIN_HTML.replace('</form>', '<p style="color:#ff3333;text-align:center;">[!] INVALID CREDENTIALS</p></form>')
                self.wfile.write(error_html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[SERVER LOG] {format % args}")

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NetCorp - Secure Login</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        body { margin: 0; padding: 0; background-color: #050510; color: #e0e0e0; font-family: 'Share Tech Mono', monospace; overflow-x: hidden; height: 100vh; display: flex; justify-content: center; align-items: center; }
        #matrix-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; opacity: 0.3; }
        .login-box { position: relative; z-index: 1; background: rgba(10, 10, 20, 0.95); border: 2px solid #00ffff; box-shadow: 0 0 20px #00ffff; padding: 40px; width: 400px; border-radius: 5px; }
        .login-box h1 { color: #00ffff; text-shadow: 0 0 10px #00ffff; text-align: center; margin-bottom: 30px; }
        .input-group { margin-bottom: 20px; }
        .input-group label { display: block; color: #00ffff; margin-bottom: 5px; }
        .input-group input { width: 100%; background: #000; border: 1px solid #00ffff; color: #00ffff; padding: 10px; font-family: 'Share Tech Mono', monospace; font-size: 1rem; outline: none; box-sizing: border-box; }
        .input-group input:focus { box-shadow: 0 0 10px #00ffff; }
        button { width: 100%; background: #ff00ff; color: #fff; border: none; padding: 12px; font-family: 'Share Tech Mono', monospace; font-size: 1.1rem; cursor: pointer; font-weight: bold; }
        button:hover { background: #fff; color: #ff00ff; box-shadow: 0 0 15px #ff00ff; }
        .hint { margin-top: 20px; padding-top: 20px; border-top: 1px solid #333; font-size: 0.9rem; color: #666; text-align: center; }
    </style>
</head>
<body>
    <canvas id="matrix-bg"></canvas>
    <div class="login-box">
        <h1>NETCORP SECURE LOGIN</h1>
        <form method="POST" action="/login">
            <div class="input-group">
                <label>USERNAME</label>
                <input type="text" name="username" required>
            </div>
            <div class="input-group">
                <label>PASSWORD</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">AUTHENTICATE</button>
        </form>
        <div class="hint">
            <p>Default credentials: guest / guest123</p>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('matrix-bg');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth; canvas.height = window.innerHeight;
        const chars = '01'; const fontSize = 14; const columns = canvas.width / fontSize; const drops = [];
        for (let i = 0; i < columns; i++) drops[i] = 1;
        function drawMatrix() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.05)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#00ffff'; ctx.font = fontSize + 'px monospace';
            for (let i = 0; i < drops.length; i++) {
                const text = chars.charAt(Math.floor(Math.random() * chars.length));
                if (i < columns * 0.2 || i > columns * 0.8) ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 50);
    </script>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NetCorp - Dashboard</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        body { margin: 0; padding: 0; background-color: #050510; color: #e0e0e0; font-family: 'Share Tech Mono', monospace; }
        #matrix-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; opacity: 0.3; }
        .container { position: relative; z-index: 1; max-width: 1200px; margin: 0 auto; padding: 20px; }
        nav { background: rgba(10, 10, 20, 0.95); border: 2px solid #00ffff; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        nav h1 { margin: 0; color: #00ffff; text-shadow: 0 0 10px #00ffff; }
        nav .user-info { color: #00ffff; }
        nav a { color: #ff00ff; text-decoration: none; margin-left: 20px; }
        nav a:hover { text-shadow: 0 0 10px #ff00ff; }
        .content { background: rgba(10, 10, 20, 0.95); border: 2px solid #00ffff; padding: 30px; }
        .content h2 { color: #00ffff; border-bottom: 1px solid #ff00ff; padding-bottom: 10px; }
        .card { background: rgba(0, 255, 255, 0.05); border: 1px solid #00ffff; padding: 20px; margin: 20px 0; }
        .card h3 { color: #ff00ff; margin-top: 0; }
        .warning { color: #ff3333; text-shadow: 0 0 5px #ff3333; }
        .waf-status { background: rgba(255, 0, 0, 0.1); border: 1px solid #ff3333; padding: 10px; margin-bottom: 20px; color: #ff3333; font-weight: bold; }
        details { margin-top: 20px; border-top: 1px solid #333; padding-top: 10px; }
        summary { color: #00ffff; cursor: pointer; font-size: 1.1rem; }
        .hint-text { color: #aaa; margin-top: 10px; font-size: 1rem; }
    </style>
</head>
<body>
    <canvas id="matrix-bg"></canvas>
    <div class="container">
        <nav>
            <h1>NETCORP DASHBOARD</h1>
            <div>
                <span class="user-info">Welcome, {{USERNAME}} ({{ROLE}})</span>
                <a href="/admin">[ADMIN PANEL]</a>
                <a href="/logout">[LOGOUT]</a>
            </div>
        </nav>
        <div class="waf-status">[!] SYSTEM PROTECTION: WEB APPLICATION FIREWALL (WAF) ACTIVE</div>
        <div class="content">
            <h2>USER PROFILE</h2>
            <div class="card">
                <h3>Account Information</h3>
                <p>Username: {{USERNAME}}</p>
                <p>Role: {{ROLE}}</p>
                <p>Token Type: JWT (HS256 Signed)</p>
            </div>
            <div class="card">
                <h3>Access Level</h3>
                <p class="warning">Your current access level does not permit viewing classified materials.</p>
            </div>
        </div>
        <details>
            <summary>[?] DECRYPT HINT PROTOCOL</summary>
            <div class="hint-text">
                > HINT 1: The server uses JWT. The header contains the algorithm ("alg"). The "none" algorithm disables signature verification.<br>
                > HINT 2: A WAF is active. It monitors cookies for malicious patterns. Analyze how the WAF parses the JWT header.<br>
                > HINT 3: WAF rules are often implemented with strict regex. Backend logic might be more forgiving (normalization).
            </div>
        </details>
    </div>
    <script>
        const canvas = document.getElementById('matrix-bg'); const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth; canvas.height = window.innerHeight;
        const chars = '01'; const fontSize = 14; const columns = canvas.width / fontSize; const drops = [];
        for (let i = 0; i < columns; i++) drops[i] = 1;
        function drawMatrix() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.05)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#00ffff'; ctx.font = fontSize + 'px monospace';
            for (let i = 0; i < drops.length; i++) {
                const text = chars.charAt(Math.floor(Math.random() * chars.length));
                if (i < columns * 0.2 || i > columns * 0.8) ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 50);
    </script>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NetCorp - Admin Panel</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        body { margin: 0; padding: 0; background-color: #050510; color: #e0e0e0; font-family: 'Share Tech Mono', monospace; }
        #matrix-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; opacity: 0.3; }
        .container { position: relative; z-index: 1; max-width: 1200px; margin: 0 auto; padding: 20px; }
        nav { background: rgba(10, 10, 20, 0.95); border: 2px solid #00ff00; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        nav h1 { margin: 0; color: #00ff00; text-shadow: 0 0 10px #00ff00; }
        nav a { color: #ff00ff; text-decoration: none; margin-left: 20px; }
        .content { background: rgba(10, 10, 20, 0.95); border: 2px solid #00ff00; padding: 30px; }
        .content h2 { color: #00ff00; border-bottom: 1px solid #ff00ff; padding-bottom: 10px; }
        .flag-box { background: rgba(0, 255, 0, 0.1); border: 2px dashed #00ff00; padding: 30px; margin: 30px 0; text-align: center; }
        .flag-text { font-size: 2rem; color: #ffff00; text-shadow: 0 0 15px #ffff00; margin: 20px 0; }
        .success { color: #00ff00; text-shadow: 0 0 10px #00ff00; }
    </style>
</head>
<body>
    <canvas id="matrix-bg"></canvas>
    <div class="container">
        <nav>
            <h1>NETCORP ADMIN PANEL</h1>
            <div><a href="/dashboard">[BACK]</a> <a href="/logout">[LOGOUT]</a></div>
        </nav>
        <div class="content">
            <h2 class="success">ROOT ACCESS GRANTED - WAF BYPASSED</h2>
            <p>Congratulations. You have successfully bypassed the WAF and forged a valid admin token.</p>
            <div class="flag-box">
                <p>CLASSIFIED FLAG:</p>
                <div class="flag-text">{{FLAG}}</div>
            </div>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('matrix-bg'); const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth; canvas.height = window.innerHeight;
        const chars = '01'; const fontSize = 14; const columns = canvas.width / fontSize; const drops = [];
        for (let i = 0; i < columns; i++) drops[i] = 1;
        function drawMatrix() {
            ctx.fillStyle = 'rgba(5, 5, 16, 0.05)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#00ffff'; ctx.font = fontSize + 'px monospace';
            for (let i = 0; i < drops.length; i++) {
                const text = chars.charAt(Math.floor(Math.random() * chars.length));
                if (i < columns * 0.2 || i > columns * 0.8) ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 50);
    </script>
</body>
</html>
"""

WAF_BLOCK_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NetCorp - WAF Blocked</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        body { margin: 0; padding: 0; background-color: #050510; color: #e0e0e0; font-family: 'Share Tech Mono', monospace; height: 100vh; display: flex; justify-content: center; align-items: center; }
        .error-box { background: rgba(10, 10, 20, 0.95); border: 2px solid #ff3333; box-shadow: 0 0 30px #ff3333; padding: 40px; text-align: center; max-width: 600px; }
        .error-box h1 { color: #ff3333; text-shadow: 0 0 10px #ff3333; font-size: 2rem; }
        .error-box p { color: #ff6666; }
        .error-box a { color: #00ffff; text-decoration: none; border: 1px solid #00ffff; padding: 10px 20px; display: inline-block; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="error-box">
        <h1>403 - WAF INTERCEPTED</h1>
        <p>Malicious token signature detected. Request blocked by Web Application Firewall.</p>
        <p>Rule Violation: Invalid Algorithm Header</p>
        <a href="/dashboard">Return to Dashboard</a>
    </div>
</body>
</html>
"""

ACCESS_DENIED_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NetCorp - Access Denied</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        body { margin: 0; padding: 0; background-color: #050510; color: #e0e0e0; font-family: 'Share Tech Mono', monospace; height: 100vh; display: flex; justify-content: center; align-items: center; }
        .error-box { background: rgba(10, 10, 20, 0.95); border: 2px solid #ff3333; box-shadow: 0 0 20px #ff3333; padding: 40px; text-align: center; }
        .error-box h1 { color: #ff3333; text-shadow: 0 0 10px #ff3333; }
        .error-box a { color: #00ffff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="error-box">
        <h1>403 - ACCESS DENIED</h1>
        <p>Invalid or insufficient privileges.</p>
        <p><a href="/dashboard">Return to Dashboard</a></p>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CTFHandler)
    print("=" * 50)
    print("CTFdpk Arena - Topic 3, Level 5 (JWT + WAF Bypass) Started!")
    print("Open: http://localhost:8000")
    print("=" * 50)
    httpd.serve_forever()
