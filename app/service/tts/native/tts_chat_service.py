"""
Native Gemini TTS chat service extension
Inherits from original chat service, adds native Gemini TTS support (single and multi-speaker), maintains backward compatibility
"""

import datetime
import time
from typing import Any, Dict

from app.config.config import settings
from app.database.services import add_error_log, add_request_log
from app.domain.gemini_models import GeminiRequest
from app.log.logger import get_gemini_logger
from app.service.chat.gemini_chat_service import GeminiChatService
from app.service.tts.native.tts_response_handler import TTSResponseHandler

logger = get_gemini_logger()


class TTSGeminiChatService(GeminiChatService):
    """
    TTS-supporting Gemini chat service
    Inherits from original GeminiChatService, adds TTS functionality
    """

    def __init__(self, base_url: str, key_manager):
        """
        Initialize TTS chat service
        """
        super().__init__(base_url, key_manager)
        # Replace original handler with TTS response handler
        self.response_handler = TTSResponseHandler()
        logger.info(
            "TTS Gemini Chat Service initialized with multi-speaker TTS support"
        )

    async def generate_content(
        self, model: str, request: GeminiRequest, api_key: str
    ) -> Dict[str, Any]:
        """
        Generate content, supporting TTS
        """
        try:
            # Add debug log
            logger.info(f"TTS request model: {model}")
            logger.info(f"TTS request generationConfig: {request.generationConfig}")

            # Check if it is a TTS model; if so, special handling is needed
            if "tts" in model.lower():
                logger.info("Detected TTS model, applying TTS-specific processing")
                # For TTS models, we need to ensure that the correct fields are passed
                response = await self._handle_tts_request(model, request, api_key)
                return response
            else:
                # For non-TTS models, use the parent class's method
                response = await super().generate_content(model, request, api_key)
                return response
        except Exception as e:
            logger.error(f"TTS API call failed with error: {e}")
            raise

    async def _handle_tts_request(
        self, model: str, request: GeminiRequest, api_key: str
    ) -> Dict[str, Any]:
        """
        Handle TTS-specific request, including full logging functionality
        """
        # Record start time and request time
        start_time = time.perf_counter()
        request_datetime = datetime.datetime.now()
        is_success = False
        status_code = None

        try:
            # Build TTS-specific payload - excludes tools and safetySettings
            from app.service.chat.gemini_chat_service import _filter_empty_parts

            request_dict = request.model_dump(exclude_none=False)

            # Build simplified TTS-specific payload
            payload = {
                "contents": _filter_empty_parts(request_dict.get("contents", [])),
                "generationConfig": request_dict.get("generationConfig", {}),
            }

            # Only add systemInstruction if present
            if request_dict.get("systemInstruction"):
                payload["systemInstruction"] = request_dict.get("systemInstruction")

            # Ensure generationConfig is not None
            if payload["generationConfig"] is None:
                payload["generationConfig"] = {}

            # Obtain TTS-related fields directly from request.generationConfig
            if request.generationConfig:
                # Add TTS-specific fields
                if request.generationConfig.responseModalities:
                    payload["generationConfig"][
                        "responseModalities"
                    ] = request.generationConfig.responseModalities
                    logger.info(
                        f"Added responseModalities: {request.generationConfig.responseModalities}"
                    )

                if request.generationConfig.speechConfig:
                    payload["generationConfig"][
                        "speechConfig"
                    ] = request.generationConfig.speechConfig
                    logger.info(
                        f"Added speechConfig: {request.generationConfig.speechConfig}"
                    )
            else:
                logger.warning(
                    "No generationConfig found in request, TTS fields may be missing"
                )

            logger.info(f"TTS payload before API call: {payload}")

            # Call API
            response = await self.api_client.generate_content(payload, model, api_key)

            # If execution reaches here, the API call was successful
            is_success = True
            status_code = 200

            # Use TTS response handler to process the response
            return self.response_handler.handle_response(response, model, False, None)

        except Exception as e:
            # Log error
            is_success = False
            error_msg = str(e)

            # Attempt to extract status code from error message
            import re

            match = re.search(r"status code (\d+)", error_msg)
            if match:
                status_code = int(match.group(1))
            else:
                status_code = 500

            # Add error log
            await add_error_log(
                gemini_key=api_key,
                model_name=model,
                error_type="tts-api-error",
                error_log=error_msg,
                error_code=status_code,
                request_msg=(
                    request.model_dump(exclude_none=False)
                    if settings.ERROR_LOG_RECORD_REQUEST_BODY
                    else None
                ),
            )

            logger.error(f"TTS API call failed: {error_msg}")
            raise

        finally:
            # Record request log
            end_time = time.perf_counter()
            latency_ms = int((end_time - start_time) * 1000)

            await add_request_log(
                model_name=model,
                api_key=api_key,
                is_success=is_success,
                status_code=status_code,
                latency_ms=latency_ms,
                request_time=request_datetime,
            )
