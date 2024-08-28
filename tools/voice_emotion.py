import numpy as np
import tensorflow as tf
import librosa
from tensorflow.keras.layers import MultiHeadAttention, Dense, LayerNormalization, Dropout
from gtts import gTTS
import os
import json

# Define the custom TransformerBlock layer
class TransformerBlock(tf.keras.layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1, **kwargs):
        super(TransformerBlock, self).__init__(**kwargs)
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.rate = rate

        self.att = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential([
            Dense(ff_dim, activation="relu"),
            Dense(embed_dim),
        ])
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(rate)
        self.dropout2 = Dropout(rate)
        self.adjust_lstm_output = Dense(embed_dim)

    def call(self, inputs, training=False):
        reshaped_inputs = tf.reshape(inputs, (tf.shape(inputs)[0], tf.shape(inputs)[1], -1, 256))
        reshaped_inputs = tf.reduce_mean(reshaped_inputs, axis=2)
        attn_output = self.att(reshaped_inputs, reshaped_inputs)
        attn_output = self.dropout1(attn_output, training=training)
        adjusted_inputs = self.adjust_lstm_output(reshaped_inputs)
        out1 = self.layernorm1(adjusted_inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)

    def get_config(self):
        config = super(TransformerBlock, self).get_config()
        config.update({
            'embed_dim': self.embed_dim,
            'num_heads': self.num_heads,
            'ff_dim': self.ff_dim,
            'rate': self.rate,
        })
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)

class vocal_emotion:
    def __init__(self):
        json_path = os.path.dirname( os.path.abspath( __file__ ) )
        json_path = os.path.dirname(json_path)
        with open(os.path.join(json_path, ("params.json")), 'r') as fp :
            params = json.load(fp)

        params = params["voice"]
        self.model_path = params["voice_model_path"]

        # .wav 파일 경로
        wav_file_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__))) + "/voice/output.wav"

        # .wav 파일 불러오기
        self.audio_data, self.RATE = librosa.load(wav_file_path, sr=16000)

        # Load the H5 model with custom object scope
        with tf.keras.utils.custom_object_scope({'TransformerBlock': TransformerBlock}):
            self.model = tf.keras.models.load_model(self.model_path)


    def processing(self):
        # Normalize audio data
        audio_data = self.audio_data / np.max(np.abs(self.audio_data))

        # Use librosa to extract Mel Spectrogram
        mel_spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=self.RATE, n_mels=128)
        mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)

        # Adjust Mel Spectrogram to match expected input shape
        expected_timesteps = 32  # Example: the expected number of time steps by the model
        current_timesteps = mel_spectrogram_db.shape[1]

        if current_timesteps < expected_timesteps:
            # Pad with zeros if current timesteps are less than expected
            pad_width = expected_timesteps - current_timesteps
            mel_spectrogram_db = np.pad(mel_spectrogram_db, ((0, 0), (0, pad_width)), mode='constant')
        elif current_timesteps > expected_timesteps:
            # Trim if current timesteps are more than expected
            mel_spectrogram_db = mel_spectrogram_db[:, :expected_timesteps]
        # Expand dimensions to match model input requirements
        input_data = np.expand_dims(mel_spectrogram_db, axis=0)
        self.input_data = np.expand_dims(input_data, axis=-1)  # Add channel dimension if needed

    def predict(self):
        # Perform inference
        outputs = self.model.predict(self.input_data)

        # Define the emotion labels used during training
        emotion_labels = ['angry', 'fear', 'happy', 'neutral', 'surprise', 'sad']

        # Get the class with the highest probability
        predicted_class_index = np.argmax(outputs, axis=-1)[0]

        # Map the index to the class label
        predicted_class_label = emotion_labels[predicted_class_index]

        # Print the results
        # print(f"Predicted probabilities: {outputs[0]}")
        # print(f"Predicted class index: {predicted_class_index}")
        # print(f"Predicted class label: {predicted_class_label}")

        return predicted_class_label

    def tts(self, generated_response):
        # Generate TTS based on the predicted emotion
        # Define a message for each emotion in Korean
        message = generated_response

        # Use gTTS to convert text to speech
        tts = gTTS(text=message, lang='ko')

        # Save the audio file
        output_file = "voice/talk.wav"
        tts.save(output_file)
        print(f"TTS audio saved to {output_file}")

    def vocal_prossing(self):
        "음성 감정추출 결과 출력"
        self.processing()
        emotion = self.predict()
        
        return emotion

if __name__ == '__main__':
    voice = vocal_emotion()
    voice.vocal_prossing()