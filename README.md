We built a prompt generator.

## 실행 가이드

이 프로젝트는 Windows 11 노트북에서 Python 3.11을 사용하여 진행되었습니다.

## 0. API Key 수집
프로젝트를 시작하기 전에, 아래의 두 가지 API Key를 발급받아야 합니다.

1. **Clova Speech API Key**: [이곳](https://www.ncloud.com/product/aiService/clovaSpeech)에서 발급받으세요.
   - `장문 인식 도메인`에서 **화자 인식**은 `사용`으로 설정하세요.
   - **이벤트 탐지**는 `미사용`으로 설정하세요.

2. **GPT API Key**: [이곳](https://platform.openai.com/login?launch)에서 로그인한 후 API Key를 발급받으세요.

## 1. 기본 라이브러리 설치

먼저, 프로젝트를 클론하고 필요한 라이브러리를 설치합니다. 터미널에서 다음 명령어를 입력하세요:

```bash
git clone https://github.com/maytheir/SEE_you.git
cd SEE_you
pip install -r requirements.txt
```

## 2. 빠른 시작

프로젝트 폴더 내의 `params.json` 파일을 열고, Clova Speech로부터 받은 `invoke_url_value`와 `secret_key_value`를 각각 `user_invoke_url_value`와 `user_secret_key_value`에 입력하세요. GPT의 API 키는 `user_openai_key_value`에 입력합니다.

명령 프롬프트에서 아래 명령어를 실행하여 프로젝트를 시작합니다:

```bash
python main.py
```

## 3. Python에서 사용하기
tools 폴더에 있는 .py파일을 불러와서 쉽게 사용할 수 있습니다.

### GPT API만 사용할 경우

다음 코드를 사용하여 GPT API를 통해 답변을 생성할 수 있습니다:

```python
from memory import cls_memory

mem = cls_memory()

# GPT API를 통한 답변 생성
answer = mem.question("hello world?")
print(answer)
```

### 음성 데이터만 이용할 경우

Clova Speech API를 사용하여 음성 데이터를 처리하려면 다음 코드를 사용하세요:

```python
from clova_stt import ClovaSpeechClient
import os

res = ClovaSpeechClient()

# 녹음 시작
res.start_recording()

# 녹음 종료
speech = res.stop_recording()

# 텍스트 인식 결과 출력
print(speech)
```

### 카메라 처리만 이용할 경우

카메라를 통해 감정을 처리하려면 다음 코드를 사용하세요:

```python
from facial_emotion_detect import FER

detector = FER()

# 카메라 시작
detector.start_camera()

# 카메라 종료
current_emotion = detector.stop_camera()

# 감정 인식 결과 출력
print(current_emotion)
```

### 음성 감정 추출만 이용할 경우
```python
import voice_emotion

# voice/output.wav 파일의 감정 추출
voice = vocal_emotion()
voice_emotion = voice.vocal_prossing()

print(voice_emotion)
```

## 라이센스
이 프로젝트는 AGPL3.0 라이센스 하에 제공됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## Data set License
'''bash
## Acknowledgements

This project utilizes multiple datasets, all of which are licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

### 1. FER Final Project Dataset
- **Dataset Title**: [FER Final Project Dataset](https://universe.roboflow.com/fer-group-6/fer-final-project)
- **Author**: FER Group 6
- **Published On**: Roboflow Universe
- **Publisher**: Roboflow
- **Publication Date**: May 2024
- **Access Date**: August 28, 2024

### 2. facedetection2 Dataset
- **Dataset Title**: [facedetection2 Dataset](https://universe.roboflow.com/emotiondetection/facedetection2-6qc02)
- **Author**: emotiondetection
- **Published On**: Roboflow Universe
- **Publisher**: Roboflow
- **Publication Date**: March 2023
- **Access Date**: August 28, 2024

### 3. expression Dataset
- **Dataset Title**: [expression Dataset](https://universe.roboflow.com/yolok-6hiio/expression-rjtzg)
- **Author**: YOLOK
- **Published On**: Roboflow Universe
- **Publisher**: Roboflow
- **Publication Date**: May 2024
- **Access Date**: August 28, 2024
```
