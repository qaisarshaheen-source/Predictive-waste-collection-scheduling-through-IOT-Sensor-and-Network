# Smart Waste Bin — Predictive Waste Collection Scheduling Through IoT Sensor and Network

A Flask web application that pairs an Arduino-based smart bin (ultrasonic fill-level sensors + servo-controlled compartments) with a webcam and an AI image classifier to automatically sort waste into **plastic**, **paper**, and **glass** compartments, track fill levels in real time, and email alerts when a bin is nearly full.

> **Note:** This README was generated from a direct analysis of the source code, since the repository does not currently include one.

## How it works

1. A webcam frame is captured and sent to an image classifier (OpenAI GPT-4 Vision) to identify the waste type. If no OpenAI API key is configured, the app falls back to a **dummy mode** that picks a class at random so the rest of the pipeline can still be tested.
2. The classification result is mapped to a serial command (`PLASTIC`, `PAPER`, `GLASS`) and sent over USB to an Arduino, which is expected to open the matching compartment's servo.
3. The Arduino also reports back ultrasonic distance readings per compartment (e.g. `Plastic: 10 cm`), which the app parses and converts into a 0–100% fill level.
4. When a compartment's fill level crosses 90%, the app emails an alert (with a cooldown to avoid spamming).
5. A Flask web dashboard shows the live camera feed, current fill levels, manual override buttons per compartment, and a history of past scans, behind a login system.

## Features

- Live MJPEG camera stream with on/off toggle
- AI-based waste classification (OpenAI Vision API) with an offline dummy fallback
- Serial communication with an Arduino for bin actuation and ultrasonic level readings
- Real-time bin fill-level tracking and threshold-based email alerts (SMTP/Gmail)
- Manual compartment control from the UI
- User accounts (register/login/logout) with per-user geolocation captured at login (reverse-geocoded via OpenStreetMap Nominatim)
- Scan history log (SQLite via SQLAlchemy)
- Standalone debug/test scripts for serial ports, SMTP, and calibration

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-Login, Flask-SQLAlchemy |
| Database | SQLite |
| Computer vision | OpenCV (`cv2`) |
| AI classification | OpenAI API (GPT-4 Vision) |
| Hardware link | `pyserial` (Arduino over USB) |
| Alerts | SMTP (Gmail) |
| Frontend | Jinja2 templates, vanilla JS/CSS |

## Repository structure

```
.
├── app.py                 # Flask app factory, all routes
├── config.py               # App/hardware/email configuration
├── models.py                # SQLAlchemy models: User, ScanLog, BinAlert
├── check_ports.py           # Lists available serial ports
├── debug_serial.py          # Serial module sanity check
├── debug_email_real.py      # Standalone SMTP send test (uses config.py values)
├── test_smtp.py             # Standalone SMTP send test (hardcoded credentials)
├── test_suite.py            # Test runner
├── utils.rar                # utils/ package: serial_handler.py, ai_detector.py, email_utils.py
├── static.rar                # static/ assets: script.js, style.css
├── templates.rar             # templates/: index, login, register, dashboard, history, about, base
└── tests.rar                 # tests/: test_calibration.py, test_email.py
```

> **The `utils`, `static`, `templates`, and `tests` folders are committed as `.rar` archives, not as plain folders.** You'll need to extract them (e.g. with `unrar` or 7-Zip) before running the app, so that `utils/`, `static/`, and `templates/` exist as real directories next to `app.py`.

## Hardware requirements

- Arduino (or compatible board) connected over USB, running firmware that:
  - Accepts `PLASTIC\n`, `PAPER\n`, `GLASS\n`, `BEEP\n` commands to drive servos
  - Streams ultrasonic distance readings as lines like `Plastic: 10 cm`
  - **No Arduino sketch (`.ino`) is included in this repo** — you'll need to write/supply the firmware yourself to match this protocol.
- Ultrasonic distance sensors, one per compartment
- Servos to open/close each compartment
- A webcam accessible to OpenCV as device `0`

## Setup

1. **Clone and extract archives**
   ```bash
   git clone https://github.com/qaisarshaheen-source/Predictive-waste-collection-scheduling-through-IOT-Sensor-and-Network.git
   cd Predictive-waste-collection-scheduling-through-IOT-Sensor-and-Network
   unrar x utils.rar
   unrar x static.rar
   unrar x templates.rar
   unrar x tests.rar
   ```

2. **Install dependencies**

   There is no `requirements.txt` in the repo. Based on the imports used, install:
   ```bash
   pip install flask flask-login flask-sqlalchemy werkzeug opencv-python requests numpy pyserial openai
   ```

3. **Configure environment variables**

   `config.py` reads these from the environment (with defaults for local dev):

   | Variable | Purpose | Default |
   |---|---|---|
   | `ARDUINO_PORT` | Serial port for the Arduino | `COM7` |
   | `OPENAI_API_KEY` | Enables real AI classification (unset = dummy mode) | unset |
   | `SECRET_KEY` | Flask session secret | `dev-key-change-in-prod` |
   | `MAIL_USERNAME` | Gmail account used to send alerts | Add a gmail to send alerts |
   | `MAIL_PASSWORD` | Gmail app password | Add App password  |
   | `MAIL_DEFAULT_SENDER` | From address for alert emails | Add a gmail to recieve alerts |
   | `ALERT_EMAIL_RECIPIENT` | Where alerts are sent | Add a gmail to recieve alerts |

4. **Run**
   ```bash
   python app.py
   ```
   The app creates `users.db` (SQLite) on first run and starts at `http://127.0.0.1:5000`.

## Routes

| Route | Method(s) | Description |
|---|---|---|
| `/register`, `/login`, `/logout` | GET/POST | Auth |
| `/` | GET | Dashboard (login required) |
| `/video_feed` | GET | MJPEG camera stream |
| `/toggle_camera` | POST | Turn the camera on/off |
| `/detect_waste` | POST | Capture a frame, classify it, actuate the servo, log the scan |
| `/manual_control` | POST | Manually trigger a compartment (`plastic`/`paper`/`glass`/`beep`/`reset`) |
| `/status` | GET | Current fill levels, last classification, active alerts |
| `/history` | GET | Last 50 scans |
| `/about` | GET | About page |
| `/test_email` | GET | Sends a test alert email |

## Testing

```bash
python -m unittest tests/test_calibration.py
python -m unittest tests/test_email.py
```
`test_calibration.py` verifies the distance-to-fill-percentage math in `serial_handler.py`; `test_email.py` mocks `smtplib` to verify alert sending and cooldown logic.



