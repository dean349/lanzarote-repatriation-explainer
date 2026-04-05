"""
Clipboard TTS Monitor for Antigravity AI Responses
----------------------------------------------------
Uses Microsoft Edge Neural TTS (en-GB-RyanNeural) for natural-sounding
human male speech. Requires internet connection.

Usage:
    python tts_clipboard_monitor.py

Stop: Press Ctrl+C
"""

import asyncio
import os
import re
import tempfile
import time
import threading

import edge_tts
import pygame
import win32clipboard

# ── Voice Configuration ────────────────────────────────────────────────────────
VOICE = "en-GB-RyanNeural"   # Natural British male. Alternatives:
                              #   "en-US-GuyNeural"     - American male
                              #   "en-GB-ThomasNeural"  - British male (alt)
                              #   "en-US-ChristopherNeural" - American male (deep)
RATE  = "+0%"                 # Speech rate: "-10%" slower, "+10%" faster
PITCH = "+0Hz"                # Pitch adjust: "-5Hz" deeper, "+5Hz" higher
# ──────────────────────────────────────────────────────────────────────────────


def clean_text(text: str) -> str:
    """Strip markdown formatting for natural-sounding speech."""
    # Remove code blocks entirely — don't attempt to read them
    text = re.sub(r'```[\s\S]*?```', 'code block omitted.', text)
    text = re.sub(r'`[^`\n]+`', '', text)
    # Remove headings markers but keep text
    text = re.sub(r'#{1,6}\s+', '', text)
    # Remove bold/italic markers but keep text
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\*(.+?)\*', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'__(.+?)__', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'_(.+?)_', r'\1', text, flags=re.DOTALL)
    # Remove markdown links — keep the display text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove table rows and separators
    text = re.sub(r'\|[^\n]+\|', '', text)
    text = re.sub(r'^[\s\-\|:]+$', '', text, flags=re.MULTILINE)
    # Remove bullet/numbered list markers
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-_*]{3,}$', '', text, flags=re.MULTILINE)
    # Remove blockquote markers
    text = re.sub(r'^\s*>\s+', '', text, flags=re.MULTILINE)
    # Collapse paragraph breaks into sentence pauses
    text = re.sub(r'\n{2,}', '. ', text)
    text = re.sub(r'\n', ' ', text)
    # Clean up double punctuation
    text = re.sub(r'\.\.+', '.', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


async def speak_async(text: str):
    """Generate speech via Edge TTS and play it."""
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name

    try:
        await communicate.save(tmp_path)

        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()

        # Wait for playback — exit cleanly if cancelled (Ctrl+C)
        try:
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pygame.mixer.music.stop()
            raise  # re-raise so the monitor loop also exits

        pygame.mixer.music.unload()
        pygame.mixer.quit()
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def get_clipboard_text() -> str:
    """Safely read Unicode text from the Windows clipboard."""
    try:
        win32clipboard.OpenClipboard()
        try:
            return win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except TypeError:
            return ""
    except Exception:
        return ""
    finally:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass


async def monitor():
    print(f"\n{'=' * 55}")
    print(f"  Antigravity TTS Monitor — {VOICE}")
    print(f"{'=' * 55}")
    print("  Copy any AI response to hear it in a natural voice.")
    print("  Requires internet connection (uses Edge Neural TTS).")
    print("  Press Ctrl+C to stop.\n")

    last_text = get_clipboard_text()  # Snapshot current clipboard so we don't re-read on start

    while True:
        try:
            current = get_clipboard_text()

            if current and current != last_text and len(current) > 10:
                last_text = current
                cleaned = clean_text(current)
                if cleaned:
                    preview = cleaned[:90] + ("..." if len(cleaned) > 90 else "")
                    print(f"▶  Speaking: {preview}")
                    await speak_async(cleaned)
                    print()

            await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            # Ctrl+C causes asyncio to cancel the task — exit cleanly
            raise
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        print("\nStopped.")
