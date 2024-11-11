import os
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
import requests
from fastapi import FastAPI, Request
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Create audio directory if it doesn't exist
AUDIO_DIR = Path("audio_files")
AUDIO_DIR.mkdir(exist_ok=True)

# Mount static directory for audio files
app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")

# Initialize clients
twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class CallState:
    def __init__(self):
        self.conversation_history = []
        self.current_state = "greeting"

# Store call states
call_states = {}

async def get_ai_response(user_input, conversation_history):
    """Get response from OpenAI"""
    messages = conversation_history + [{"role": "user", "content": user_input}]
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

async def generate_voice(text, call_sid):
    """Generate voice using ElevenLabs"""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{os.getenv('ELEVENLABS_VOICE_ID')}/stream"
    
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": os.getenv('ELEVENLABS_API_KEY'),
        "Content-Type": "application/json"
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        # Generate unique filename for this response
        filename = f"{call_sid}_{int(time.time())}.mp3"
        filepath = AUDIO_DIR / filename
        
        # Save audio file
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        # Return the URL path for the audio file
        return f"/audio/{filename}"
    except Exception as e:
        logger.error(f"Error generating voice with ElevenLabs: {str(e)}")
        return None

@app.post("/call/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming calls"""
    try:
        logger.info("Received incoming call")
        form_data = await request.form()
        logger.debug(f"Form data: {dict(form_data)}")
        
        call_sid = form_data['CallSid']
        logger.info(f"Call SID: {call_sid}")
        
        call_states[call_sid] = CallState()
        
        response = VoiceResponse()
        
        # Generate greeting with ElevenLabs
        greeting = "Hello Thank you for calling Mightzen dot ca! How can I help you today?"
        audio_url = await generate_voice(greeting, call_sid)
        
        if audio_url:
            logger.info(f"Using ElevenLabs TTS for greeting - Audio URL: {audio_url}")
            # Get the full URL including ngrok domain
            full_audio_url = str(request.base_url)[:-1] + audio_url
            response.play(full_audio_url)
        else:
            logger.warning("Falling back to Twilio TTS for greeting")
            response.say(greeting)
        
        gather = Gather(
            input='speech',
            action='/call/process_speech',
            method='POST',
            language='en-US',
            enhanced='true'
        )
        response.append(gather)
        
        # Add a backup in case speech isn't detected
        response.redirect('/call/incoming')
        
        logger.info("Returning response to Twilio")
        return Response(
            content=str(response),
            media_type="application/xml"
        )
    except Exception as e:
        logger.error(f"Error in incoming_call: {str(e)}")
        response = VoiceResponse()
        response.say("We're sorry, but there was an error processing your call. Please try again later.")
        return Response(
            content=str(response),
            media_type="application/xml"
        )
#  reusable function for voice responses
async def create_voice_response(text: str, call_sid: str, request: Request) -> VoiceResponse:
    """Create a TwiML response with ElevenLabs voice"""
    response = VoiceResponse()
    
    audio_url = await generate_voice(text, call_sid)
    if audio_url:
        logger.info(f"Using ElevenLabs TTS - Audio URL: {audio_url}")
        full_audio_url = str(request.base_url)[:-1] + audio_url
        response.play(full_audio_url)
    else:
        logger.warning("Falling back to Twilio TTS")
        response.say(text)
    
    return response
@app.post("/call/process_speech")
async def process_speech(request: Request):
    try:
        form_data = await request.form()
        call_sid = form_data['CallSid']
        speech_result = form_data.get('SpeechResult')
        
        if not speech_result:
            logger.warning("No speech detected")
            response = await create_voice_response(
                "I didn't catch that. Could you please repeat?",
                call_sid,
                request
            )
            gather = Gather(
                input='speech',
                action='/call/process_speech',
                method='POST',
                language='en-US',
                enhanced='true'
            )
            response.append(gather)
            return Response(
                content=str(response),
                media_type="application/xml"
            )
            
        logger.info(f"Processing speech for call {call_sid}: {speech_result}")
        
        # Get call state
        state = call_states.get(call_sid)
        if not state:
            logger.warning(f"No state found for call {call_sid}, creating new state")
            state = CallState()
            call_states[call_sid] = state
        
        # Get AI response
        ai_response = await get_ai_response(speech_result, state.conversation_history)
        logger.info(f"AI Response: {ai_response}")
        
        # Create response
        response = VoiceResponse()
        
        # Try to use ElevenLabs
        audio_url = await generate_voice(ai_response, call_sid)
        if audio_url:
            logger.info(f"Using ElevenLabs TTS - Audio URL: {audio_url}")
            # Get the full URL including ngrok domain
            full_audio_url = str(request.base_url)[:-1] + audio_url
            response.play(full_audio_url)
        else:
            logger.info("Using Twilio TTS fallback")
            response.say(ai_response)
        
        # Update conversation history
        state.conversation_history.extend([
            {"role": "user", "content": speech_result},
            {"role": "assistant", "content": ai_response}
        ])
        
        # Gather next user input
        gather = Gather(
            input='speech',
            action='/call/process_speech',
            method='POST',
            language='en-US',
            enhanced='true'
        )
        response.append(gather)
        
        return Response(
            content=str(response),
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error in process_speech: {str(e)}", exc_info=True)
        response = await create_voice_response(
            "I apologize, but I'm having trouble processing your request. Please try again.",
            call_sid,
            request
        )
        gather = Gather(
            input='speech',
            action='/call/process_speech',
            method='POST',
            language='en-US',
            enhanced='true'
        )
        response.append(gather)
        return Response(
            content=str(response),
            media_type="application/xml"
        )

# Cleanup function to remove old audio files
async def cleanup_audio_files():
    """Remove audio files older than 1 hour"""
    while True:
        try:
            current_time = time.time()
            for audio_file in AUDIO_DIR.glob("*.mp3"):
                if current_time - audio_file.stat().st_mtime > 3600:  # 1 hour
                    audio_file.unlink()
        except Exception as e:
            logger.error(f"Error cleaning up audio files: {str(e)}")
        await asyncio.sleep(300)  # Check every 5 minutes

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(cleanup_audio_files())

if __name__ == "__main__":
    import uvicorn
    import time
    import asyncio
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)