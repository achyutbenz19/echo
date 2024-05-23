import os
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from dotenv import load_dotenv
from deepgram import PrerecordedOptions, AsyncPreRecordedClient, DeepgramClientOptions, \
    BufferSource
from deepgram.clients.prerecorded.errors import DeepgramTypeError

load_dotenv()

NO_SPEECH_FROM_TEXT = "<<Issue getting speech from the text>>"
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

class SpeechToTextManager:
    def __init__(self, guild, audio_cost_calculator):
        self.guild = guild
        self.audio_cost_calculator = audio_cost_calculator
        self.deepgram_client = AsyncPreRecordedClient(DeepgramClientOptions(api_key=DEEPGRAM_API_KEY))
        self.executor = ThreadPoolExecutor()
        

    async def print_speech(self, user_audio_segment, user_id):
        """
        Adds the passed audio to the transcript as text if it has detectable speech in it
        :param user_audio_segment: The audio to try to detect speech in
        :param user_id: The user the audio is associated with
        """
        speech_as_text = await self.audio_has_speech(user_audio_segment, user_id)
        await self.save_transcription(speech_as_text, user_id)
        print(speech_as_text)

    async def audio_has_speech(self, user_audio_segment, user_id):
        """
        Determines if the passed audio segment has speech. Sends it to the VAD first, if the VAD detects speech, then it
        send it to the API. Also calculates the cost of the API call.
        :param user_audio_segment: The audio to try to detect speech in
        :param user_id: The user the audio is associated with
        :return: The speech converted to text if both the VAD and the S2T API found speech. None if one of those failed
        to find speech
        """
        self.audio_cost_calculator.calculate_cost(user_audio_segment.duration_seconds, user_id)
        speech_as_text = await self.get_speech_as_text(user_audio_segment, self.guild.id)
        if speech_as_text and speech_as_text != NO_SPEECH_FROM_TEXT:
            return speech_as_text
        self.audio_cost_calculator.increment_failed_requests()
        print("Tried to convert speech to text but no speech was detected")
        return None

    async def get_speech_as_text(self, user_audio_segment, server_id):
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True
        )

        buffer = BytesIO()
        user_audio_segment.export(buffer, format="wav")
        buffer.seek(0)

        try:
            url_response = await self.deepgram_client.transcribe_file(BufferSource(buffer=buffer.getvalue()), options)
        except DeepgramTypeError as e:
            print(f"Error from the Deepgram API while getting the S2T: {e}")
            return NO_SPEECH_FROM_TEXT
        except Exception as e:
            error_type = e.__class__.__name__
            print(f"An error occurred while trying to get the S2T: {error_type}: {e}")
            return NO_SPEECH_FROM_TEXT

        if not url_response or not url_response.results or not url_response.results.channels:
            print("Something went wrong getting the S2T")
            return NO_SPEECH_FROM_TEXT
        return url_response.results.channels[0].alternatives[0].transcript
    
    async def save_transcription(self, transcription, user_id):
        """
        Saves the transcription to a file, appending it along with the user ID.
        :param transcription: The transcription text
        :param user_id: The ID of the user associated with the transcription
        """
        
        with open("current_transcription.txt", "a") as f:
            f.write(f"@{self.guild.get_member(int(user_id)).name}: {transcription}\n")
