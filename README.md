# Raspberry Pi Surveillance Camera

This project implements a surveillance camera system using a Raspberry Pi, PiCamera, and motion detection with face recognition capabilities. It provides a web interface for live streaming and sends SMS notifications when an intrusion is detected.

## Features

- Live video streaming through a web interface
- Motion detection
- Face recognition
- SMS notifications on intrusion detection
- Mobile-responsive web design

## Requirements

- Raspberry Pi (with Raspbian OS)
- PiCamera module
- Python 3.x
- OpenCV
- Twilio account for SMS notifications

## Setup

1. Clone this repository to your Raspberry Pi.

2. Install the required Python packages:
   ```
   pip install picamera opencv-python-headless numpy twilio
   ```

3. Set up your Twilio account and obtain your account SID, auth token, and Twilio phone number.

4. Update the following variables in the script with your Twilio credentials:
   - `account_sid`
   - `auth_token`
   - `twilio_phone_number`
   - `recipient_phone_number`

5. Ensure the face cascade XML file is in the correct location:
   ```
   /home/pi/Downloads/IoT-and-Computing-Lab-main/haarcascade_frontalface_default.xml
   ```
   If the file is in a different location, update the `face_cascade_path` variable accordingly.

## Usage

1. Run the script:
   ```
   python surveillance_camera.py
   ```

2. Open a web browser and navigate to `http://<raspberry_pi_ip>:8000` to view the live stream.

3. The system will automatically detect motion and faces. When an intrusion is detected, you'll receive an SMS notification.

## Customization

- Adjust the `motion_threshold` value to change the sensitivity of motion detection.
- Modify the HTML/CSS in the `PAGE` variable to customize the web interface.

## Security Note

This script contains sensitive information (Twilio credentials). In a production environment, it's recommended to use environment variables or a separate configuration file to store these credentials securely.

## Contributing

Contributions to improve the project are welcome. Please feel free to submit a Pull Request.

## License

[MIT License](https://opensource.org/licenses/MIT)
