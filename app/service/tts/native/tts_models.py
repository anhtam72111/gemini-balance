"""
Native Gemini TTS extended data models
Inherits from the original model, adding native Gemini TTS related fields, maintaining backward compatibility
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from app.domain.gemini_models import GenerationConfig as BaseGenerationConfig


class TTSGenerationConfig(BaseGenerationConfig):
    """
    Generation config class supporting TTS
    Inherits from the original GenerationConfig, adding TTS related fields
    """
    # TTS related configuration
    responseModalities: Optional[List[str]] = None
    speechConfig: Optional[Dict[str, Any]] = None


class MultiSpeakerVoiceConfig(BaseModel):
    """Multi-speaker voice configuration"""
    speakerVoiceConfigs: List[Dict[str, Any]]


class SpeechConfig(BaseModel):
    """Voice configuration"""
    multiSpeakerVoiceConfig: Optional[MultiSpeakerVoiceConfig] = None
    voiceConfig: Optional[Dict[str, Any]] = None


class TTSRequest(BaseModel):
    """TTS request model"""
    contents: List[Dict[str, Any]]
    generationConfig: TTSGenerationConfig
