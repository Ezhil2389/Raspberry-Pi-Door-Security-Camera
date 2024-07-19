from http.server import BaseHTTPRequestHandler, HTTPServer
import io
import logging
from threading import Condition
from picamera import PiCamera
import numpy as np
import cv2
from twilio.rest import Client

# Twilio credentials
account_sid = 'Enter Your ID'
auth_token = 'Enter Your Token'
twilio_phone_number = '+17082942639'
recipient_phone_number = '+919042006514'  # Replace with the recipient's phone number

def send_sms(message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=twilio_phone_number,
        to=recipient_phone_number
    )
    print(f"Message sent successfully! SID: {message.sid}")

# HTML content for the streaming page
PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raspberry Pi Surveillance Camera</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f8f0e5;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }

        header {
            background-color: #0f2c59;
            color: #dac0a3;
            text-align: center;
            padding: 1em;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            transition: background-color 0.3s, color 0.3s;
            cursor: pointer;
        }

        header:hover {
            background-color: #1b3b6f;
            color: #f8f0e5;
        }

        h1 {
            margin-bottom: 0.5em;
        }

        main {
            background-color: #f8f0e5;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            align-items: center;
            transition: background-color 0.3s;
        }

        main:hover {
            background-color: #f0e8d8; /* A slightly different shade */
        }

        figure {
            margin-bottom: 20px;
        }

        img {
            display: block;
            margin: 0 auto;
            max-width: 100%;
            height: auto;
            border: 2px solid #1b3b6f;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
        }

        img:hover {
            transform: scale(1.05);
        }

        #notification {
            text-align: center;
            font-size: 1.2em;
            color: #e44d26;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <header>
        <h1>Doorbell Camera Feed</h1>
    </header>

    <main>
        <figure>
            <img src="stream.mjpg" alt="Surveillance Stream">
        </figure>

        <p id="notification"></p>
    </main>
</body>
</html>

"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.detect_intrusion(frame)

            except Exception as e:
                logging.warning('Removed streaming client %s: %s', self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

    def detect_intrusion(self, frame):
        global prev_frame
        global motion_threshold

        if prev_frame is None:
            prev_frame = frame
            return

        frame_np = np.frombuffer(frame, dtype=np.uint8)
        frame_np = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)

        prev_frame_np = np.frombuffer(prev_frame, dtype=np.uint8)
        prev_frame_np = cv2.imdecode(prev_frame_np, cv2.IMREAD_COLOR)

        diff = np.abs(frame_np - prev_frame_np)
        total_diff = np.sum(diff)

        if total_diff > motion_threshold:
            gray_frame = cv2.cvtColor(frame_np, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)

            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame_np, (x, y), (x + w, y + h), (0, 255, 0), 2)
                self.send_notification()

        _, encoded_frame = cv2.imencode('.jpg', frame_np)
        self.wfile.write(b'--FRAME\r\n')
        self.send_header('Content-Type', 'image/jpeg')
        self.send_header('Content-Length', len(encoded_frame))
        self.end_headers()
        self.wfile.write(encoded_frame.tobytes())
        self.wfile.write(b'\r\n')

        prev_frame = frame

    def send_notification(self):
        notification_script = b'<script>showNotification();</script>'
        self.wfile.write(notification_script)
        send_sms("Intrusion Detected!")

if __name__ == '__main__':
    with PiCamera(resolution='640x480', framerate=15) as camera:
        output = StreamingOutput()
        camera.rotation = 180
        camera.start_recording(output, format='mjpeg')

        prev_frame = None
        motion_threshold = 10000

        face_cascade_path = '/home/pi/Downloads/IoT-and-Computing-Lab-main/haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(face_cascade_path)

        try:
            address = ('', 8000)
            server = HTTPServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            camera.stop_recording()
