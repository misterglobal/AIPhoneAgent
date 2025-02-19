Voice Assistant API with Twilio, OpenAI, and ElevenLabs
This project is a FastAPI application that integrates with Twilio for handling incoming voice calls, uses OpenAI's GPT-3.5-turbo for conversational AI, and leverages ElevenLabs for high-quality text-to-speech (TTS) voice synthesis. It creates dynamic, voice-driven interactions for callers, generating audio responses on the fly while maintaining conversation history.

Features
Incoming Call Handling:
Processes incoming calls via Twilio, generating a greeting and prompting the caller for speech input.

Conversational AI:
Integrates with OpenAI's GPT-3.5-turbo to generate context-aware responses based on the conversation history.

Dynamic Voice Synthesis:
Uses ElevenLabs API to convert text responses to speech. If ElevenLabs fails, it falls back to Twilio's TTS.

Audio File Management:
Saves generated audio files in a local directory and serves them as static files. A background task cleans up files older than 1 hour.

Logging:
Provides detailed debug and error logging to help with monitoring and troubleshooting.

Prerequisites
Python 3.8 or higher
A Twilio account with valid TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
An OpenAI API key for GPT-3.5-turbo access (OPENAI_API_KEY)
An ElevenLabs API key (ELEVENLABS_API_KEY) and a valid ELEVENLABS_VOICE_ID
uvicorn for running the FastAPI application
Setup
Clone the Repository:

bash
Copy
git clone <repository-url>
cd <repository-directory>
Create and Activate a Virtual Environment:

bash
Copy
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies:

bash
Copy
pip install -r requirements.txt
If you don't have a requirements.txt file, you can manually install the following packages:

fastapi
uvicorn
python-dotenv
twilio
openai
requests
Configure Environment Variables:

Create a .env file in the project root and add your credentials:

env
Copy
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_elevenlabs_voice_id
Create Audio Directory:

The application will automatically create an audio_files directory if it does not exist. This directory is used to store generated TTS audio files.

Running the Application
Start the FastAPI server using uvicorn:

bash
Copy
uvicorn main:app --host 0.0.0.0 --port 8000
Replace main:app with the appropriate module and app name if your file structure differs.

Endpoints
1. Handle Incoming Calls
Endpoint: /call/incoming
Method: POST
Description:
Processes the incoming call from Twilio.
Generates a greeting using ElevenLabs TTS (with a fallback to Twilio TTS).
Prompts the caller for speech input.
2. Process Speech Input
Endpoint: /call/process_speech
Method: POST
Description:
Processes the speech input from the caller.
If no speech is detected, prompts the caller to repeat.
Sends the caller's speech to OpenAI for a contextual response.
Generates a TTS response using ElevenLabs (fallback to Twilio TTS if needed).
Updates the conversation history for ongoing context.
Background Tasks
Audio Cleanup:
A background task runs every 5 minutes to clean up audio files in the audio_files directory that are older than 1 hour. This helps manage disk space and keep the directory clutter-free.
Logging
The application uses Python's built-in logging module:

Logs are output to the console with a level of DEBUG.
Errors during processing (e.g., API failures, speech processing issues) are logged for troubleshooting.
Troubleshooting
Environment Variables:
Ensure all required environment variables are correctly set in the .env file.

API Errors:
Check the logs for detailed error messages if there are issues with Twilio, OpenAI, or ElevenLabs integrations.

Audio Playback:
If generated audio is not playing correctly, verify the URL paths and ensure that the static files are being served correctly by FastAPI.

License
This project is open source and available under the MIT License.

Contributing
Contributions are welcome! Please open an issue or submit a pull request with any improvements or bug fixes.