# quick mjpeg stream of the car camera, served on port 8080
import threading, time, signal, sys, rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

frame = None

class Sub(Node):
    def __init__(self):
        super().__init__('stream')
        self.create_subscription(CompressedImage, '/color/image/compressed', self.cb, 1)
    def cb(self, msg):
        global frame
        frame = bytes(msg.data)

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=f')
        self.end_headers()
        try:
            while True:
                if frame:
                    self.wfile.write(b'--f\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(0.03)
        except (BrokenPipeError, ConnectionResetError):
            pass  # browser tab closed
    def log_message(self, *a):
        pass  # dont spam the terminal

# dont let ros grab ctrl+c, otherwise it kills ros but the web server keeps going
rclpy.init(signal_handler_options=rclpy.signals.SignalHandlerOptions.NO)
signal.signal(signal.SIGTERM, lambda *a: sys.exit(0))  # kill -> exit cleanly too
node = Sub()
threading.Thread(target=rclpy.spin, args=(node,), daemon=True).start()
try:
    ThreadingHTTPServer(('0.0.0.0', 8080), H).serve_forever()
except (KeyboardInterrupt, SystemExit):
    pass
rclpy.shutdown()
