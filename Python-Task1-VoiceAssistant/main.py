
import datetime as dt
import queue
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox
from urllib.parse import quote_plus

import requests

try:
    import wikipedia
except ImportError:
    wikipedia = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


# =========================================================
# NOVA THEME
# =========================================================

BG = "#0B1120"
PANEL = "#151F33"
CHAT_BG = "#101B30"
INPUT_BG = "#202E46"

ACCENT = "#7189FF"
ACCENT_HOVER = "#5D75EA"

GREEN = "#34D399"
GREEN_BUTTON = "#087F68"
GREEN_HOVER = "#109B7E"

TEXT = "#F1F5F9"
MUTED = "#A8B4C8"
BORDER = "#344563"
ERROR = "#F87171"


# =========================================================
# NOVA APPLICATION
# =========================================================

class Nova:

    def __init__(self, root):

        self.root = root

        self.root.title("Nova | Desktop Voice Assistant")
        self.root.geometry("850x650")
        self.root.minsize(680, 580)
        self.root.configure(bg=BG)

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        # Application state
        self.processing = False
        self.closing = False

        # Thread communication queues
        self.ui_queue = queue.Queue()
        self.speech_queue = queue.Queue()

        # Text-to-speech availability
        self.tts_available = pyttsx3 is not None

        # Build GUI
        self.build_interface()

        # Start background workers
        self.root.after(100, self.process_ui_queue)
        threading.Thread(
            target=self.speech_worker,
            daemon=True
        ).start()

        # Initial welcome message
        self.log(
            "NOVA",
            "Hello! I'm Nova, your personal desktop assistant.\n\n"
            "I can help you with:\n"
            "• Current time and date\n"
            "• Opening websites\n"
            "• Google searches\n"
            "• Wikipedia information\n"
            "• Current weather information\n\n"
            "TRY THESE COMMANDS:\n"
            "• What time is it?\n"
            "• What is today's date?\n"
            "• Open YouTube\n"
            "• Search Python tutorials\n"
            "• Wikipedia Ada Lovelace\n"
            "• Weather in Kolkata\n\n"
            "Type a command below or click LISTEN to speak."
        )

        if self.tts_available:
            self.set_status("Ready | Nova is online", GREEN)
        else:
            self.set_status("Ready | Voice output unavailable", MUTED)

    # =====================================================
    # GUI DESIGN
    # =====================================================

    def build_interface(self):

        # Header
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(14, 8))

        title_area = tk.Frame(header, bg=BG)
        title_area.pack(side="left")

        tk.Label(
            title_area,
            text="NOVA",
            font=("Segoe UI", 29, "bold"),
            fg=ACCENT,
            bg=BG
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="YOUR PERSONAL DESKTOP VOICE ASSISTANT",
            font=("Segoe UI", 9, "bold"),
            fg=MUTED,
            bg=BG
        ).pack(anchor="w")

        self.status_label = tk.Label(
            header,
            text="● Starting...",
            font=("Segoe UI", 10, "bold"),
            fg=GREEN,
            bg=BG
        )

        self.status_label.pack(side="right")

        # Conversation panel
        chat_container = tk.Frame(
            self.root,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        chat_container.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=8
        )

        # Chat heading
        chat_header = tk.Frame(chat_container, bg=PANEL)
        chat_header.pack(fill="x", padx=15, pady=11)

        tk.Label(
            chat_header,
            text="CONVERSATION",
            font=("Segoe UI", 11, "bold"),
            fg=TEXT,
            bg=PANEL
        ).pack(side="left")

        tk.Label(
            chat_header,
            text="NOVA CHAT",
            font=("Segoe UI", 9, "bold"),
            fg=MUTED,
            bg=PANEL
        ).pack(side="right")

        tk.Frame(
            chat_container,
            bg=BORDER,
            height=1
        ).pack(fill="x")

        # Chat text and scrollbar
        chat_area = tk.Frame(chat_container, bg=CHAT_BG)
        chat_area.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        self.chat = tk.Text(
            chat_area,
            bg=CHAT_BG,
            fg=TEXT,
            font=("Segoe UI", 10),
            wrap="word",
            relief="flat",
            padx=15,
            pady=12,
            state="disabled",
            insertbackground=TEXT,
            selectbackground=ACCENT,
            spacing1=3,
            spacing3=5
        )

        scrollbar = tk.Scrollbar(
            chat_area,
            command=self.chat.yview,
            bg=PANEL,
            troughcolor=CHAT_BG,
            activebackground=ACCENT
        )

        self.chat.configure(
            yscrollcommand=scrollbar.set
        )

        self.chat.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Chat message styles
        self.chat.tag_configure(
            "nova",
            foreground=ACCENT,
            font=("Segoe UI", 10, "bold")
        )

        self.chat.tag_configure(
            "user",
            foreground=GREEN,
            font=("Segoe UI", 10, "bold")
        )

        self.chat.tag_configure(
            "message",
            foreground=TEXT,
            font=("Segoe UI", 10)
        )

        # =================================================
        # INPUT SECTION
        # =================================================

        input_section = tk.Frame(self.root, bg=BG)

        input_section.pack(
            fill="x",
            padx=24,
            pady=(5, 5)
        )

        tk.Label(
            input_section,
            text="TYPE YOUR COMMAND HERE",
            font=("Segoe UI", 9, "bold"),
            fg="#B9C7E8",
            bg=BG
        ).pack(anchor="w", pady=(0, 7))

        input_row = tk.Frame(input_section, bg=BG)
        input_row.pack(fill="x")

        self.entry = tk.Entry(
            input_row,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground="white",
            font=("Segoe UI", 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#526687",
            highlightcolor=ACCENT
        )

        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=12
        )

        self.placeholder = "Type here... e.g. What time is it?"

        self.entry.insert(0, self.placeholder)
        self.entry.configure(fg=MUTED)

        self.entry.bind(
            "<FocusIn>",
            self.remove_placeholder
        )

        self.entry.bind(
            "<FocusOut>",
            self.add_placeholder
        )

        self.entry.bind(
            "<Return>",
            lambda event: self.send()
        )

        self.send_button = self.make_button(
            input_row,
            "SEND ➤",
            self.send,
            ACCENT,
            ACCENT_HOVER,
            width=11
        )

        self.send_button.pack(
            side="left",
            padx=(10, 0),
            fill="y"
        )

        # =================================================
        # ACTION BUTTONS
        # =================================================

        actions = tk.Frame(self.root, bg=BG)

        actions.pack(
            fill="x",
            padx=24,
            pady=(7, 15)
        )

        self.listen_button = self.make_button(
            actions,
            "🎙  LISTEN",
            self.listen,
            GREEN_BUTTON,
            GREEN_HOVER
        )

        self.listen_button.pack(
            side="left",
            padx=(0, 8)
        )

        self.make_button(
            actions,
            "❔  HELP",
            self.help,
            BORDER,
            "#465C7D"
        ).pack(side="left", padx=5)

        self.make_button(
            actions,
            "CLEAR CHAT",
            self.clear_chat,
            BORDER,
            "#465C7D"
        ).pack(side="left", padx=5)

        tk.Label(
            actions,
            text="Type or speak to Nova",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=BG
        ).pack(side="right", pady=12)

    # =====================================================
    # BUTTON DESIGN
    # =====================================================

    def make_button(
        self,
        parent,
        text,
        command,
        color,
        hover,
        width=None
    ):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground=hover,
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=17,
            pady=12,
            width=width
        )

        button.bind(
            "<Enter>",
            lambda event: button.configure(bg=hover)
        )

        button.bind(
            "<Leave>",
            lambda event: button.configure(bg=color)
        )

        return button

    # =====================================================
    # INPUT PLACEHOLDER
    # =====================================================

    def remove_placeholder(self, event=None):

        if self.entry.get() == self.placeholder:

            self.entry.delete(0, "end")
            self.entry.configure(fg=TEXT)

    def add_placeholder(self, event=None):

        if not self.entry.get().strip():

            self.entry.insert(0, self.placeholder)
            self.entry.configure(fg=MUTED)

    # =====================================================
    # STATUS INDICATOR
    # =====================================================

    def set_status(self, text, color):

        self.status_label.configure(
            text="● " + text,
            fg=color
        )

    # =====================================================
    # CHAT DISPLAY
    # =====================================================

    def log(self, who, msg):

        if self.closing:
            return

        self.chat.configure(state="normal")

        if who.startswith("NOVA"):
            tag = "nova"
        else:
            tag = "user"

        self.chat.insert(
            "end",
            who + "\n",
            tag
        )

        self.chat.insert(
            "end",
            str(msg) + "\n\n",
            "message"
        )

        self.chat.see("end")

        self.chat.configure(state="disabled")

    def clear_chat(self):

        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")

        self.log(
            "NOVA",
            "Chat cleared. What can I help you with?"
        )

    # =====================================================
    # UI QUEUE
    # All Tkinter updates happen on the main thread.
    # =====================================================

    def process_ui_queue(self):

        if self.closing:
            return

        try:

            while True:

                event = self.ui_queue.get_nowait()

                event_type = event[0]

                if event_type == "status":

                    self.set_status(
                        event[1],
                        event[2]
                    )

                elif event_type == "message":

                    self.log(
                        event[1],
                        event[2]
                    )

                elif event_type == "response":

                    self.finish_command(
                        event[1],
                        event[2]
                    )

                elif event_type == "close":

                    self.close_app()
                    return

        except queue.Empty:
            pass

        self.root.after(
            100,
            self.process_ui_queue
        )

    # =====================================================
    # TEXT TO SPEECH
    # =====================================================

    def speech_worker(self):

        if not pyttsx3:
            return

        engine = None

        try:

            # Initialize the speech engine in its own thread.
            engine = pyttsx3.init()

            engine.setProperty("rate", 175)
            engine.setProperty("volume", 1.0)

            while not self.closing:

                text = self.speech_queue.get()

                if text is None:
                    break

                try:

                    self.ui_queue.put(
                        ("status", "Speaking...", GREEN)
                    )

                    engine.say(text)
                    engine.runAndWait()

                except Exception as error:

                    self.ui_queue.put(
                        (
                            "status",
                            "Ready | Speech error",
                            ERROR
                        )
                    )

                finally:

                    self.ui_queue.put(
                        ("status", "Ready | Nova is online", GREEN)
                    )

        except Exception:

            self.ui_queue.put(
                (
                    "status",
                    "Ready | Voice output unavailable",
                    MUTED
                )
            )

        finally:

            if engine:

                try:
                    engine.stop()
                except Exception:
                    pass

    def reply(self, msg):

        self.log("NOVA", msg)

        self.set_status(
            "Ready | Nova is online",
            GREEN
        )

        if self.tts_available:

            # Keep spoken output manageable.
            self.speech_queue.put(str(msg))

    # =====================================================
    # COMMAND INPUT
    # =====================================================

    def send(self):

        query = self.entry.get().strip()

        if not query or query == self.placeholder:
            return

        if self.processing:
            return

        self.entry.delete(0, "end")
        self.entry.configure(fg=TEXT)

        self.log("YOU", query)

        self.process_command(query)

    # =====================================================
    # COMMAND PROCESSING
    # =====================================================

    def process_command(self, query):

        self.processing = True

        self.send_button.configure(
            state="disabled",
            text="WAIT..."
        )

        self.listen_button.configure(
            state="disabled"
        )

        self.set_status(
            "Processing...",
            ACCENT
        )

        threading.Thread(
            target=self.command_worker,
            args=(query,),
            daemon=True
        ).start()

    def command_worker(self, query):

        try:

            response = self.command(query)

        except Exception as error:

            response = (
                "An unexpected error occurred: "
                + str(error)
            )

        should_exit = query.lower().strip() in (
            "exit",
            "quit",
            "stop"
        )

        self.ui_queue.put(
            ("response", response, should_exit)
        )

    def finish_command(self, response, should_exit=False):

        if self.closing:
            return

        self.processing = False

        self.send_button.configure(
            state="normal",
            text="SEND ➤"
        )

        self.listen_button.configure(
            state="normal"
        )

        self.reply(response)

        if should_exit:

            self.root.after(
                1800,
                self.close_app
            )

    # =====================================================
    # VOICE RECOGNITION
    # =====================================================

    def listen(self):

        if not sr:

            messagebox.showwarning(
                "Voice Recognition Unavailable",
                "SpeechRecognition is not installed.\n\n"
                "Install SpeechRecognition and PyAudio, "
                "or type your commands instead."
            )

            return

        if self.processing:
            return

        self.processing = True

        self.send_button.configure(
            state="disabled"
        )

        self.listen_button.configure(
            state="disabled",
            text="LISTENING..."
        )

        self.set_status(
            "Starting microphone...",
            GREEN
        )

        threading.Thread(
            target=self.listen_worker,
            daemon=True
        ).start()

    def listen_worker(self):

        try:

            recognizer = sr.Recognizer()

            with sr.Microphone() as source:

                self.ui_queue.put(
                    (
                        "status",
                        "Adjusting microphone...",
                        ACCENT
                    )
                )

                recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5
                )

                self.ui_queue.put(
                    (
                        "status",
                        "Listening... Speak now",
                        GREEN
                    )
                )

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=8
                )

            self.ui_queue.put(
                (
                    "status",
                    "Recognizing speech...",
                    ACCENT
                )
            )

            query = recognizer.recognize_google(audio)

            self.ui_queue.put(
                (
                    "message",
                    "YOU (VOICE)",
                    query
                )
            )

            try:

                response = self.command(query)

            except Exception as error:

                response = (
                    "An error occurred: "
                    + str(error)
                )

            should_exit = query.lower().strip() in (
                "exit",
                "quit",
                "stop"
            )

        except sr.WaitTimeoutError:

            response = (
                "I did not hear anything. "
                "Please click Listen and try again."
            )

            should_exit = False

        except sr.UnknownValueError:

            response = (
                "I could not understand your speech. "
                "Please speak clearly or type your command."
            )

            should_exit = False

        except sr.RequestError:

            response = (
                "The speech recognition service is unavailable. "
                "Please check your internet connection."
            )

            should_exit = False

        except Exception as error:

            response = (
                "I could not access your microphone.\n\n"
                "Check your microphone connection and "
                "Windows microphone permissions.\n\n"
                "Error: " + str(error)
            )

            should_exit = False

        self.ui_queue.put(
            ("response", response, should_exit)
        )

    # =====================================================
    # COMMANDS
    # =====================================================

    def command(self, query):

        text = query.lower().strip()

        # ---------------- TIME ----------------

        if "time" in text:

            current_time = dt.datetime.now().strftime(
                "%I:%M %p"
            )

            return "The current time is " + current_time

        # ---------------- DATE ----------------

        if "date" in text:

            current_date = dt.datetime.now().strftime(
                "%A, %d %B %Y"
            )

            return "Today is " + current_date

        # ---------------- OPEN WEBSITES ----------------

        if text.startswith("open "):

            websites = {
                "youtube": "https://www.youtube.com",
                "google": "https://www.google.com",
                "gmail": "https://mail.google.com",
                "github": "https://github.com"
            }

            website_name = text[5:].strip()

            if website_name in websites:

                webbrowser.open(
                    websites[website_name]
                )

                return (
                    "Opening "
                    + website_name
                    + " for you."
                )

            return (
                "I can currently open YouTube, Google, "
                "Gmail and GitHub."
            )

        # ---------------- GOOGLE SEARCH ----------------

        if text.startswith("search "):

            search_query = query[7:].strip()

            if not search_query:

                return "Please tell me what you want to search."

            search_url = (
                "https://www.google.com/search?q="
                + quote_plus(search_query)
            )

            webbrowser.open(search_url)

            return (
                "Searching the web for "
                + search_query
                + "."
            )

        # ---------------- WIKIPEDIA ----------------

        if text.startswith("wikipedia "):

            topic = query[10:].strip()

            if not wikipedia:

                return (
                    "Wikipedia support is unavailable. "
                    "Install the wikipedia package."
                )

            try:

                result = wikipedia.summary(
                    topic,
                    sentences=2
                )

                return result

            except Exception:

                return (
                    "I could not find a Wikipedia summary "
                    "for that topic."
                )

        # ---------------- WEATHER ----------------

        if text.startswith("weather in "):

            city = query[11:].strip()

            if not city:

                return "Please specify a city."

            try:

                geo_response = requests.get(
                    "https://geocoding-api.open-meteo.com/v1/search",
                    params={
                        "name": city,
                        "count": 1,
                        "language": "en",
                        "format": "json"
                    },
                    timeout=10
                )

                geo_response.raise_for_status()

                locations = geo_response.json().get(
                    "results",
                    []
                )

                if not locations:

                    return (
                        "I could not find the city "
                        + city
                        + "."
                    )

                place = locations[0]

                weather_response = requests.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": place["latitude"],
                        "longitude": place["longitude"],
                        "current": (
                            "temperature_2m,"
                            "relative_humidity_2m,"
                            "wind_speed_10m"
                        ),
                        "timezone": "auto"
                    },
                    timeout=10
                )

                weather_response.raise_for_status()

                weather_data = weather_response.json()

                current = weather_data["current"]

                return (
                    f"Current weather in {place['name']}:\n\n"
                    f"Temperature: {current['temperature_2m']}°C\n"
                    f"Humidity: {current['relative_humidity_2m']}%\n"
                    f"Wind speed: {current['wind_speed_10m']} km/h"
                )

            except requests.RequestException:

                return (
                    "The weather service is unavailable. "
                    "Please check your internet connection."
                )

            except (KeyError, ValueError, TypeError):

                return (
                    "I received an unexpected weather response. "
                    "Please try again."
                )

        # ---------------- HELP ----------------

        if text in ("help", "commands"):

            return (
                "Here are the commands I understand:\n\n"
                "TIME\n"
                "• What time is it?\n\n"
                "DATE\n"
                "• What is today's date?\n\n"
                "OPEN WEBSITES\n"
                "• Open YouTube\n"
                "• Open Google\n"
                "• Open Gmail\n"
                "• Open GitHub\n\n"
                "GOOGLE SEARCH\n"
                "• Search Python tutorials\n\n"
                "WIKIPEDIA\n"
                "• Wikipedia Ada Lovelace\n\n"
                "WEATHER\n"
                "• Weather in Kolkata\n\n"
                "EXIT\n"
                "• Exit"
            )

        # ---------------- EXIT ----------------

        if text in ("exit", "quit", "stop"):

            return "Goodbye! It was nice assisting you."

        # ---------------- UNKNOWN COMMAND ----------------

        return (
            "Sorry, I didn't understand that command.\n\n"
            "Type 'help' to see the available commands."
        )

    # =====================================================
    # HELP WINDOW
    # =====================================================

    def help(self):

        messagebox.showinfo(
            "Nova | Help",
            "WELCOME TO NOVA!\n\n"
            "You can type commands or use the microphone.\n\n"
            "TIME\n"
            "Ask: What time is it?\n\n"
            "DATE\n"
            "Ask: What is today's date?\n\n"
            "OPEN WEBSITES\n"
            "Ask: Open YouTube / Google / Gmail / GitHub\n\n"
            "GOOGLE SEARCH\n"
            "Ask: Search Python tutorials\n\n"
            "WIKIPEDIA\n"
            "Ask: Wikipedia Ada Lovelace\n\n"
            "WEATHER\n"
            "Ask: Weather in Kolkata\n\n"
            "EXIT\n"
            "Ask: Exit"
        )

    # =====================================================
    # CLOSE APPLICATION
    # =====================================================

    def close_app(self):

        if self.closing:
            return

        self.closing = True

        # Stop the speech worker if it is waiting.
        self.speech_queue.put(None)

        self.root.destroy()


# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = Nova(root)

    root.mainloop()
