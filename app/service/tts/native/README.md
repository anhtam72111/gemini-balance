# Native Gemini TTS Functionality

This module adds native Gemini TTS (Text-to-Speech) functionality to the Gemini Balance project, supporting single and multi-speaker voice synthesis. It uses an intelligent detection and inheritance-based design to maintain full compatibility with the original codebase.

## 🎯 Design Principles

- **Intelligent Detection**: Automatically detects all requests in native Gemini TTS format (containing `responseModalities` and `speechConfig`).
- **Inheritance instead of Modification**: All extensions inherit from original classes without modifying source code.
- **Full Compatibility**: Original TTS functionality (OpenAI-compatible TTS) remains completely unaffected.
- **Dynamic Model Selection**: Allows users to specify different TTS models in the request URL.
- **Automatic Fallback**: Automatically falls back to the standard service if native TTS processing fails.
- **Comprehensive Logging**: Includes request logs, error logs, and performance monitoring.
- **Ease of Maintenance**: No conflicts when updating original source code.

## 📁 File Structure

```text
app/service/tts/
├── tts_service.py           # Original OpenAI-compatible TTS service
└── native/                  # Native Gemini TTS extensions
    ├── __init__.py          # Module initialization
    ├── README.md            # Documentation (this file)
    ├── tts_models.py        # TTS data models (inherits from original models)
    ├── tts_response_handler.py  # TTS response handler (inherits from original handler)
    ├── tts_chat_service.py  # TTS chat service (inherits from original service)
    └── tts_routes.py        # TTS route extensions and dependency injection
```

## 🚀 Native Gemini TTS Features

### Intelligent Detection Mechanism (Current Implementation)

Native Gemini TTS is automatically enabled through intelligent detection, requiring no manual configuration:

1. **Auto-Enable**:
```bash
# Simply start the service, native TTS becomes automatically available
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Zero Configuration**:
- No environment variables required.
- No config file modifications needed.
- Based entirely on intelligent request content inspection.

### How It Works

The system intelligently detects request content:
- **Native TTS Request**: Contains `responseModalities: ["AUDIO"]` and `speechConfig` → Uses TTS enhanced service.
  - **Single Speaker**: Contains `voiceConfig.prebuiltVoiceConfig`.
  - **Multi-Speaker**: Contains `multiSpeakerVoiceConfig`.
- **Standard Request**: Non-TTS model → Uses original Gemini chat service.

```python
# Intelligent detection logic in app/router/gemini_routes.py
if "tts" in model_name.lower() and request.generationConfig:
    # Get TTS configuration directly from the parsed request object
    response_modalities = request.generationConfig.responseModalities or []
    speech_config = request.generationConfig.speechConfig or {}

    # If it contains AUDIO modality and speech configuration, consider it a native TTS request
    if "AUDIO" in response_modalities and speech_config:
        # Use TTS enhanced service
        tts_service = await get_tts_chat_service(key_manager)
        return await tts_service.generate_content(...)
    # Otherwise use original service
```

## 📝 Usage Examples

### 1. Native Gemini Single-Speaker TTS (using enhanced service)

Native Gemini format requests containing `voiceConfig.prebuiltVoiceConfig` will automatically use the TTS enhanced service:

```json
{
  "contents": [{
    "parts": [{"text": "Hello, this is a native Gemini TTS test."}]
  }],
  "generationConfig": {
    "responseModalities": ["AUDIO"],
    "speechConfig": {
      "voiceConfig": {
        "prebuiltVoiceConfig": {
          "voiceName": "Puck"
        }
      }
    }
  }
}
```

### 2. Native Gemini Multi-Speaker TTS (using enhanced service)

Native Gemini format requests containing `multiSpeakerVoiceConfig` will automatically use the TTS enhanced service:

```json
{
  "contents": [{
    "role": "user",
    "parts": [{"text": "Hello! How are you?"}]
  }],
  "generationConfig": {
    "responseModalities": ["AUDIO"],
    "speechConfig": {
      "multiSpeakerVoiceConfig": {
        "speakerVoiceConfigs": [
          {
            "speaker": "Assistant",
            "voiceConfig": {
              "prebuiltVoiceConfig": {
                "voiceName": "Kore"
              }
            }
          }
        ]
      }
    }
  }
}
```

### 3. OpenAI-Compatible TTS Request (using original service)

OpenAI-compatible TTS requests use different API paths and are unaffected by this module:

```bash
# Path: /v1/audio/speech
{
    "model": "tts-1",
    "input": "This is an OpenAI-compatible TTS test.",
    "voice": "alloy"
}
```

**Note**: OpenAI-compatible TTS requests:
- Use path: `/v1/audio/speech`
- Use `Authorization` header instead of `x-goog-api-key`.
- Return an audio file instead of a JSON response.
- Are not affected by the TTS enhanced service in this module.

### Standard Text Generation (using original service)

Requests for non-TTS models use the original Gemini chat service, completely unaffected:

```json
{
  "contents": [{
    "parts": [{"text": "Please provide a brief introduction to the history of AI."}]
  }]
}
```

## 🔧 Technical Implementation

### Inheritance Relationship

```text
GeminiChatService
    ↓ (Inherits)
TTSGeminiChatService
    ├── Overrides generate_content() method
    ├── Adds _handle_tts_request() method
    └── Integrates comprehensive logging features

GeminiResponseHandler
    ↓ (Inherits)
TTSResponseHandler
    └── Overrides handle_response() method

GenerationConfig (Pydantic Model)
    ↓ (Extends)
