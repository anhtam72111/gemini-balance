
import asyncio
import math
from typing import Any, AsyncGenerator, Callable, List

from app.config.config import settings
from app.core.constants import (
    DEFAULT_STREAM_CHUNK_SIZE,
    DEFAULT_STREAM_LONG_TEXT_THRESHOLD,
    DEFAULT_STREAM_MAX_DELAY,
    DEFAULT_STREAM_MIN_DELAY,
    DEFAULT_STREAM_SHORT_TEXT_THRESHOLD,
)
from app.log.logger import get_gemini_logger, get_openai_logger

logger_openai = get_openai_logger()
logger_gemini = get_gemini_logger()


class StreamOptimizer:
    """Stream output optimizer

    Provides stream output optimization features, including smart delay adjustment and long text chunking.
    """

    def __init__(
        self,
        logger=None,
        min_delay: float = DEFAULT_STREAM_MIN_DELAY,
        max_delay: float = DEFAULT_STREAM_MAX_DELAY,
        short_text_threshold: int = DEFAULT_STREAM_SHORT_TEXT_THRESHOLD,
        long_text_threshold: int = DEFAULT_STREAM_LONG_TEXT_THRESHOLD,
        chunk_size: int = DEFAULT_STREAM_CHUNK_SIZE,
    ):
        """Initialize stream output optimizer

        Parameters:
            logger: logger instance
            min_delay: minimum delay time (seconds)
            max_delay: maximum delay time (seconds)
            short_text_threshold: short text threshold (character count)
            long_text_threshold: long text threshold (character count)
            chunk_size: long text chunk size (character count)
        """
        self.logger = logger
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.short_text_threshold = short_text_threshold
        self.long_text_threshold = long_text_threshold
        self.chunk_size = chunk_size

    def calculate_delay(self, text_length: int) -> float:
        """Calculate delay time based on text length

        Parameters:
            text_length: text length

        Returns:
            delay time (seconds)
        """
        if text_length <= self.short_text_threshold:
            # Short text uses larger delay
            return self.max_delay
        elif text_length >= self.long_text_threshold:
            # Long text uses smaller delay
            return self.min_delay
        else:
            # Medium length text uses linear interpolation to calculate delay
            # Use logarithmic function to make delay changes smoother
            ratio = math.log(text_length / self.short_text_threshold) / math.log(
                self.long_text_threshold / self.short_text_threshold
            )
            return self.max_delay - ratio * (self.max_delay - self.min_delay)

    def split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into small chunks

        Parameters:
            text: text to be split

        Returns:
            list of text chunks
        """
        return [
            text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)
        ]

    async def optimize_stream_output(
        self,
        text: str,
        create_response_chunk: Callable[[str], Any],
        format_chunk: Callable[[Any], str],
    ) -> AsyncGenerator[str, None]:
        """Optimize stream output

        Parameters:
            text: text to output
            create_response_chunk: function to create response chunk, receives text, returns response chunk
            format_chunk: function to format response chunk, receives response chunk, returns formatted string

        Returns:
            async generator, yielding formatted response chunks
        """
        if not text:
            return

        # Calculate smart delay time
        delay = self.calculate_delay(len(text))

        # Determine output method based on text length
        if len(text) >= self.long_text_threshold:
            # Long text: chunked output
            chunks = self.split_text_into_chunks(text)
            for chunk_text in chunks:
                chunk_response = create_response_chunk(chunk_text)
                yield format_chunk(chunk_response)
                await asyncio.sleep(delay)
        else:
            # Short text: character-by-character output
            for char in text:
                char_chunk = create_response_chunk(char)
                yield format_chunk(char_chunk)
                await asyncio.sleep(delay)


# Create default optimizer instances, can be imported and used directly
openai_optimizer = StreamOptimizer(
    logger=logger_openai,
    min_delay=settings.STREAM_MIN_DELAY,
    max_delay=settings.STREAM_MAX_DELAY,
    short_text_threshold=settings.STREAM_SHORT_TEXT_THRESHOLD,
    long_text_threshold=settings.STREAM_LONG_TEXT_THRESHOLD,
    chunk_size=settings.STREAM_CHUNK_SIZE,
)

gemini_optimizer = StreamOptimizer(
    logger=logger_gemini,
    min_delay=settings.STREAM_MIN_DELAY,
    max_delay=settings.STREAM_MAX_DELAY,
    short_text_threshold=settings.STREAM_SHORT_TEXT_THRESHOLD,
    long_text_threshold=settings.STREAM_LONG_TEXT_THRESHOLD,
    chunk_size=settings.STREAM_CHUNK_SIZE,
)
