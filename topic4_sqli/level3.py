from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
import sqlite3
import urllib.parse
import html

FLAG = "FLAG{bl1nd_5ql1_m45t3r}"

 def init_db():
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    
     c.execute('CREATE TABLE employees (id INTEGER PRIMARY KEY, emp_id TEXT, name TEXT, password TEXT, role TEXT, department TEXT, status TEXT, secret_token TEXT)')
    
     c.execute("INSERT INTO employees VALUES (1, 'EMP001', 'John Smith', 'admin123', 'admin', 'IT Department', 'Active', ?)", (FLAG,))
    c.execute("INSERT INTO employees VALUES (2, 'EMP002', 'Jane Doe', 'pegawai123', 'employee', 'Human Resources', 'Active', 'null')")
    c.execute("INSERT INTO employees VALUES (3, 'EMP003', 'Bob Johnson', 'bob123', 'employee', 'Finance', 'Active', 'null')")
     c.execute("INSERT INTO employees VALUES (4, 'EMP004', 'Alice Wonderland', 'alice123', 'employee', 'Marketing', 'Inactive', 'null')")
    
    conn.commit()
    return conn

DB_CONN = init_db()

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
            dashboard = dashboard.replace('{{VERIFY_RESULT}}', '')  
            
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

        elif self.path == '/check_status':
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
            check_input = form_data.get('emp_id', [''])[0]
             
            query = f"SELECT 1 FROM employees WHERE emp_id = '{check_input}'"
            
            try:
                c = DB_CONN.cursor()
                c.execute(query)
                result = c.fetchone()
                
                 current_emp = cookie['session_emp'].value
                c.execute(f"SELECT name, role, department FROM employees WHERE emp_id='{current_emp}'")
                user = c.fetchone()
                
                dashboard = DASHBOARD_HTML.replace('{{NAME}}', html.escape(user[0]))
                dashboard = dashboard.replace('{{DEPARTMENT}}', html.escape(user[2]))
                dashboard = dashboard.replace('{{ROLE}}', user[1])
                
                if result:
                     
                    result_html = '<div style="margin-top:15px; padding:10px; background:#dcfce7; border:1px solid #22c55e; border-radius:4px; color:#166534; font-weight:600;">✔ Status: ACTIVE EMPLOYEE</div>'
                else:
                     
                    result_html = '<div style="margin-top:15px; padding:10px; background:#fee2e2; border:1px solid #ef4444; border-radius:4px; color:#991b1b; font-weight:600;"> Status: NOT FOUND / INACTIVE</div>'
                    
                dashboard = dashboard.replace('{{VERIFY_RESULT}}', result_html)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(dashboard.encode())
                
            except sqlite3.Error:
                 
                current_emp = cookie['session_emp'].value
                c.execute(f"SELECT name, role, department FROM employees WHERE emp_id='{current_emp}'")
                user = c.fetchone()
                
                dashboard = DASHBOARD_HTML.replace('{{NAME}}', html.escape(user[0]))
                dashboard = dashboard.replace('{{DEPARTMENT}}', html.escape(user[2]))
                dashboard = dashboard.replace('{{ROLE}}', user[1])
                dashboard = dashboard.replace('{{VERIFY_RESULT}}', '<div style="margin-top:15px; padding:10px; background:#fef08a; border:1px solid #eab308; border-radius:4px; color:#854d0e; font-weight:600;">⚠ Status: SYSTEM ERROR (Invalid Query Syntax)</div>')
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(dashboard.encode())
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
        .verify-box { display: flex; gap: 10px; margin-top: 15px; }
        .verify-box input { flex: 1; padding: 10px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 14px; }
        .verify-box button { padding: 10px 20px; background-color: #1e3a8a; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600; }
        .verify-box button:hover { background-color: #1e40af; }
        .sys-info { font-size: 12px; color: #94a3b8; margin-top: 10px; }
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
        <div class="card">
            <h3>Welcome, {{NAME}}</h3>
            <div class="info-grid">
                <div class="info-item"><label>Department</label><span>{{DEPARTMENT}}</span></div>
                <div class="info-item"><label>Access Role</label><span>{{ROLE}}</span></div>
            </div>
        </div>
        
        <div class="card">
            <h3>HR Verification Tool</h3>
            <p style="color:#64748b; font-size:14px; margin-bottom:15px;">Verify if an Employee ID is currently active in the system.</p>
            <form method="POST" action="/check_status">
                <div class="verify-box">
                    <input type="text" name="emp_id" placeholder="Enter Employee ID to verify (e.g., EMP002)" required>
                    <button type="submit">Verify Status</button>
                </div>
            </form>
            {{VERIFY_RESULT}}
            <div class="sys-info">System Info: DB Engine = SQLite 3.39.4 | Endpoint: /check_status</div>
        </div>
    </div>
    <!-- DEV NOTE: TODO: Add rate limiting to /check_status. Current implementation allows high-frequency automated requests. -->
</body>
</html>
"""

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CTFHandler)
    print("=" * 50)
    print("CTFdpk Arena - Topic 4, Level 3 (Blind SQLi) Started!")
    print("Open: http://localhost:8000")
    print("=" * 50)
    httpd.serve_forever()
