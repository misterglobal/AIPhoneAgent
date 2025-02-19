# Voice Assistant API with Twilio, OpenAI, and ElevenLabs

This project is a FastAPI application that integrates with Twilio for handling incoming voice calls, uses OpenAI's GPT-3.5-turbo for conversational AI, and leverages ElevenLabs for high-quality text-to-speech (TTS) voice synthesis. It creates dynamic, voice-driven interactions for callers, generating audio responses on the fly while maintaining conversation history.

---

## Features

- **Incoming Call Handling:**  
  Processes incoming calls via Twilio, generating a greeting and prompting the caller for speech input.

- **Conversational AI:**  
  Integrates with OpenAI's GPT-3.5-turbo to generate context-aware responses based on the conversation history.

- **Dynamic Voice Synthesis:**  
  Uses ElevenLabs API to convert text responses to speech. If ElevenLabs fails, it falls back to Twilio's TTS.

- **Audio File Management:**  
  Saves generated audio files in a local directory and serves them as static files. A background task cleans up files older than 1 hour.

- **Logging:**  
  Provides detailed debug and error logging to help with monitoring and troubleshooting.

---

## Prerequisites

- Python 3.8 or higher
- A Twilio account with valid **TWILIO_ACCOUNT_SID** and **TWILIO_AUTH_TOKEN**
- An OpenAI API key for GPT-3.5-turbo access (**OPENAI_API_KEY**)
- An ElevenLabs API key (**ELEVENLABS_API_KEY**) and a valid **ELEVENLABS_VOICE_ID**
- [uvicorn](https://www.uvicorn.org/) for running the FastAPI application

---

## Setup

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>

License
This project is open source and available under the MIT License.

Contributing
Contributions are welcome! Please open an issue or submit a pull request with any improvements or bug fixes.
