from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
import sqlite3
import urllib.parse
import html

FLAG = "FLAG{r34l_w0rld_sql1_b4s1cs}"

def init_db():
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('CREATE TABLE employees (id INTEGER PRIMARY KEY, emp_id TEXT, name TEXT, password TEXT, role TEXT, department TEXT)')
    
    c.execute("INSERT INTO employees VALUES (1, 'EMP001', 'John Smith', 'admin123', 'admin', 'IT Department')")
    c.execute("INSERT INTO employees VALUES (2, 'EMP002', 'Jane Doe', 'pegawai123', 'employee', 'Human Resources')")
    c.execute("INSERT INTO employees VALUES (3, 'EMP003', 'Bob Johnson', 'bob123', 'employee', 'Finance')")
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
            
            if user[1] == 'admin':
                dashboard = dashboard.replace('{{ADMIN_LINK}}', '<a href="/admin" style="color:white; text-decoration:none; margin-left:20px; font-size:14px;">[Admin Panel]</a>')
            else:
                dashboard = dashboard.replace('{{ADMIN_LINK}}', '')
                
            self.wfile.write(dashboard.encode())
            return
        
        if parsed_path.path == '/admin':
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
            c.execute(f"SELECT role FROM employees WHERE emp_id='{emp_id}'")
            role = c.fetchone()
            
            if not role or role[0] != 'admin':
                self.send_response(403)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(ACCESS_DENIED_HTML.encode())
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            admin_html = ADMIN_HTML.replace('{{FLAG}}', FLAG)
            self.wfile.write(admin_html.encode())
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
        <div class="footer">
            &copy; 2024 CityNet Corporation. All rights reserved.
        </div>
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
    </style>
</head>
<body>
    <div class="navbar">
        <h2>CityNet HR Portal - Dashboard</h2>
        <div class="nav-links">
            <a href="/dashboard">Home</a>
            <a href="#">Profile</a>
            <a href="#">Leave Request</a>
            {{ADMIN_LINK}}
            <a href="/logout">Logout</a>
        </div>
    </div>
    <div class="container">
        <div class="card">
            <h3>Welcome Back</h3>
            <p>Hello, <strong>{{NAME}}</strong>. You have successfully logged into the system.</p>
        </div>
        <div class="card">
            <h3>Employee Information</h3>
            <div class="info-grid">
                <div class="info-item">
                    <label>Department</label>
                    <span>{{DEPARTMENT}}</span>
                </div>
                <div class="info-item">
                    <label>Access Role</label>
                    <span>{{ROLE}}</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CityNet HR Portal - Admin Panel</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; }
        .navbar { background-color: #7f1d1d; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h2 { margin: 0; font-size: 20px; }
        .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .card h3 { color: #7f1d1d; margin-top: 0; }
        .flag-box { background: #fef2f2; border: 2px dashed #ef4444; padding: 20px; margin-top: 20px; text-align: center; }
        .flag-text { font-size: 24px; color: #991b1b; font-weight: bold; font-family: monospace; }
    </style>
</head>
<body>
    <div class="navbar">
        <h2>CityNet HR Portal - System Administration (Restricted)</h2>
        <div><a href="/dashboard" style="color:white; text-decoration:none;">Back to Dashboard</a></div>
    </div>
    <div class="container">
        <div class="card">
            <h3>System Management</h3>
            <p>You have full access as a System Administrator.</p>
            <div class="flag-box">
                <p>SYSTEM FLAG (Simulated Confidential Data):</p>
                <div class="flag-text">{{FLAG}}</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

ACCESS_DENIED_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Access Denied</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .error-box { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; max-width: 400px; }
        .error-box h1 { color: #ef4444; margin: 0 0 10px; }
        .error-box p { color: #64748b; }
        .error-box a { color: #1e3a8a; text-decoration: none; font-weight: 600; }
    </style>
</head>
<body>
    <div class="error-box">
        <h1>403 - Access Denied</h1>
        <p>You do not have permission to access this page.</p>
        <p><a href="/dashboard">Return to Dashboard</a></p>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CTFHandler)
    print("=" * 50)
    print("CTFdpk Arena - Topic 4, Level 1 (Realistic SQLi) Started!")
    print("Open: http://localhost:8000")
    print("=" * 50)
    httpd.serve_forever()
