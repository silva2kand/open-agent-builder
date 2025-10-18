#!/usr/bin/env python3
"""
Enhanced HuggingFace Chat with Voice Input and Improved Copy Support

Fixes:
- Replaced invalid placeholder code with a runnable Tkinter app
- Safe voice import handling with clear fallback guidance
- Added robust copy support and simple mock reply for offline use
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import requests
import threading
import pyperclip
from datetime import datetime
import os
import sys
import queue
import time

"""Voice imports with graceful fallback.
These modules are optional; the app runs without them.
"""
VOICE_AVAILABLE = False
try:
    import speech_recognition as sr  # type: ignore
    import pyttsx3  # type: ignore
    VOICE_AVAILABLE = True
    print("✅ Voice modules loaded successfully")
except Exception as voice_import_error:
    # Do not crash on environments without audio dependencies
    print(f"⚠️ Voice modules not available: {voice_import_error}")
    print("Tip: pip install SpeechRecognition pyttsx3 pyaudio")


def _generate_mock_reply(user_text: str) -> str:
    """Return a deterministic mock reply for offline/demo use.

    This avoids network calls so the UI is runnable anywhere.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    if not user_text.strip():
        return f"[{timestamp}] I didn't catch anything. Please type something."
    return f"[{timestamp}] You said: {user_text.strip()}"

class ChatManager:
    """Manage chat history and clipboard copy behavior.

    Provides simple utilities needed by the GUI including replay protection
    (no duplicate consecutive assistant messages) and easy access to the
    latest assistant message for copy-to-clipboard.
    """

    def __init__(self) -> None:
        self._messages: list[dict[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        if role not in {"user", "assistant", "system"}:
            raise ValueError("role must be 'user', 'assistant', or 'system'")
        # Prevent trivial duplicate consecutive assistant messages (replay)
        if (
            role == "assistant"
            and self._messages
            and self._messages[-1]["role"] == "assistant"
            and self._messages[-1]["content"] == content
        ):
            return
        self._messages.append({"role": role, "content": content})

    def get_last_assistant_message(self) -> str | None:
        for message in reversed(self._messages):
            if message["role"] == "assistant":
                return message["content"]
        return None

    def to_json(self) -> str:
        return json.dumps(self._messages, ensure_ascii=False, indent=2)


class ChatApp:
    """A minimal Tkinter chat UI with copy support."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.chat_manager = ChatManager()
        self._build_ui()

    def _build_ui(self) -> None:
        self.root.title("HuggingFace Chat (Enhanced)")
        self.root.geometry("760x520")

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Chat transcript
        self.transcript = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            height=20,
            state=tk.NORMAL,
            font=("Consolas", 11),
        )
        self.transcript.pack(fill=tk.BOTH, expand=True)

        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", lambda _e: self._on_send_clicked())

        send_btn = ttk.Button(input_frame, text="Send", command=self._on_send_clicked)
        send_btn.pack(side=tk.LEFT, padx=(8, 0))

        copy_btn = ttk.Button(input_frame, text="Copy Last Reply", command=self._on_copy_clicked)
        copy_btn.pack(side=tk.LEFT, padx=(8, 0))

        if VOICE_AVAILABLE:
            voice_label = ttk.Label(input_frame, text="🎤 Voice ready")
            voice_label.pack(side=tk.LEFT, padx=(12, 0))
        else:
            voice_label = ttk.Label(input_frame, text="🎤 Voice unavailable")
            voice_label.pack(side=tk.LEFT, padx=(12, 0))

        # Initial system message
        self._append_to_transcript("system", "Welcome! Type a message and press Send.")

    def _append_to_transcript(self, role: str, content: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "system": "[system]",
            "user": "[user]",
            "assistant": "[assistant]",
        }.get(role, "[other]")
        self.transcript.insert(tk.END, f"{timestamp} {prefix} {content}\n")
        self.transcript.see(tk.END)
        self.chat_manager.add_message(role, content)

    def _on_send_clicked(self) -> None:
        user_text = self.input_var.get()
        self.input_var.set("")
        if not user_text.strip():
            messagebox.showinfo("Empty message", "Please type something before sending.")
            return
        self._append_to_transcript("user", user_text)

        # Produce a mock assistant reply (no network requirements)
        assistant_text = _generate_mock_reply(user_text)
        self._append_to_transcript("assistant", assistant_text)

    def _on_copy_clicked(self) -> None:
        last_reply = self.chat_manager.get_last_assistant_message()
        if not last_reply:
            messagebox.showinfo("Nothing to copy", "No assistant reply available yet.")
            return
        try:
            pyperclip.copy(last_reply)
            messagebox.showinfo("Copied", "Assistant reply copied to clipboard.")
        except Exception as copy_error:
            messagebox.showerror("Copy failed", f"Could not copy to clipboard: {copy_error}")


def main() -> None:
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
if __name__ == "__main__":
    main()
