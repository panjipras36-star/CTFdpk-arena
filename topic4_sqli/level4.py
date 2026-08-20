from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
import sqlite3
import urllib.parse
import html
import re

FLAG = "FLAG{w4f_by_p4ss_m4st3r}"


def init_db():
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    
    c.execute('CREATE TABLE employees (id INTEGER PRIMARY KEY, emp_id TEXT, name TEXT, password TEXT, role TEXT, department TEXT)')
    c.execute("INSERT INTO employees VALUES (1, 'EMP001', 'John Smith', 'admin123', 'admin', 'IT Department')")
    c.execute("INSERT INTO employees VALUES (2, 'EMP002', 'Jane Doe', 'pegawai123', 'employee', 'Human Resources')")
    c.execute("INSERT INTO employees VALUES (3, 'EMP003', 'Bob Johnson', 'bob123', 'employee', 'Finance')")
    
    c.execute('CREATE TABLE system_config (id INTEGER PRIMARY KEY, config_name TEXT, config_value TEXT)')
    c.execute("INSERT INTO system_config VALUES (1, 'db_version', 'SQLite 3.39.4')")
    c.execute(f"INSERT INTO system_config VALUES (2, 'system_flag', '{FLAG}')")
    
    conn.commit()
    return conn

DB_CONN = init_db()


def waf_check(input_str):
    """Simulasi WAF yang memblokir karakter dan kata kunci tertentu."""
    # Aturan 1: Blokir Spasi
    if ' ' in input_str:
        return False
    
    # Aturan 2: Blokir kata kunci AND dan OR (case-insensitive)
    # Menggunakan regex word boundary untuk menghindari false positive (misal: 'android')
    lower_input = input_str.lower()
    if re.search(r'\band\b', lower_input) or re.search(r'\bor\b', lower_input):
        return False
        
    return True

class CTFHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/logout':
            self.send_response(302)
            self.send_header('Set-Cookie', 'session_emp=; Path=/; Max-Age=0')
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
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            
            if 'session_emp' not in cookie:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            emp_id = cookie['session_emp'].value
            c = DB_CONN.cursor()
            c.execute(f"SELECT name, role, department FROM employees WHERE emp_id='{emp_id}'")
            user = c.fetchone()
            
            if not user:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            dashboard = DASHBOARD_HTML.replace('{{NAME}}', html.escape(user[0]))
            dashboard = dashboard.replace('{{DEPARTMENT}}', html.escape(user[2]))
            dashboard = dashboard.replace('{{ROLE}}', user[1])
            dashboard = dashboard.replace('{{SEARCH_RESULTS}}', '<p style="color:#94a3b8; font-style:italic; margin-top:20px; font-size:14px;">Enter an Employee ID above to search the directory.</p>')
                
            self.wfile.write(dashboard.encode())
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
            
            # WAF Check pada input login
            if not waf_check(emp_id) or not waf_check(password):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_html = LOGIN_HTML.replace('<!-- ERROR_MSG -->', '<div style="background:#fee2e2; color:#991b1b; padding:10px; border-radius:4px; margin-bottom:20px; text-align:center;">[!] WAF ALERT: Malicious input detected. Request blocked.</div>')
                self.wfile.write(error_html.encode())
                return

            query = f"SELECT * FROM employees WHERE emp_id='{emp_id}' AND password='{password}'"
            
            try:
                c = DB_CONN.cursor()
                c.execute(query)
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
                    error_html = LOGIN_HTML.replace('<!-- ERROR_MSG -->', '<div style="background:#fee2e2; color:#991b1b; padding:10px; border-radius:4px; margin-bottom:20px; text-align:center;">Invalid Employee ID or Password.</div>')
                    self.wfile.write(error_html.encode())
            except sqlite3.Error:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_html = LOGIN_HTML.replace('<!-- ERROR_MSG -->', '<div style="background:#fee2e2; color:#991b1b; padding:10px; border-radius:4px; margin-bottom:20px; text-align:center;">System Error Occurred.</div>')
                self.wfile.write(error_html.encode())

        elif self.path == '/search':
            cookie_header = self.headers.get('Cookie', '')
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            
            if 'session_emp' not in cookie:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            search_input = form_data.get('query', [''])[0]
            
            # WAF Check pada input pencarian
            if not waf_check(search_input):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                current_emp = cookie['session_emp'].value
                c = DB_CONN.cursor()
                c.execute(f"SELECT name, role, department FROM employees WHERE emp_id='{current_emp}'")
                user = c.fetchone()
                
                dashboard = DASHBOARD_HTML.replace('{{NAME}}', html.escape(user[0]))
                dashboard = dashboard.replace('{{DEPARTMENT}}', html.escape(user[2]))
                dashboard = dashboard.replace('{{ROLE}}', user[1])
                dashboard = dashboard.replace('{{SEARCH_RESULTS}}', '<div style="background:#fee2e2; color:#991b1b; padding:15px; border-radius:4px; margin-top:20px; border:1px solid #ef4444;"><strong>[!] WAF BLOCKED:</strong> Your search query was flagged as malicious. Common SQL keywords and spaces are not allowed.</div>')
                self.wfile.write(dashboard.encode())
                return

            # --- VULNERABLE BACKEND (UNION INJECTION) ---
            query = f"SELECT emp_id, name, department FROM employees WHERE emp_id = '{search_input}'"
            
            try:
                c = DB_CONN.cursor()
                c.execute(query)
                results = c.fetchall()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                current_emp = cookie['session_emp'].value
                c.execute(f"SELECT name, role, department FROM employees WHERE emp_id='{current_emp}'")
                user = c.fetchone()
                
                dashboard = DASHBOARD_HTML.replace('{{NAME}}', html.escape(user[0]))
                dashboard = dashboard.replace('{{DEPARTMENT}}', html.escape(user[2]))
                dashboard = dashboard.replace('{{ROLE}}', user[1])
                
                search_html = "<div style='margin-top:20px;'><h4 style='color:#1e3a8a; margin-bottom:10px;'>Search Results:</h4>"
                search_html += "<table style='width:100%; border-collapse: collapse; background:white; border-radius:4px; overflow:hidden;'><tr style='background:#f1f5f9;'><th style='padding:12px; border-bottom:2px solid #e2e8f0; text-align:left; color:#64748b; font-size:12px;'>EMPLOYEE ID</th><th style='padding:12px; border-bottom:2px solid #e2e8f0; text-align:left; color:#64748b; font-size:12px;'>NAME</th><th style='padding:12px; border-bottom:2px solid #e2e8f0; text-align:left; color:#64748b; font-size:12px;'>DEPARTMENT</th></tr>"
                
                if results:
                    for row in results:
                        search_html += f"<tr><td style='padding:12px; border-bottom:1px solid #e2e8f0; color:#0f172a;'>{html.escape(str(row[0]))}</td><td style='padding:12px; border-bottom:1px solid #e2e8f0; color:#0f172a;'>{html.escape(str(row[1]))}</td><td style='padding:12px; border-bottom:1px solid #e2e8f0; color:#0f172a;'>{html.escape(str(row[2]))}</td></tr>"
                else:
                    search_html += "<tr><td colspan='3' style='padding:15px; text-align:center; color:#64748b;'>No employee found with that ID.</td></tr>"
                
                search_html += "</table></div>"
                dashboard = dashboard.replace('{{SEARCH_RESULTS}}', search_html)
                self.wfile.write(dashboard.encode())
                
            except sqlite3.Error as e:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                current_emp = cookie['session_emp'].value
                c.execute(f"SELECT name, role, department FROM employees WHERE emp_id='{current_emp}'")
                user = c.fetchone()
                
                dashboard = DASHBOARD_HTML.replace('{{NAME}}', html.escape(user[0]))
                dashboard = dashboard.replace('{{DEPARTMENT}}', html.escape(user[2]))
                dashboard = dashboard.replace('{{ROLE}}', user[1])
                dashboard = dashboard.replace('{{SEARCH_RESULTS}}', f'<div style="background:#fee2e2; color:#991b1b; padding:15px; border-radius:4px; margin-top:20px; font-size:14px;">Database Error: {html.escape(str(e))}</div>')
                self.wfile.write(dashboard.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[SERVER LOG] {format % args}")

# --- HTML TEMPLATES ---
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CityNet HR Portal - Login</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .login-container { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #1e3a8a; margin: 0; font-size: 24px; }
        .header p { color: #64748b; margin: 5px 0 0; font-size: 14px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #334155; font-weight: 600; font-size: 14px; }
        .form-group input { width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
        .form-group input:focus { outline: none; border-color: #1e3a8a; box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.1); }
        button { width: 100%; padding: 12px; background-color: #1e3a8a; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
        button:hover { background-color: #1e40af; }
        .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #94a3b8; }
        .dev-note { text-align: center; margin-top: 15px; font-size: 11px; color: #cbd5e1; font-style: italic; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="header">
            <h1>CityNet HR Portal</h1>
            <p>Employee Management System</p>
        </div>
        <!-- ERROR_MSG -->
        <form method="POST" action="/login">
            <div class="form-group">
                <label>Employee ID</label>
                <input type="text" name="emp_id" required placeholder="Enter your Employee ID">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required placeholder="Enter your Password">
            </div>
            <button type="submit">Sign In</button>
        </form>
        
        <!-- HINT 4 WORDS: Simulasi Default Credentials / Info Disclosure -->
        <div class="dev-note">QA test: EMP002 Employee123</div>
        
        <div class="footer">&copy; 2024 CityNet Corporation. All rights reserved.</div>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CityNet HR Portal - Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; }
        .navbar { background-color: #1e3a8a; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h2 { margin: 0; font-size: 20px; }
        .nav-links a { color: white; text-decoration: none; margin-left: 20px; font-size: 14px; }
        .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .card h3 { color: #1e3a8a; margin-top: 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .info-item { margin-bottom: 15px; }
        .info-item label { display: block; color: #64748b; font-size: 12px; margin-bottom: 5px; }
        .info-item span { color: #0f172a; font-weight: 600; font-size: 16px; }
        .search-box { display: flex; gap: 10px; margin-top: 15px; }
        .search-box input { flex: 1; padding: 10px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 14px; }
        .search-box button { padding: 10px 20px; background-color: #1e3a8a; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600; }
        .search-box button:hover { background-color: #1e40af; }
        .waf-banner { background: #fef08a; border: 1px solid #eab308; color: #854d0e; padding: 10px 15px; border-radius: 4px; margin-bottom: 20px; font-size: 13px; font-weight: 600; }
        details { margin-top: 20px; border-top: 1px solid #e2e8f0; padding-top: 10px; }
        summary { color: #1e3a8a; cursor: pointer; font-weight: 600; font-size: 14px; }
        .hint-text { color: #64748b; margin-top: 10px; font-size: 13px; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="navbar">
        <h2>CityNet HR Portal</h2>
        <div class="nav-links">
            <a href="/dashboard">Home</a>
            <a href="#">Profile</a>
            <a href="/logout">Logout</a>
        </div>
    </div>
    <div class="container">
        <div class="waf-banner">[!] SECURITY NOTICE: Web Application Firewall (WAF) is active. Malicious patterns will be blocked.</div>
        <div class="card">
            <h3>Welcome, {{NAME}}</h3>
            <div class="info-grid">
                <div class="info-item"><label>Department</label><span>{{DEPARTMENT}}</span></div>
                <div class="info-item"><label>Access Role</label><span>{{ROLE}}</span></div>
            </div>
        </div>
        
        <div class="card">
            <h3>Employee Directory Search</h3>
            <p style="color:#64748b; font-size:14px; margin-bottom:15px;">Search for employee details by their Employee ID.</p>
            <form method="POST" action="/search">
                <div class="search-box">
                    <input type="text" name="query" placeholder="Enter Employee ID (e.g., EMP001)" required>
                    <button type="submit">Search</button>
                </div>
            </form>
            {{SEARCH_RESULTS}}
        </div>

        <details>
            <summary>[?] System Hints</summary>
            <div class="hint-text">
                > HINT 1: The WAF blocks standard spaces and common logical operators (AND, OR).<br>
                > HINT 2: SQL has alternative ways to represent spaces (using comments) and alternative logical operators supported by SQLite.<br>
                > HINT 3: The flag is stored in the 'system_config' table. You need to extract it using a UNION-based injection.
            </div>
        </details>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CTFHandler)
    print("=" * 50)
    print("CTFdpk Arena - Topic 4, Level 4 (WAF Bypass) Started!")
    print("Open: http://localhost:8000")
    print("=" * 50)
    httpd.serve_forever()
