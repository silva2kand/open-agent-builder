#!/usr/bin/env python3
"""
Enhanced HuggingFace Chat with Voice Input and Improved Copy Support
Fixed chat replay errors and enhanced Tamil-English voice support
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

# Voice imports with fallback handling
VOICE_AVAILABLE = False
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
    print("✅ Voice modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Voice modules not available: {e}")
    print("Run: pip install SpeechRecognition pyttsx3 pyaudio")

class ChatManager:
    """Manages chat history with replay protection and copy functionality"""
    ...existing code...
if __name__ == "__main__":
    main()
