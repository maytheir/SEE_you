"""
    해당 코드는 Chat GPT API의 예제 코드를 기반으로 작성되었습니다.
"""

from openai import OpenAI
import json
import os

# 기억
class cls_memory:
    def __init__(self):
        json_path = os.path.dirname( os.path.abspath( __file__ ) )
        json_path = os.path.dirname(json_path)
        with open(os.path.join(json_path, ("params.json")), 'r') as fp :
            params = json.load(fp)

        params = params["gpt"]
        user_api_key = params["user_openai_key_value"]

        self.client = OpenAI(api_key = user_api_key)

        self.text = ""

    def read_memory(self):
        """
            메모리 읽어오는 함수.
        """
        try:
            with open('tools/mem.txt', 'r', encoding='utf-8') as file:
                # 파일 작업 수행
                self.text = file.read()
        except (FileNotFoundError, IOError):
            pass 

        return self.text
     
    def simple_save_memory(self, text):
        "단순 저장"
        with open('tools/mem.txt', 'a', encoding='utf-8') as file:
            file.write(text)
    
    def question(self, text):
        """
            질문 대답용 함수.
            CHAT GPT API 활용
        """
        completion = self.client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """
                사람의 친한 친구.
                대답은 무조건 \"AI : \"의 뒤에 이루어져야 함. 또한 문장은 무조건 1줄만 출력해야 함.
                친구의 기분을 파악하여서 기쁠때는 같이 기쁜 일을 축하해줘. 슬플 때는 공감해주면서 가벼운 위로를 해줘. 화날 때는 어떤 일이 있었는지 얘기를 듣고, 같이 공감해줘. 두려울 때는 어떤 것이 두려운지 묻고, 용기를 심어줘. 놀랄 때는 어떤 일에 놀랐는지 호기심 가득한 물음과 답변을 해줘.
                """},
            {"role": "user", "content": text}
        ]
        )

        if "AI : " in completion.choices[0].message.content:
            out = completion.choices[0].message.content
        else:
            out = "AI : " + completion.choices[0].message.content

        return out
    
    def create_prompt(self, text, facial_emotion, vocal_emotion):
        anser = (f"얼굴: {facial_emotion} 목소리: {vocal_emotion} 텍스트: {text}") + "\n"
  
        return anser
        