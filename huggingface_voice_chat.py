#!/usr/bin/env python3
"""
HuggingFace Desktop GUI with Voice Input Support
Tamil-English Mixed Natural Language Support

Fixes:
- Guard optional voice dependencies to prevent crashes
- Replace placeholder with a runnable Tkinter app
- Provide minimal VoiceManager with safe fallbacks
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import os
import sys
import time

# Optional voice dependencies
VOICE_AVAILABLE = False
try:
    import speech_recognition as sr  # type: ignore
    import pyttsx3  # type: ignore
    VOICE_AVAILABLE = True
    print("✅ Voice modules loaded successfully")
except Exception as voice_import_error:
    print(f"⚠️ Voice modules not available: {voice_import_error}")
    print("Tip: pip install SpeechRecognition pyttsx3 pyaudio")

class VoiceManager:
    """Manage speech recognition and text-to-speech with graceful fallbacks."""

    def __init__(self) -> None:
        self._available = VOICE_AVAILABLE
        self._recognizer = sr.Recognizer() if self._available else None  # type: ignore[name-defined]
        self._tts_engine = pyttsx3.init() if self._available else None  # type: ignore[name-defined]

    @property
    def available(self) -> bool:
        return self._available

    def speak(self, text: str) -> None:
        if not self._available or self._tts_engine is None:
            raise RuntimeError("Voice not available. Install pyttsx3 and dependencies.")
        self._tts_engine.say(text)
        self._tts_engine.runAndWait()

    def listen_once(self, timeout: float = 5.0, phrase_time_limit: float = 10.0) -> str:
        if not self._available or self._recognizer is None:
            raise RuntimeError("Voice not available. Install SpeechRecognition and dependencies.")
        with sr.Microphone() as source:  # type: ignore[attr-defined]
            self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self._recognizer.listen(
                source, timeout=timeout, phrase_time_limit=phrase_time_limit
            )
        try:
            return self._recognizer.recognize_google(audio)
        except Exception as recognition_error:
            return f"[voice error] {recognition_error}"


class VoiceApp:
    """A minimal Tkinter UI demonstrating voice availability and actions."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.voice = VoiceManager()
        self._last_text_spoken: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.root.title("HuggingFace Voice Chat")
        self.root.geometry("640x420")

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.transcript = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, height=16, font=("Consolas", 11)
        )
        self.transcript.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(main_frame)
        controls.pack(fill=tk.X, pady=(10, 0))

        self.input_var = tk.StringVar()
        self.entry = ttk.Entry(controls, textvariable=self.input_var)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", lambda _e: self._on_send_clicked())

        send_btn = ttk.Button(controls, text="Send", command=self._on_send_clicked)
        send_btn.pack(side=tk.LEFT, padx=(8, 0))

        speak_btn = ttk.Button(controls, text="Speak Reply", command=self._on_speak_clicked)
        if not self.voice.available:
            speak_btn.state(["disabled"])
        speak_btn.pack(side=tk.LEFT, padx=(8, 0))

        listen_btn = ttk.Button(controls, text="Listen", command=self._on_listen_clicked)
        if not self.voice.available:
            listen_btn.state(["disabled"])
        listen_btn.pack(side=tk.LEFT, padx=(8, 0))

        status_text = "🎤 Voice ready" if self.voice.available else "🎤 Voice unavailable"
        status_label = ttk.Label(controls, text=status_text)
        status_label.pack(side=tk.LEFT, padx=(12, 0))

        self._append("system", "Type text and press Send. Use voice if available.")

    def _append(self, role: str, content: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"system": "[system]", "user": "[user]", "assistant": "[assistant]"}.get(role, "[other]")
        self.transcript.insert(tk.END, f"{timestamp} {prefix} {content}\n")
        self.transcript.see(tk.END)

    def _on_send_clicked(self) -> None:
        text = self.input_var.get().strip()
        self.input_var.set("")
        if not text:
            messagebox.showinfo("Empty", "Please type something before sending.")
            return
        self._append("user", text)
        reply = f"Echo: {text}"
        self._last_text_spoken = reply
        self._append("assistant", reply)

    def _on_speak_clicked(self) -> None:
        if not self.voice.available:
            messagebox.showwarning("Voice unavailable", "Install audio dependencies to enable speech.")
            return
        if not self._last_text_spoken:
            messagebox.showinfo("Nothing to speak", "No assistant reply to speak yet.")
            return
        try:
            self.voice.speak(self._last_text_spoken)
        except Exception as err:
            messagebox.showerror("Speak failed", str(err))

    def _on_listen_clicked(self) -> None:
        if not self.voice.available:
            messagebox.showwarning("Voice unavailable", "Install audio dependencies to enable listening.")
            return
        try:
            heard = self.voice.listen_once()
            self._append("user", f"[heard] {heard}")
        except Exception as err:
            messagebox.showerror("Listen failed", str(err))
if __name__ == "__main__":
    def main() -> None:
        root = tk.Tk()
        _ = VoiceApp(root)
        root.mainloop()

    main()
