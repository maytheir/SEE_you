from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.properties import StringProperty
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.audio import SoundLoader

from tools.facial_emotion_detect import FER
from tools.memory import cls_memory
from tools.clova_stt import ClovaSpeechClient
import time
import tools.voice_emotion

class ImageButton(ButtonBehavior, Image):
    pass

LabelBase.register(name='Gulim', fn_regular='font/gulim.ttc')

mem = cls_memory()
res = ClovaSpeechClient()
detector = FER()
voice = tools.voice_emotion.vocal_emotion()

class MyApp(App):
    image_source = StringProperty('icon/stop.png')
    camera_image_source = StringProperty('icon/start_camera.png')
    
    def build(self):
        self.voice_thread = None
        self.que = ""
        self.current_emotion = ""
        self.vocal_emotion = ""

        self.recoding = False
        self.text = mem.read_memory()
        self.new_com = ""
        self.camera_activate = True

        # 메인 레이아웃 생성
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        top_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1), padding=10, spacing=30)

        # 스크롤뷰 생성
        self.scroll_view = ScrollView(size_hint=(0.9, 1))
        with self.scroll_view.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.scroll_view.size, pos=self.scroll_view.pos)

        self.label_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.label_layout.bind(minimum_height=self.label_layout.setter('height'))
        self.scroll_view.add_widget(self.label_layout)

        # 오른쪽 위 버튼 레이아웃
        top_right_layout = BoxLayout(orientation='vertical', size_hint=(0.2, 1), padding=(20, 10, 10, 10), spacing=10)

        # 종료 버튼
        exit_button = ImageButton(
            source='icon/exit.png',
            size_hint=(1, 0.2),
            keep_ratio=True,
            allow_stretch=True
        )
        exit_button.bind(on_press=self.stop)

        # 녹음 버튼
        self.recode_img = ImageButton(
            source=self.image_source,
            size_hint=(1, 0.2),
            allow_stretch=True,
            keep_ratio=True
        )
        self.recode_img.bind(on_press=self.recod_on_button_click)

        # 카메라 버튼
        self.cam_button = ImageButton(
            source=self.camera_image_source,
            size_hint=(1, 0.2),
            allow_stretch=True,
            keep_ratio=True
        )
        self.cam_button.bind(on_press=self.toggle_camera_lock)

        top_right_layout.add_widget(exit_button)
        top_right_layout.add_widget(self.recode_img)
        top_right_layout.add_widget(self.cam_button)

        top_layout.add_widget(self.scroll_view)
        top_layout.add_widget(top_right_layout)

        layout.add_widget(top_layout)
        self.scroll_view.bind(size=self._update_rect, pos=self._update_rect)

        return layout

    def change_image(self, *args):
        if self.image_source == 'icon/stop.png':
            self.image_source = 'icon/recoding.png'
        else:
            self.image_source = 'icon/stop.png'
            
    def change_camera_image(self, *args):
        if self.camera_image_source == 'icon/start_camera.png':
            self.camera_image_source = 'icon/stop_camera.png'
        else:
            self.camera_image_source = 'icon/start_camera.png'

    def on_image_source(self, instance, value):
        # image_source가 변경될 때마다 Image 위젯의 source를 업데이트
        self.recode_img.source = self.image_source
        
    def on_camera_image_source(self, instance, value):
        # camera_image_source가 변경될 때마다 Image 위젯의 source를 업데이트
        self.cam_button.source = self.camera_image_source

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def stop(self, *args):
        self.recoding = False
        
        res.stop_recording()
        detector.stop_camera()
        
        mem.simple_save_memory(self.new_com)
        self._stop()

    def scroll(self, label):
        if self.label_layout.height > self.scroll_view.height:
            self.scroll_view.scroll_to(self.anser_label)

    def recod_on_button_click(self, instance):
        self.recoding = not self.recoding
        self.change_image()

        if self.recoding:
            res.start_recording()
            if self.camera_activate:
                detector.start_camera()
        else:
            self.que = res.stop_recording()
            self.vocal_emotion = voice.vocal_prossing()
            if self.camera_activate:
                self.current_emotion = detector.stop_camera()

            self.comunity(text=self.que, current_emotion=self.current_emotion, vocal_emotion=self.vocal_emotion)
            self.re()
        
        time.sleep(0.3)

    def re(self):
        "감정 데이터 및 텍스트 초기화 함수"
        self.que = ""
        self.current_emotion = ""
        self.vocal_emotion = ""

    def toggle_camera_lock(self, instance):
        if self.camera_activate:
            self.camera_activate = False
            self.change_camera_image()

        else:
            self.camera_activate = True
            self.change_camera_image()

    def play_sound(self):
        sound = SoundLoader.load('voice/talk.wav')
        if sound:
            sound_length = sound.length
            sound.play()
            time.sleep(sound_length)

    def comunity(self, text="", current_emotion="", vocal_emotion=""):
        self.new_com += "사용자 : "
        created_prompt = mem.create_prompt(text, current_emotion, vocal_emotion)
        new_text = self.text + self.new_com + created_prompt

        anser = mem.question(new_text) + "\n"
        cleaned_string = anser.replace("AI : ", "")
        voice.tts(cleaned_string)

        self.new_com += text + "\n" + anser

        import threading
        self.voice_thread = threading.Thread(target=self.play_sound)
        self.voice_thread.start()

        Clock.schedule_once(lambda dt: self._update_ui(text, anser))

    def _update_ui(self, text, anser):
        self.question_label = Label(text="사용자 : " + text, font_name='Gulim', size_hint_y=None, height=50, color=(0, 0, 0, 1))
        self.anser_label = Label(text=anser, font_name='Gulim', size_hint_y=None, height=50, color=(0, 0, 0, 1))

        self.label_layout.add_widget(self.question_label)
        self.label_layout.add_widget(self.anser_label)
        self.scroll(self.anser_label)

        Clock.schedule_once(self.scroll, 0)

if __name__ == '__main__':

    LabelBase.register(name='Gulim', fn_regular='font/gulim.ttc')

    MyApp().run()