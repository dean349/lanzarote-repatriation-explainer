import asyncio
import os
import re
import tempfile
import time
import threading

import edge_tts
import pygame
import win32clipboard
import keyboard

# ── Voice Configuration ────────────────────────────────────────────────────────
VOICE = "en-GB-RyanNeural"
RATE  = "+0%"
PITCH = "+0Hz"
# ──────────────────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    # Remove code blocks entirely — don't attempt to read them
    text = re.sub(r'```[\s\S]*?```', 'code block omitted.', text)
    text = re.sub(r'`[^`\n]+`', '', text)
    # Remove tool execution logs often added to responses
    text = re.sub(r'Ran command:.*?\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Viewed.*?:\d+-\d+\n', '', text, flags=re.IGNORECASE)
    
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

def get_clipboard_text() -> str:
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

class TTSManager:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.thread.start()
        self.current_task = None
        self.pygame_initialized = False

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_coro(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    async def _speak_async(self, text: str):
        communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp_path = f.name

        try:
            await communicate.save(tmp_path)

            if not self.pygame_initialized:
                pygame.mixer.init()
                self.pygame_initialized = True
            
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()

            try:
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                pygame.mixer.music.stop()
                raise
        finally:
            if self.pygame_initialized:
                try:
                    pygame.mixer.music.unload()
                except Exception:
                    pass
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def speak(self, text: str):
        self.stop()
        if text.strip() != "":
            # Clear current line explicitly instead of \r, to avoid messes in some terminals
            print(f"\n▶  Speaking: {text[:80]}...\n  Waiting for command...", end='', flush=True)
            self.current_task = self.run_coro(self._speak_async(text))

    def stop(self):
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
        if self.pygame_initialized:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

tts_manager = TTSManager()

def trigger_speak():
    # Send Ctrl+C to copy selected text
    keyboard.send('ctrl+c')
    time.sleep(0.15)  # allow clipboard to update
    
    text = get_clipboard_text()
    cleaned = clean_text(text)
    if cleaned:
        tts_manager.speak(cleaned)

def trigger_stop():
    print("\n■  Playback stopped.\n  Waiting for command...", end='', flush=True)
    tts_manager.stop()

def main():
    print(f"\n{'=' * 55}")
    print(f"  Antigravity TTS Hotkey Reader — {VOICE}")
    print(f"{'=' * 55}")
    print("  1. Highlight ANY text.")
    print("  2. Press Ctrl+Shift+S to read it aloud.")
    print("  3. Press Ctrl+Shift+Q to hush him mid-sentence.")
    print("  4. Regular Ctrl+C copies normally without reading.")
    print("  Press Ctrl+C in this terminal to quit.\n")
    print("  Waiting for command...", end='', flush=True)
    
    keyboard.add_hotkey('ctrl+shift+s', trigger_speak)
    keyboard.add_hotkey('ctrl+shift+q', trigger_stop)

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tts_manager.stop()
        print("\nStopped.")

if __name__ == "__main__":
    main()
