from waitress import serve
from app import app
import socket

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    ip = get_ip_address()
    port = 5000
    print(f"Starting server on http://{ip}:{port}")
    print(f"You can also access it via http://localhost:{port}")
    serve(app, host='0.0.0.0', port=port)
