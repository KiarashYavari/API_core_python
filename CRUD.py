import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3

# In-memory SQLite database
# conn = sqlite3.connect(':memory:', check_same_thread=False)
# cursor = conn.cursor()

# check_same_thread=False -> Allow multiple threads to use the same database connection 
# On HDD sqlite DB for data persistance
conn = sqlite3.connect('users.db', check_same_thread=True)
cursor = conn.cursor()

# Create a users table
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
               (id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')
conn.commit()

# Helper function to convert users to JSON
def users_to_json(users):
    print(users)
    return json.dumps([{'id': user[0], 'name': user[1], 'email': user[2]} for user in users])

class CRUDHandler(BaseHTTPRequestHandler):
    
    # Parse request body
    def parse_request_body(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        return json.loads(body)
    
    def error_404_msg(self):
        return json.dumps({'Error': 'User Not found'})
    
    # Handle GET requests
    def do_GET(self):
        if self.path == "/users":
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(users_to_json(users).encode())
        else:
            self.send_response(404)
            self.end_headers()

    # Handle POST requests (Create)
    def do_POST(self):
        if self.path == "/users":
            try:
                data = self.parse_request_body()
                cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (data['name'], data['email']))
                conn.commit()
                self.send_response(201)
                self.end_headers()
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        else:
            self.send_response(404)
            self.end_headers()

    # Handle PUT requests (Update)
    def do_PUT(self):
        if self.path.startswith("/users/"):
            try:
                user_id = int(self.path.split("/")[-1])
                data = self.parse_request_body()
                cursor.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (data['name'], data['email'], user_id))
                conn.commit()
                if cursor.rowcount == 0:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(self.error_404_msg().encode())
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'msg':'User updated successfully!'}).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(f"Error: please send {str(e)} too!".encode())
                
        else:
            self.send_response(404)
            self.end_headers()
            

    # Handle DELETE requests (Delete)
    def do_DELETE(self):
        if self.path.startswith("/users/"):
            try:
                user_id = int(self.path.split("/")[-1])
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                if cursor.rowcount == 0:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(self.error_404_msg().encode())
                else:
                    self.send_response(204)
                    self.end_headers()
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=CRUDHandler, port=8000):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on  http://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
