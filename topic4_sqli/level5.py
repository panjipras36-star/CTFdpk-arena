from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
import sqlite3
import urllib.parse
import html
import re
import hashlib
import subprocess

FLAG_IN_DB = "FLAG{w4f_by_p4ss_m4st3r_v2}"
ENCRYPTION_KEY = "citynet2024"
SECRET_MESSAGE = "Login as EMP002 / staff123 to access the dashboard."

def generate_encrypted_message():
    try:
        result = subprocess.run(
            ['openssl', 'enc', '-aes-256-cbc', '-a', '-k', ENCRYPTION_KEY, '-md', 'sha256'],
            input=SECRET_MESSAGE.encode(),
            capture_output=True
        )
        return result.stdout.strip()
    except Exception:
        return b"ENCRYPTION_FAILED"

ENCRYPTED_DATA = generate_encrypted_message()

def init_db():
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('CREATE TABLE employees (id INTEGER PRIMARY KEY, emp_id TEXT, name TEXT, password TEXT, role TEXT)')
    c.execute('CREATE TABLE secret_flags (id INTEGER PRIMARY KEY, flag_text TEXT)')
    
    admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
    staff_hash = hashlib.sha256("staff123".encode()).hexdigest()
    
    c.execute("INSERT INTO employees VALUES (1, 'EMP001', 'Admin', ?, 'admin')", (admin_hash,))
    c.execute("INSERT INTO employees VALUES (2, 'EMP002', 'Staff', ?, 'employee')", (staff_hash,))
    c.execute(f"INSERT INTO secret_flags VALUES (1, '{FLAG_IN_DB}')")
    conn.commit()
    return conn

DB_CONN = init_db()

def waf_check(input_str):
    lower_input = input_str.lower()
    if re.search(r'\bunion\b', lower_input): return False
    if re.search(r'\band\b', lower_input): return False
    if re.search(r'\bor\b', lower_input): return False
    if '--' in input_str or '/*' in input_str or '*/' in input_str: return False
    return True

def execute_stacked_query(query):
    statements = [s.strip() for s in query.split(';') if s.strip() and s.strip() not in ["'", "''"]]
    results = []
    for stmt in statements:
        try:
            c = DB_CONN.cursor()
            c.execute(stmt)
            try:
                rows = c.fetchall()
                if rows: results = rows
            except: pass
        except Exception as e:
            print(f"[DB ERROR] {e}")
    return results

class CTFHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == '/assets':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""<html><body style="font-family:monospace; background:#111; color:#0f0; padding:40px;">
            <h2>/assets/ Directory</h2><hr>
            <ul><li><a href="/assets/surprise.txt" style="color:#0f0;">surprise.txt</a></li>
            <li><a href="/assets/system_logs.dat" style="color:#0f0;">system_logs.dat</a></li></ul></body></html>""")
            return

        if path == '/assets/surprise.txt':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Decoy file. Nothing here.")
            return

        if path == '/assets/system_logs.dat':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"QWNjZXNzIGdyYW50ZWQuIEFuYWx5emUgeW91ciBuZXh0IHZlY3RvciBjYXJlZnVsbHkuIERvIG5vdCBiZSByZWNrbGVzcy4gVGhlIG5leHQgY2x1ZSBpcyBsb2NhdGVkIGF0IC9kb2NzLg==")
            return

        if path == '/docs':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"ERROR 403: Forbidden. Payload intercepted. Data is encrypted. Missing decryption key. Hint: Check /static/legacy_auth.js\n\n" + ENCRYPTED_DATA)
            return

        if path == '/static/legacy_auth.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            self.wfile.write(b"// Decryption key: 'citynet2024'\n")
            return

        if path == '/login' or path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(LOGIN_HTML.encode())
            return

        if path == '/dashboard':
            cookie = SimpleCookie()
            cookie.load(self.headers.get('Cookie', ''))
            if 'session_emp' not in cookie:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.replace('{{RESULTS}}', '<p style="color:#64748b;font-style:italic;">Enter an Employee ID above to search.</p>').encode())
            return

        if path == '/submit':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(SUBMIT_PAGE_HTML.encode())
            return

        if path == '/admin':
            self.send_response(403)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>403 Forbidden</h1><p>Even admins cannot view the flag directly here. You must extract it from the database.</p>")
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            emp_id = form_data.get('emp_id', [''])[0]
            password = form_data.get('password', [''])[0]
            input_hash = hashlib.sha256(password.encode()).hexdigest()
            
            c = DB_CONN.cursor()
            c.execute(f"SELECT * FROM employees WHERE emp_id='{emp_id}' AND password='{input_hash}'")
            user = c.fetchone()
            
            if user:
                self.send_response(302)
                self.send_header('Set-Cookie', f'session_emp={user[1]}; Path=/')
                self.send_header('Location', '/dashboard')
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(LOGIN_HTML.replace('<!-- ERROR_MSG -->', '<div style="color:red;text-align:center;">Invalid credentials</div>').encode())

        elif self.path == '/search':
            cookie = SimpleCookie()
            cookie.load(self.headers.get('Cookie', ''))
            if 'session_emp' not in cookie:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            search_input = form_data.get('query', [''])[0]

            if not waf_check(search_input):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(DASHBOARD_HTML.replace('{{RESULTS}}', '<div style="color:red;"><strong>[!] WAF BLOCKED:</strong> Malicious pattern detected.</div>').encode())
                return

            query = f"SELECT name, role FROM employees WHERE emp_id = '{search_input}'"
            
            try:
                results = execute_stacked_query(query)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html_results = "<table style='width:100%;border-collapse:collapse;margin-top:15px;'><tr style='background:#f1f5f9;'><th style='padding:10px;border:1px solid #cbd5e1;'>Name</th><th style='padding:10px;border:1px solid #cbd5e1;'>Role</th></tr>"
                if results:
                    for row in results:
                        html_results += f"<tr><td style='padding:10px;border:1px solid #cbd5e1;'>{html.escape(str(row[0]))}</td><td style='padding:10px;border:1px solid #cbd5e1;'>{html.escape(str(row[1]))}</td></tr>"
                else:
                    html_results += "<tr><td colspan='2' style='padding:10px;text-align:center;color:#64748b;'>No results found</td></tr>"
                html_results += "</table>"
                
                self.wfile.write(DASHBOARD_HTML.replace('{{RESULTS}}', html_results).encode())
            except Exception as e:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(DASHBOARD_HTML.replace('{{RESULTS}}', f'<div style="color:red;">DB Error: {html.escape(str(e))}</div>').encode())

        elif self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            submitted_flag = form_data.get('flag', [''])[0].strip()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            if submitted_flag == FLAG_IN_DB:
                self.wfile.write(CYBERPUNK_SUCCESS_HTML.encode())
            else:
                self.wfile.write(SUBMIT_PAGE_HTML.replace('{{MESSAGE}}', '<div style="color:#ff003c;text-shadow:0 0 10px #ff003c;font-size:24px;margin-top:20px;">[ ACCESS DENIED ] INVALID FLAG</div>').encode())

    def log_message(self, format, *args):
        pass

LOGIN_HTML = """<!DOCTYPE html><html><head><title>Login</title></head><body style="font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;background:#f0f2f5;margin:0;">
<div style="background:white;padding:40px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.1);width:300px;">
<h2 style="text-align:center;color:#1e3a8a;">CityNet Login</h2>
<!-- dev note: check /assets -->
<form method="POST" action="/login">
<input type="text" name="emp_id" placeholder="Employee ID" style="width:100%;padding:10px;margin:10px 0;box-sizing:border-box;"><br>
<input type="password" name="password" placeholder="Password" style="width:100%;padding:10px;margin:10px 0;box-sizing:border-box;"><br>
<button type="submit" style="width:100%;padding:10px;background:#1e3a8a;color:white;border:none;">Sign In</button>
</form><!-- ERROR_MSG --></div></body></html>"""

DASHBOARD_HTML = """<!DOCTYPE html><html><head><title>Dashboard</title></head><body style="font-family:sans-serif;background:#f8fafc;margin:0;">
<div style="background:#1e3a8a;color:white;padding:15px 30px;display:flex;justify-content:space-between;align-items:center;">
<h2 style="margin:0;">CityNet Dashboard</h2>
<div>
<a href="/submit" style="color:#fbbf24;margin-right:20px;font-weight:bold;text-decoration:none;">[ SUBMIT FLAG ]</a>
<a href="/admin" style="color:white;margin-right:20px;text-decoration:none;">Admin Panel</a>
<a href="/logout" style="color:white;text-decoration:none;">Logout</a>
</div></div>
<div style="max-width:800px;margin:40px auto;background:white;padding:30px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.05);">
<h3 style="color:#1e3a8a;">Employee Search</h3>
<p style="color:#64748b;font-size:14px;">Search for employee details. (WAF Active: UNION, AND, OR, --, /* are blocked)</p>
<form method="POST" action="/search">
<input type="text" name="query" placeholder="Enter Employee ID (e.g., EMP001)" style="width:70%;padding:10px;border:1px solid #cbd5e1;border-radius:4px;">
<button type="submit" style="padding:10px 20px;background:#1e3a8a;color:white;border:none;border-radius:4px;cursor:pointer;">Search</button>
</form>
<hr style="margin:20px 0;">
{{RESULTS}}
</div></body></html>"""

SUBMIT_PAGE_HTML = """<!DOCTYPE html><html><head><title>Submit Flag</title></head><body style="font-family:monospace;background:#0a0a0a;color:#00ff41;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;">
<div style="background:#111;padding:40px;border:2px solid #00ff41;border-radius:8px;box-shadow:0 0 20px #00ff41;width:500px;text-align:center;">
<h1 style="color:#00ff41;text-shadow:0 0 10px #00ff41;margin:0;">[ FLAG SUBMISSION TERMINAL ]</h1>
<p style="color:#00ff41;font-size:14px;margin:20px 0;">> Enter extracted flag to verify access_</p>
<form method="POST" action="/submit">
<input type="text" name="flag" placeholder="FLAG{...}" style="width:90%;padding:12px;background:#000;color:#00ff41;border:1px solid #00ff41;font-family:monospace;font-size:16px;margin:10px 0;">
<br><button type="submit" style="width:90%;padding:12px;background:#00ff41;color:#000;border:none;font-family:monospace;font-weight:bold;font-size:16px;cursor:pointer;margin-top:10px;">>> SUBMIT <<</button>
</form>
{{MESSAGE}}
<p style="color:#666;font-size:12px;margin-top:30px;"><a href="/dashboard" style="color:#666;">[ RETURN TO DASHBOARD ]</a></p>
</div></body></html>"""

CYBERPUNK_SUCCESS_HTML = """<!DOCTYPE html>
<html>
<head>
<title>ACCESS GRANTED</title>
<style>
@keyframes flicker {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}
@keyframes glitch {
    0% { transform: translate(0); }
    20% { transform: translate(-2px, 2px); }
    40% { transform: translate(-2px, -2px); }
    60% { transform: translate(2px, 2px); }
    80% { transform: translate(2px, -2px); }
    100% { transform: translate(0); }
}
@keyframes scanline {
    0% { transform: translateY(-100%); }
    100% { transform: translateY(100vh); }
}
body {
    margin: 0;
    background: #0a0a0a;
    font-family: 'Courier New', monospace;
    color: #00ff41;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    position: relative;
}
body::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 255, 65, 0.03) 0px,
        rgba(0, 255, 65, 0.03) 1px,
        transparent 1px,
        transparent 2px
    );
    pointer-events: none;
    z-index: 10;
}
body::after {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: rgba(0, 255, 65, 0.3);
    animation: scanline 4s linear infinite;
    pointer-events: none;
    z-index: 11;
}
.container {
    text-align: center;
    z-index: 5;
    animation: flicker 2s infinite;
}
.skull {
    font-size: 120px;
    color: #ff003c;
    text-shadow: 0 0 20px #ff003c, 0 0 40px #ff003c, 0 0 60px #ff003c;
    margin: 0;
    animation: glitch 0.3s infinite;
    line-height: 1;
}
.title {
    font-size: 48px;
    color: #00ff41;
    text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41;
    margin: 20px 0;
    letter-spacing: 8px;
}
.subtitle {
    font-size: 18px;
    color: #ff003c;
    text-shadow: 0 0 8px #ff003c;
    margin: 10px 0;
    letter-spacing: 4px;
}
.flag-box {
    margin-top: 30px;
    padding: 20px;
    border: 2px dashed #00ff41;
    background: rgba(0, 255, 65, 0.05);
    display: inline-block;
}
.flag-text {
    font-size: 24px;
    color: #00ff41;
    text-shadow: 0 0 10px #00ff41;
    letter-spacing: 2px;
}
.corner {
    position: absolute;
    width: 30px;
    height: 30px;
    border: 2px solid #00ff41;
}
.tl { top: 20px; left: 20px; border-right: none; border-bottom: none; }
.tr { top: 20px; right: 20px; border-left: none; border-bottom: none; }
.bl { bottom: 20px; left: 20px; border-right: none; border-top: none; }
.br { bottom: 20px; right: 20px; border-left: none; border-top: none; }
.status {
    position: absolute;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 12px;
    color: #666;
    letter-spacing: 3px;
}
</style>
</head>
<body>
<div class="corner tl"></div>
<div class="corner tr"></div>
<div class="corner bl"></div>
<div class="corner br"></div>

<div class="container">
    <div class="skull">💀</div>
    <div class="title">GREAT JOB, HACKER</div>
    <div class="subtitle">[ SYSTEM BREACH SUCCESSFUL ]</div>
    <div class="flag-box">
        <div style="font-size:12px;color:#666;margin-bottom:10px;letter-spacing:2px;">EXTRACTED FLAG:</div>
        <div class="flag-text">FLAG{w4f_by_p4ss_m4st3r_v2}</div>
    </div>
</div>

<div class="status">>> CONNECTION SECURE // SESSION TERMINATED <<</div>
</body>
</html>"""

if __name__ == '__main__':
    httpd = HTTPServer(('', 8000), CTFHandler)
    print("=" * 50)
    print("CTFdpk Arena - Topic 4, Level 5 (Final Boss) Started!")
    print("Open: http://localhost:8000")
    print("=" * 50)
    httpd.serve_forever()
