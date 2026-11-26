# Lecture AI

Lecture AI is a Python desktop application I built to help with lectures.

You can add a lecture as a PDF, Word file, text file, video, or audio file. The program extracts the content, converts speech to text when needed, and then uses a local AI model to summarize and analyze the lecture.

It can also keep processed lectures organized and create one combined reference containing all of them.

## Features

- Read PDF, Word, and text files
- Transcribe audio and video locally using faster-whisper (a Whisper implementation)
- Summarize lectures using a local Ollama model
- Process multiple lectures
- Save a separate summary for each lecture
- Create one combined reference containing all lectures
- Generate HTML versions of the summaries
- Run the AI locally without a paid API

## Built With

- Python
- Tkinter
- Ollama
- faster-whisper
- FFmpeg
- Markdown
- HTML

## Requirements

### Python

Python 3.10 or newer.

Check your version:

```bash
python --version
```

### Ollama

The AI part of the project runs through Ollama.

Download it from:

https://ollama.com/download

After installing Ollama, run:

```bash
ollama serve
```

Then download an AI model.

For a medium/powerful computer:

```bash
ollama pull qwen2.5:7b
```

For a lower-spec computer:

```bash
ollama pull llama3.2:3b
```

You can change the model name from the application if you want to use another Ollama model.

### FFmpeg

FFmpeg is needed for audio and video files.

**Windows:**

```bash
winget install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

**Linux:**

```bash
sudo apt install ffmpeg
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Mo7am2d-1/Lecture-AI.git
cd Lecture-AI
```

Create a virtual environment:

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Program

First, make sure Ollama is running:

```bash
ollama serve
```

Then open another terminal and run:

```bash
python app.py
```

## How It Works

1. Add a lecture file.
2. Give the lecture a name.
3. Add more lectures if needed.
4. Click **"🚀 معالجة الكل"**.
5. The program extracts the text or transcribes the audio/video.
6. The content is sent to the local Ollama model for summarization and analysis.
7. Each lecture gets its own summary.
8. You can open the summaries from the application.
9. You can also create one combined reference for all processed lectures.
10. The summaries can be opened as HTML pages and saved as PDF if needed.

## Screenshots

Some screenshots from the application are included below.

![Lecture AI Screenshot 1](screenshots/photo_1_2026-09-08_00-20-40.jpg)

![Lecture AI Screenshot 2](screenshots/photo_2_2026-09-08_00-20-40.jpg)

![Lecture AI Screenshot 3](screenshots/photo_3_2026-09-08_00-20-40.jpg)

![Lecture AI Screenshot 4](screenshots/photo_4_2026-09-08_00-20-40.jpg)

![Lecture AI Screenshot 5](screenshots/photo_5_2026-09-08_00-20-40.jpg)

![Lecture AI Screenshot 6](screenshots/photo_6_2026-09-08_00-20-40.jpg)

![Lecture AI Screenshot 7](screenshots/photo_7_2026-09-08_00-20-40.jpg)

![Lecture AI Screenshot 8](screenshots/photo_8_2026-09-08_00-20-40.jpg)

![Lecture AI Screenshot 9](screenshots/photo_9_2026-09-08_00-20-40.jpg)

## Project Structure

```text
Lecture-AI/
├── app.py                  # Main application
├── extractors.py           # PDF, Word and text extraction
├── transcriber.py          # Audio/video transcription
├── ai_engine.py            # Ollama AI processing
├── knowledge_base.py       # Saving summaries and building the reference
├── html_design.py          # HTML page design
├── requirements.txt        # Required Python packages
├── screenshots/            # Application screenshots
└── README.md               # Project documentation
```

The application also creates generated files and folders while processing lectures, such as summaries and the combined reference.

## Local AI

The main reason I used Ollama in this project is to keep the AI part local.

The application does not need a paid AI API. The lecture content is processed on the computer using the local AI model.

An internet connection is only needed when downloading the required models for the first time.

## Notes

- Whisper downloads its model the first time it is used.
- Long lectures can be split into smaller parts before processing.
- Larger AI models can give better results but need more RAM/VRAM.
- Generated summaries are saved locally.
- Video and audio processing requires FFmpeg.

## Why I Made This

I wanted to build something that could actually be useful for studying instead of making a simple AI demo.

The project gave me a chance to work with Python, desktop applications, document processing, speech-to-text, local AI models, and generating HTML/Markdown content in one project.

## Author

**Mohamed Faisal**

GitHub: [Mo7am2d-1](https://github.com/Mo7am2d-1)

LinkedIn: [Mohamed Faisal](https://www.linkedin.com/in/mohamed-faisal-safwat-saqr-81abb342b)

---

If you find the project useful, feel free to star it.
