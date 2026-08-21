from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
import sqlite3
import urllib.parse
import html

FLAG = "FLAG{st0r3d_xss_pr0f1l3}"

def init_db():
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, bio TEXT)')
    c.execute("INSERT INTO users VALUES (1, 'staff', 'staff123', 'Regular employee')")
    c.execute("INSERT INTO users VALUES (2, 'admin', 'admin123', 'System administrator')")
    conn.commit()
    return conn

DB = init_db()

class ProfileHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        
        if path == '/login' or path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(LOGIN_HTML.encode())
            return
        
        if path == '/profile':
            cookie = SimpleCookie()
            cookie.load(self.headers.get('Cookie', ''))
            
            if 'session' not in cookie:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            username = cookie['session'].value
            c = DB.cursor()
            c.execute("SELECT bio FROM users WHERE username=?", (username,))
            user = c.fetchone()
            
            if not user:
                self.send_response(404)
                self.end_headers()
                return
            
            bio = user[0]
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            profile_html = PROFILE_HTML.replace('{{USERNAME}}', username)
            profile_html = profile_html.replace('{{BIO}}', bio)
            
            if '<script>' in bio.lower() or 'alert(' in bio.lower():
                profile_html = profile_html.replace('{{FLAG_BOX}}', f'''
                <div style="background:#000;color:#00ff41;border:2px solid #00ff41;padding:20px;margin-top:20px;font-family:monospace;">
                    <h2>[✓] STORED XSS TRIGGERED</h2>
                    <p>Persistent XSS vulnerability confirmed in profile bio!</p>
                    <p style="font-size:18px;">FLAG: <strong>{FLAG}</strong></p>
                    <p style="color:#666;font-size:12px;">Proceed to Level 3: topic5_level3.py (Port 8003)</p>
                </div>
                ''')
            else:
                profile_html = profile_html.replace('{{FLAG_BOX}}', '<p style="color:#666;">Hint: Update your bio with JavaScript payload.</p>')
            
            self.wfile.write(profile_html.encode())
            return
        
        if path == '/edit':
            cookie = SimpleCookie()
            cookie.load(self.headers.get('Cookie', ''))
            
            if 'session' not in cookie:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            username = cookie['session'].value
            c = DB.cursor()
            c.execute("SELECT bio FROM users WHERE username=?", (username,))
            user = c.fetchone()
            bio = user[0] if user else ''
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(EDIT_HTML.replace('{{BIO}}', bio).encode())
            return
        
        if path == '/logout':
            self.send_response(302)
            self.send_header('Set-Cookie', 'session=; Path=/; Max-Age=0')
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
        
        if self.path == '/login':
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]
            
            c = DB.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            
            if user:
                self.send_response(302)
                self.send_header('Set-Cookie', f'session={username}; Path=/')
                self.send_header('Location', '/profile')
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(LOGIN_HTML.replace('{{ERROR}}', '<div style="color:red;text-align:center;">Invalid credentials</div>').encode())
        
        elif self.path == '/update_bio':
            cookie = SimpleCookie()
            cookie.load(self.headers.get('Cookie', ''))
            
            if 'session' not in cookie:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            username = cookie['session'].value
            bio = form_data.get('bio', [''])[0]
            
            c = DB.cursor()
            c.execute("UPDATE users SET bio=? WHERE username=?", (bio, username))
            DB.commit()
            
            self.send_response(302)
            self.send_header('Location', '/profile')
            self.end_headers()

    def log_message(self, format, *args):
        pass

LOGIN_HTML = """<!DOCTYPE html>
<html>
<head><title>CityNet - Login</title></head>
<body style="font-family:sans-serif;background:#f0f2f5;margin:0;padding:40px;">
<div style="max-width:400px;margin:0 auto;background:white;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    <h1 style="color:#1e3a8a;text-align:center;">CityNet Staff Portal</h1>
    {{ERROR}}
    <form method="POST" action="/login">
        <input type="text" name="username" placeholder="Username" style="width:100%;padding:10px;margin:10px 0;box-sizing:border-box;"><br>
        <input type="password" name="password" placeholder="Password" style="width:100%;padding:10px;margin:10px 0;box-sizing:border-box;"><br>
        <button type="submit" style="width:100%;padding:10px;background:#1e3a8a;color:white;border:none;">Login</button>
    </form>
    <p style="color:#999;font-size:12px;text-align:center;margin-top:20px;">Hint: Try staff/staff123</p>
</div>
</body>
</html>"""

PROFILE_HTML = """<!DOCTYPE html>
<html>
<head><title>Profile - {{USERNAME}}</title></head>
<body style="font-family:sans-serif;background:#f0f2f5;margin:0;padding:40px;">
<div style="max-width:600px;margin:0 auto;background:white;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    <h1 style="color:#1e3a8a;">Profile: {{USERNAME}}</h1>
    <div style="background:#f8fafc;padding:20px;border-radius:4px;margin:20px 0;">
        <h3>Bio:</h3>
        <p>{{BIO}}</p>
    </div>
    {{FLAG_BOX}}
    <a href="/edit" style="color:#1e3a8a;">Edit Profile</a> | 
    <a href="/logout" style="color:#1e3a8a;">Logout</a>
</div>
</body>
</html>"""

EDIT_HTML = """<!DOCTYPE html>
<html>
<head><title>Edit Profile</title></head>
<body style="font-family:sans-serif;background:#f0f2f5;margin:0;padding:40px;">
<div style="max-width:600px;margin:0 auto;background:white;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    <h1 style="color:#1e3a8a;">Edit Profile Bio</h1>
    <form method="POST" action="/update_bio">
        <textarea name="bio" placeholder="Tell us about yourself..." style="width:100%;padding:10px;border:1px solid #cbd5e1;border-radius:4px;min-height:100px;">{{BIO}}</textarea><br><br>
        <button type="submit" style="padding:10px 20px;background:#1e3a8a;color:white;border:none;">Update Bio</button>
    </form>
    <a href="/profile" style="color:#1e3a8a;">← Back to Profile</a>
</div>
</body>
</html>"""

if __name__ == '__main__':
    httpd = HTTPServer(('', 8002), ProfileHandler)
    print("=" * 50)
    print("Topic 5 - Level 2: Stored XSS (Profile Bio)")
    print("Open: http://localhost:8002")
    print("=" * 50)
    httpd.serve_forever()
