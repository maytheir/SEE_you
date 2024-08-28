"""
    해당 코드는 Clova Speech의 예제 코드를 기반으로 작성되었습니다.
"""

import requests
import json
import pyaudio
import wave
import threading
import os
import json

class ClovaSpeechClient:
    def __init__(self):
        json_path = os.path.dirname( os.path.abspath( __file__ ) )
        json_path = os.path.dirname(json_path)
        with open(os.path.join(json_path, ("params.json")), 'r') as fp :
            params = json.load(fp)
            
        params = params["clova"]
        user_invoke_url_value = params["user_invoke_url_value"]
        user_secret_key_value = params["user_secret_key_value"]

        self.invoke_url = user_invoke_url_value
        self.secret = user_secret_key_value

        self.recording_thread = None
        self.stop_event = threading.Event()


    def req_url(self, url, completion, callback=None, userdata=None, forbiddens=None, boostings=None, wordAlignment=True, fullText=True, diarization=None, sed=None):
        request_body = {
            'url': url,
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
            'sed': sed,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        return requests.post(headers=headers,
                             url=self.invoke_url + '/recognizer/url',
                             data=json.dumps(request_body).encode('UTF-8'))

    def req_object_storage(self, data_key, completion, callback=None, userdata=None, forbiddens=None, boostings=None,
                           wordAlignment=True, fullText=True, diarization=None, sed=None):
        request_body = {
            'dataKey': data_key,
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
            'sed': sed,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        return requests.post(headers=headers,
                             url=self.invoke_url + '/recognizer/object-storage',
                             data=json.dumps(request_body).encode('UTF-8'))

    def req_upload(self, file, completion, callback=None, userdata=None, forbiddens=None, boostings=None,
                   wordAlignment=True, fullText=True, diarization=None, sed=None):
        request_body = {
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
            'sed': sed,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        print(json.dumps(request_body, ensure_ascii=False).encode('UTF-8'))
        files = {
            'media': open(file, 'rb'),
            'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
        }
        response = requests.post(headers=headers, url=self.invoke_url + '/recognizer/upload', files=files)
        return response
    
    def speech_to_text(self, audio_path):
        res = self.req_upload(file=audio_path, completion='sync')
        output = json.loads(res.text)
        return output["text"]

    def start_recording(self, FORMAT=pyaudio.paInt16, CHANNELS=1, RATE=44100, CHUNK=1024, RECORD_SECONDS=5, WAVE_OUTPUT_FILENAME="voice/output.wav"):
        self.stop_event.clear()
        self.recording_thread = threading.Thread(
            target=self.record_audio,
            args=(FORMAT, CHANNELS, RATE, CHUNK, RECORD_SECONDS, WAVE_OUTPUT_FILENAME)
        )
        self.recording_thread.start()

    def stop_recording(self):
        self.stop_event.set()
        if self.recording_thread:
            self.recording_thread.join()

        return self.anser

    def record_audio(self, FORMAT, CHANNELS, RATE, CHUNK, RECORD_SECONDS, WAVE_OUTPUT_FILENAME):
        audio = pyaudio.PyAudio()

        # 스트림 열기
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        print("녹음을 시작합니다...")

        frames = []

        # 녹음 루프
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
            if self.stop_event.is_set():
                break

        print("녹음이 완료되었습니다.")

        # 스트림 종료
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # WAV 파일로 저장
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        print(f"파일이 저장되었습니다: {WAVE_OUTPUT_FILENAME}")

        self.anser = self.speech_to_text("voice/output.wav")

        # os.environ['speech'] = anser



if __name__ == '__main__':
    res = ClovaSpeechClient()
    routput = res.record_audio()
    print(routput)