TTSGenerationConfig
```

### Workflow

1. **Request Received**: System receives an API request.
2. **Intelligent Detection**:
   - Checks if the model name contains "tts".
   - If it's a TTS model, checks `request.generationConfig` for `responseModalities: ["AUDIO"]` and `speechConfig`.
3. **Service Selection**:
   - **Native TTS Request**: Uses `TTSGeminiChatService` enhanced service.
   - **Standard Request**: Uses original `GeminiChatService`.
4. **Request Processing**:
   - **Native TTS**: Specially handled using `_handle_tts_request()`.
   - **Other Requests**: Uses standard `generate_content()` method.
5. **Field Handling**: Obtains TTS fields (`responseModalities`, `speechConfig`) directly from `request.generationConfig`.
6. **API Call**: Constructs optimized payload and calls Gemini API.
7. **Automatic Fallback**: If native TTS processing fails, automatically falls back to standard service.
8. **Response Handling**:
   - **TTS Response**: Detects audio data, returns original response directly.
   - **Standard Response**: Uses standard processing methods.
9. **Logging**: Records request time, success status, and error info to the database.

## 📊 Features

### ✅ Implemented Features

- **Smart Native TTS Support**: Supports single and multi-speaker voice synthesis.
  - **Single Speaker**: Supports `voiceConfig.prebuiltVoiceConfig` configuration.
  - **Multi-Speaker**: Supports `multiSpeakerVoiceConfig` configuration.
- **Intelligent Detection Mechanism**: Automatically detects all native Gemini TTS format requests.
- **Dynamic Model Selection**: Allows users to specify different TTS models in the URL.
- **Full Backward Compatibility**: Zero impact on all existing TTS features (OpenAI-compatible).
- **Automatic Fallback Mechanism**: Uses standard service automatically if native TTS processing fails.
- **Comprehensive Logging**: Request logs, error logs, performance monitoring.
- **API Quota Management**: Automatic retries and key rotation.
- **Zero-Config Activation**: No environment variables or config file changes required.
- **Error Handling**: Complete exception catching and error logging.

### 🎵 Supported Voice Configurations

#### Single Speaker

```json
"voiceConfig": {
  "prebuiltVoiceConfig": {
    "voiceName": "Kore|Puck|Other prebuilt voices"
  }
}
```

#### Multi-Speaker

```json
"multiSpeakerVoiceConfig": {
  "speakerVoiceConfigs": [
    {
      "speaker": "Character Name",
      "voiceConfig": {
        "prebuiltVoiceConfig": {
          "voiceName": "Kore|Puck|Other prebuilt voices"
        }
      }
    }
  ]
}
```

## ⚠️ Notes

### API Requirements
- Ensure the API key has TTS permissions.
- TTS functionality requires the `gemini-2.5-flash-preview-tts` model.
- Be aware of API quota limits (15 times per day for free tier).

### Performance Considerations
- TTS responses are typically larger than text responses (audio data).
- Monitoring API call frequency and success rate is recommended.
- Extended functionality does not affect the performance or stability of original features.

### Deployment Suggestions
- Test standard features in production before enabling.
- Enable TTS functionality gradually and monitor logs.
- Periodically check API quota usage.

## 📈 Monitoring and Debugging

### Log Inspection
- **Server Logs**: View the TTS request processing flow.
- **Admin Interface**: View request records in "API Call Details".
- **Error Logs**: View detailed info for failed requests.

### Debugging Tips
```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG

# View real-time logs
tail -f logs/app.log

# Multi-speaker TTS feature requires no config, automatically enabled.
# It can be intelligently detected via request content.
```

## 🔄 TTS System Comparison

The project now includes three TTS systems, each serving different purposes:

| TTS Type | Path | Model Selection | Voice Configuration | Use Case | Our Impact |
|---------|------|----------|----------|----------|------------|
| **OpenAI-Compatible TTS** | `/v1/audio/speech` | Fixed config file | Single speaker | OpenAI API compatibility | ✅ No impact |
| **Gemini Single-Speaker TTS** | `/v1beta/models/{model}:generateContent` | User-specified | Single speaker | Native Gemini TTS | ✅ Our enhancement |
| **Gemini Multi-Speaker TTS** | `/v1beta/models/{model}:generateContent` | User-specified | Multi-speaker | Dialogue scenarios | ✅ Our enhancement |

### Intelligent Routing Mechanism

```mermaid
flowchart TD
    A[API Request] --> B{Path Check}
    B -->|/v1/audio/speech| C[OpenAI-Compatible TTS Service]
    B -->|/v1beta/models/{model}:generateContent| D{Model contains 'tts'?}
    D -->|No| E[Standard Gemini Chat Service]
    D -->|Yes| F{Contains responseModalities and speechConfig?}
    F -->|No| G[Standard Gemini Chat Service]
    F -->|Yes| H[Native TTS Enhanced Service]
    H --> I{Success?}
    I -->|Yes| J[Return Native TTS Response]
    I -->|No| K[Fallback to Standard Service]
    C --> L[Complete]
    E --> L
```

## 🎉 Success Story

The intelligent detection-based native Gemini TTS solution has been successfully implemented:

- ✅ **Zero-Config Activation**: No environment variables or config changes needed.
- ✅ **Intelligent Detection**: Automatically detects all native Gemini TTS format requests.
- ✅ **Full Backward Compatibility**: Zero impact on all existing TTS features.
- ✅ **Dynamic Model Selection**: Allows user specification of different TTS models.
- ✅ **Automatic Fallback Mechanism**: Uses standard service automatically if processing fails.
- ✅ **Single and Multi-Speaker Synthesis**: Supports all native Gemini TTS scenarios.
- ✅ **Comprehensive Logging**: All requests viewable in the admin interface.
- ✅ **Robust Error Handling**: API quota and retry mechanisms.
- ✅ **Ease of Maintenance**: Conflict-free updates to original source code.

This implementation demonstrates how to gracefully extend the functionality of a complex system while maintaining perfect backward compatibility and without modifying original source code.
