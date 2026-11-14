# Nova Voice Assistant

Tkinter desktop assistant with typed commands, optional microphone speech recognition, text-to-speech, time/date, website shortcuts, Google search, Wikipedia summaries, and current city weather.

## Windows setup
Run in this folder:
```bash
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
python main.py
```
If PyAudio fails to install, try `python -m pip install pipwin` then `pipwin install pyaudio`. If microphone support remains unavailable, typed commands still work.

Speech recognition uses Google's online recognition service. Weather uses free Open-Meteo APIs. Example commands: `time`, `date`, `open YouTube`, `search Python tutorials`, `Wikipedia Ada Lovelace`, `weather in Kolkata`, `exit`.
