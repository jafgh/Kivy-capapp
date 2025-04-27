import os
import threading
import time
import base64
import io
import random
import requests
from PIL import Image as PILImage
import numpy as np
import onnxruntime as ort
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage

# --------------------------------------------------
# ثوابت
# --------------------------------------------------
CHARSET = '0123456789abcdefghijklmnopqrstuvwxyz'
CHAR2IDX = {c: i for i, c in enumerate(CHARSET)}
IDX2CHAR = {i: c for c, i in CHAR2IDX.items()}
NUM_CLASSES = len(CHARSET)
NUM_POS = 5
ONNX_MODEL_PATH = os.path.join('assets', 'holako_bag.onnx')

# --------------------------------------------------
# معالجة الصورة لتكون متوافقة مع النموذج (3 قنوات) باستخدام Pillow وNumPy
# --------------------------------------------------
def preprocess_for_model(pil_img):
    # Resize to 224x224 and convert to RGB
    img = pil_img.resize((224, 224)).convert('RGB')
    # Convert to numpy array and scale to [0,1]
    arr = np.asarray(img).astype(np.float32) / 255.0
    # Normalize to [-1,1]
    arr = (arr - 0.5) / 0.5
    # Change from HWC to CHW format
    arr = np.transpose(arr, (2, 0, 1))
    # Add batch dimension: 1x3x224x224
    return arr[np.newaxis, :, :, :].astype(np.float32)

# --------------------------------------------------
# تصميم الواجهة باستخدام Kivy
# --------------------------------------------------
KV = '''
<CaptchaWidget>:
    orientation: 'vertical'
    padding: 10
    spacing: 10

    BoxLayout:
        size_hint_y: None
        height: '30dp'
        Label:
            id: notification_label
            text: ''
            font_size: 14
            color: 1,1,1,1
    Button:
        text: 'Add Account'
        size_hint_y: None
        height: '40dp'
        on_press: root.open_add_account_popup()

    BoxLayout:
        id: captcha_box
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height

    ScrollView:
        GridLayout:
            id: accounts_layout
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            row_default_height: '40dp'
            row_force_default: False
            spacing: 5

    Label:
        id: speed_label
        text: 'Preprocess: 0 ms | Predict: 0 ms'
        size_hint_y: None
        height: '30dp'
        font_size: 12
'''

class CaptchaWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.accounts = {}
        self.current_captcha = None
        # تحميل نموذج ONNX
        if not os.path.exists(ONNX_MODEL_PATH):
            self.show_error(f"ONNX model not found:\n{ONNX_MODEL_PATH}")
            return
        try:
            self.session_onnx = ort.InferenceSession(ONNX_MODEL_PATH, providers=['CPUExecutionProvider'])
        except Exception as e:
            self.show_error(f"Failed to load ONNX model:\n{e}")
            return

    def show_error(self, msg):
        popup = Popup(title='Error', content=Label(text=msg), size_hint=(0.8,0.4))
        popup.open()

    def update_notification(self, msg, color):
        def _update(dt):
            lbl = self.ids.notification_label
            lbl.text = msg
            lbl.color = color
            print(f"{color}: {msg}")
        Clock.schedule_once(_update, 0)

    def open_add_account_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        user_input = TextInput(hint_text='Username', multiline=False)
        pwd_input = TextInput(hint_text='Password', password=True, multiline=False)
        btn_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        btn_ok = Button(text='OK')
        btn_cancel = Button(text='Cancel')
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)
        content.add_widget(user_input)
        content.add_widget(pwd_input)
        content.add_widget(btn_layout)
        popup = Popup(title='Add Account', content=content, size_hint=(0.8,0.4))

        def on_ok(instance):
            user = user_input.text.strip()
            pwd = pwd_input.text.strip()
            popup.dismiss()
            if user and pwd:
                threading.Thread(target=self.add_account, args=(user, pwd)).start()

        btn_ok.bind(on_press=on_ok)
        btn_cancel.bind(on_press=lambda x: popup.dismiss())
        popup.open()

    def generate_user_agent(self):
        ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Mobile Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0"
        ]
        return random.choice(ua_list)

    def create_session_requests(self, ua):
        headers = {
            "User-Agent": ua,
            "Host": "api.ecsc.gov.sy:8443",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ar,en-US;q=0.7,en;q=0.3",
            "Referer": "https://ecsc.gov.sy/login",
            "Content-Type": "application/json",
            "Source": "WEB",
            "Origin": "https://ecsc.gov.sy",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Priority": "u=1",
        }
        sess = requests.Session()
        sess.headers.update(headers)
        return sess

    def add_account(self, user, pwd):
        session = self.create_session_requests(self.generate_user_agent())
        start = time.time()
        if not self.login(user, pwd, session):
            self.update_notification(f"Login failed for {user}", (1,0,0,1))
            return
        elapsed = time.time() - start
        self.update_notification(f"Logged in {user} in {elapsed:.2f}s", (0,1,0,1))
        self.accounts[user] = {"password": pwd, "session": session}
        proc = self.fetch_process_ids(session)
        if proc:
            Clock.schedule_once(lambda dt: self._create_account_ui(user, proc), 0)
        else:
            self.update_notification(f"Can't fetch process IDs for {user}", (1,0,0,1))

    def login(self, user, pwd, session, retries=3):
        url = "https://api.ecsc.gov.sy:8443/secure/auth/login"
        payload = {"username": user, "password": pwd}
        for _ in range(retries):
            try:
                r = session.post(url, json=payload, verify=False)
                if r.status_code == 200:
                    self.update_notification("Login successful.", (0,1,0,1))
                    return True
                else:
                    self.update_notification(f"Login failed ({r.status_code})", (1,0,0,1))
                    return False
            except Exception as e:
                self.update_notification(f"Login error: {e}", (1,0,0,1))
                return False
        return False

    def fetch_process_ids(self, session):
        url = "https://api.ecsc.gov.sy:8443/dbm/db/execute"
        payload = {"ALIAS": "OPkUVkYsyq", "P_USERNAME": "WebSite", "P_PAGE_INDEX": 0, "P_PAGE_SIZE": 100}
        headers = {"Content-Type": "application/json", "Alias": "OPkUVkYsyq", "Referer": "https://ecsc.gov.sy/requests", "Origin": "https://ecsc.gov.sy"}
        try:
            r = session.post(url, json=payload, headers=headers, verify=False)
            if r.status_code == 200:
                return r.json().get("P_RESULT", [])
            else:
                self.update_notification(f"Fetch IDs failed ({r.status_code})", (1,0,0,1))
        except Exception as e:
            self.update_notification(f"Error fetching IDs: {e}", (1,0,0,1))
        return []

    def _create_account_ui(self, user, processes):
        layout = self.ids.accounts_layout
        hdr = Label(text=f"Account: {user}", size_hint_y=None, height='25dp')
        layout.add_widget(hdr)
        for proc in processes:
            pid = proc.get("PROCESS_ID")
            name = proc.get("ZCENTER_NAME", "Unknown")
            box = BoxLayout(size_hint_y=None, height='40dp', spacing=5)
            btn = Button(text=name)
            prog = ProgressBar(max=1, value=0)
            box.add_widget(btn)
            box.add_widget(prog)
            layout.add_widget(box)
            btn.bind(on_press=lambda inst, u=user, p=pid, pr=prog: threading.Thread(target=self._handle_captcha, args=(u,p,pr)).start())

    def _handle_captcha(self, user, pid, prog):
        Clock.schedule_once(lambda dt: prog.start(), 0)
        data = self.get_captcha(self.accounts[user]["session"], pid, user)
        Clock.schedule_once(lambda dt: prog.stop(), 0)
        if data:
            self.current_captcha = (user, pid)
            self.show_captcha(data)

    def get_captcha(self, session, pid, user):
        url = f"https://api.ecsc.gov.sy:8443/captcha/get/{pid}"
        try:
            while True:
                r = session.get(url, verify=False)
                if r.status_code == 200:
                    return r.json().get("file")
                elif r.status_code == 429:
                    time.sleep(0.1)
                elif r.status_code in (401,403):
                    if not self.login(user, self.accounts[user]["password"], session):
                        return None
                else:
                    self.update_notification(f"Server error: {r.status_code}", (1,0,0,1))
                    return None
        except Exception as e:
            self.update_notification(f"Captcha error: {e}", (1,0,0,1))
            return None

    def show_captcha(self, b64data):
        self.ids.captcha_box.clear_widgets()
        b64 = b64data.split(',')[1] if ',' in b64data else b64data
        raw = base64.b64decode(b64)
        pil = PILImage.open(io.BytesIO(raw))
        frames = []
        try:
            while True:
                rgba = pil.convert("RGB")
                frames.append(np.array(rgba, dtype=np.uint8))
                pil.seek(pil.tell()+1)
        except EOFError:
            pass
        stack = np.stack(frames, axis=0)
        bg = np.median(stack, axis=0).astype(np.uint8)
        gray = (0.2989*bg[...,0] + 0.5870*bg[...,1] + 0.1140*bg[...,2]).astype(np.uint8)
        hist, _ = np.histogram(gray.flatten(), bins=256, range=(0,256))
        total = gray.size
        sum_total = np.dot(np.arange(256), hist)
        sumB = 0.0; wB = 0.0; max_var = 0.0; threshold = 0
        for i in range(256):
            wB += hist[i]
            if wB == 0: continue
            wF = total - wB
            if wF == 0: break
            sumB += i * hist[i]
            mB = sumB / wB
            mF = (sum_total - sumB) / wF
            varBetween = wB * wF * (mB - mF)**2
            if varBetween > max_var:
                max_var = varBetween
                threshold = i
        pil_gray = PILImage.fromarray(gray, mode='L')
        binary = pil_gray.point(lambda p: 255 if p > threshold else 0)
        data = io.BytesIO()
        binary.save(data, format='png')
        data.seek(0)
        img = CoreImage(data, ext='png')
        img_widget = Label(texture=img.texture, size_hint_y=None, height='90dp')
        self.ids.captcha_box.add_widget(img_widget)
        pred, pre_ms, pred_ms = self.predict_captcha(binary)
        self.update_notification(f"Predicted CAPTCHA: {pred}", (0,0,1,1))
        Clock.schedule_once(lambda dt: setattr(self.ids.speed_label, 'text', f"Preprocess: {pre_ms:.2f} ms | Predict: {pred_ms:.2f} ms"), 0)
        self.submit_captcha(pred)

    def predict_captcha(self, pil_img):
        start_pre = time.time()
        x = preprocess_for_model(pil_img)
        end_pre = time.time()
        start_pred = time.time()
        ort_outs = self.session_onnx.run(None, {'input': x})[0]
        end_pred = time.time()
        ort_outs = ort_outs.reshape(1, NUM_POS, NUM_CLASSES)
        idxs = np.argmax(ort_outs, axis=2)[0]
        pred = ''.join(IDX2CHAR[i] for i in idxs)
        pre_ms = (end_pre - start_pre) * 1000
        pred_ms = (end_pred - start_pred) * 1000
        return pred, pre_ms, pred_ms

    def submit_captcha(self, solution):
        user, pid = self.current_captcha
        session = self.accounts[user]["session"]
        url = f"https://api.ecsc.gov.sy:8443/rs/reserve?id={pid}&captcha={solution}"
        try:
            r = session.get(url, verify=False)
            color = (0,1,0,1) if r.status_code == 200 else (1,0,0,1)
            self.update_notification(f"Submit response: {r.text}", color)
        except Exception as e:
            self.update_notification(f"Submit error: {e}", (1,0,0,1))

class CaptchaApp(App):
    def build(self):
        Builder.load_string(KV)
        return CaptchaWidget()

if __name__ == '__main__':
    CaptchaApp().run()
