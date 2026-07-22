
import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

class TestSmartWasteBin(unittest.TestCase):
    def setUp(self):
        # --- 1. MOCK SERIAL ---
        self.mock_serial_module = MagicMock()
        self.mock_serial_tools = MagicMock()
        self.mock_list_ports = MagicMock()
        
        # Setup serial.Serial class
        self.mock_serial_instance = MagicMock()
        self.mock_serial_instance.is_open = True
        # Simulate: "Plastic: 10cm (66%)"
        self.mock_serial_instance.in_waiting = 50
        # New format: "Plastic: 20 cm"
        # 20cm means (30-20)/(30-10) = 10/20 = 50%
        self.mock_serial_instance.read.return_value = b'Plastic: 20 cm\nPaper: 30 cm\nGlass: 10 cm\n'
        
        self.mock_serial_module.Serial.return_value = self.mock_serial_instance
        
        # --- 2. MOCK CV2 ---
        self.mock_cv2 = MagicMock()
        # Ensure submodules don't crash
        self.mock_cv2.gapi.wip.draw = MagicMock()
        
        # Patch sys.modules
        self.sys_modules_patcher_serial = patch.dict(sys.modules, {
            'serial': self.mock_serial_module,
            'serial.tools': self.mock_serial_tools,
            'serial.tools.list_ports': self.mock_list_ports,
            'cv2': self.mock_cv2
        })
        
        self.sys_modules_patcher_serial.start()
        
        # Now we can import the app
        from app import create_app, db, User
        self.db = db
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # Create dummy user if not exists
            if not User.query.filter_by(email='test').first():
                user = User(email='test', location_lat=0, location_lng=0)
                user.set_password('test')
                db.session.add(user)
                db.session.commit()

    def tearDown(self):
        self.sys_modules_patcher_serial.stop()
        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()

    def login(self):
        return self.client.post('/login', data=dict(
            username='test',
            password='test'
        ), follow_redirects=True)

    def test_startup_and_login(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        
        response = self.login()
        self.assertIn(b'Logged in successfully', response.data)

    def test_status_endpoint(self):
        self.login()
        response = self.client.get('/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('bin_levels', data)

    def test_manual_control_beep(self):
        self.login()
        response = self.client.post('/manual_control', json={'action': 'beep'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'Command sent')
        self.assertIn('message', data)
    def test_manual_control_servo(self):
        self.login()
        response = self.client.post('/manual_control', json={'action': 'plastic'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('Opening Plastic', data['message'])

    def test_manual_control_invalid(self):
        self.login()
        response = self.client.post('/manual_control', json={'action': 'flying_car'})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
