# YouTube Transcript Summarizer

A Streamlit web application that extracts transcripts from YouTube videos and generates concise summaries using the Hugging Face API.

![YouTube Transcript Summarizer](https://raw.githubusercontent.com/gopiashokan/YouTube-Video-Transcript-Summarizer-with-GenAI/main/image/youtube_banner.JPG)

## Features

- Extract transcripts from any YouTube video with available captions
- Support for multiple languages (if available in the video)
- Generate concise summaries of video content using Hugging Face's BART model
- Download both the summary and full transcript
- Simple and intuitive user interface
- No premium API keys required

## Demo

[Include screenshots or GIF of your application here]

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/youtube-transcript-summarizer.git
   cd youtube-transcript-summarizer
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and go to the URL displayed in your terminal (typically http://localhost:8501)

3. Paste a YouTube video URL in the input field

4. Select the transcript language from the dropdown menu

5. Click "Submit" to generate the summary

6. Use the download buttons to save the summary or full transcript if needed

## How It Works

1. The application extracts the video ID from the provided YouTube URL
2. It fetches the available transcript languages using the YouTube Transcript API
3. After selecting a language, it retrieves the full transcript
4. The transcript is sent to the Hugging Face API for summarization using the BART model
5. The summary is displayed to the user, with options to view the full transcript or download both

## Technical Details

- **Frontend**: Streamlit
- **APIs**:
  - YouTube Transcript API for extracting captions
  - Hugging Face Inference API (facebook/bart-large-cnn model) for summarization
- **Language**: Python 3.8+

## Limitations

- Works only with YouTube videos that have captions available
- The free Hugging Face API has usage limits
- Very long transcripts may be truncated before summarization
- Summary quality depends on the clarity and structure of the original transcript

## License

[MIT License](LICENSE)

## Acknowledgements

- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)
- [Hugging Face](https://huggingface.co/)
- [Streamlit](https://streamlit.io/)
- [BART model](https://huggingface.co/facebook/bart-large-cnn)

## Contact

[Your Name] - [your.email@example.com]

Project Link: [https://github.com/your-username/youtube-transcript-summarizer](https://github.com/your-username/youtube-transcript-summarizer)
