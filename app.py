import os
import langcodes
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from youtube_transcript_api import YouTubeTranscriptApi
from warnings import filterwarnings
import requests
import time

def streamlit_config():
    # page configuration
    st.set_page_config(page_title='YouTube Summarizer')

    # page header transparent color and Removes top padding 
    page_background_color = """
    <style>

    [data-testid="stHeader"] 
    {
    background: rgba(0,0,0,0);
    }

    .block-container {
        padding-top: 0rem;
    }

    </style>
    """
    st.markdown(page_background_color, unsafe_allow_html=True)

    # title and position
    add_vertical_space(2)
    st.markdown(f'<h2 style="text-align: center;">YouTube Transcript Summarizer</h2>',
                unsafe_allow_html=True)
    add_vertical_space(2)

def extract_languages(video_id):
    # Fetch the List of Available Transcripts for Given Video
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # Extract the Language Codes from List ---> ['en','ta']
    available_transcripts = [i.language_code for i in transcript_list]

    # Convert Language_codes to Human-Readable Language_names ---> 'en' into 'English'
    language_list = list({langcodes.Language.get(i).display_name() for i in available_transcripts})

    # Create a Dictionary Mapping Language_names to Language_codes
    language_dict = {langcodes.Language.get(i).display_name():i for i in available_transcripts}

    return language_list, language_dict

def extract_transcript(video_id, language):
    try:
        # Request Transcript for YouTube Video using API
        transcript_content = YouTubeTranscriptApi.get_transcript(video_id=video_id, languages=[language])
    
        # Extract Transcript Content from JSON Response and Join to Single Response
        transcript = ' '.join([i['text'] for i in transcript_content])

        return transcript
    
    except Exception as e:
        add_vertical_space(5)
        st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)
        return None

def generate_summary_with_huggingface(transcript_text):
    # Hugging Face API Key (provided)
    API_KEY = "Your_API_KEY"
    
    try:
        # Use the Hugging Face Inference API with BART model for summarization
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        
        # Truncate text if too long (BART model has token limits)
        max_length = 1024  # characters, approximate limit for better results
        if len(transcript_text) > max_length:
            st.info("Transcript is long, truncating for summarization...")
            transcript_text = transcript_text[:max_length]
            
        payload = {
            "inputs": transcript_text,
            "parameters": {
                "max_length": 500,
                "min_length": 100,
            }
        }
        
        # Make the API request
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # Check if model is loading
        if response.status_code == 503:
            st.warning("The model is loading. Please wait a moment...")
            time.sleep(10)  # Wait for model to load
            response = requests.post(API_URL, headers=headers, json=payload)
        
        # Process the response
        if response.status_code == 200:
            result = response.json()
            summary = result[0]["summary_text"]
            return summary
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return fallback_summarization(transcript_text)
    
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return fallback_summarization(transcript_text)

def fallback_summarization(text):
    """Simple extractive summarization as fallback"""
    st.warning("Using fallback summarization method...")
    sentences = text.split('. ')
    importance = {}
    
    # Simple frequency-based importance
    for i, sentence in enumerate(sentences):
        words = sentence.lower().split()
        importance[i] = len(set(words))
    
    # Get top sentences (about 20% of the original)
    top_sentences = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:max(3, len(sentences)//5)]
    top_sentences = sorted(top_sentences, key=lambda x: x[0])  # Sort by original order
    
    summary = '. '.join([sentences[i] for i, _ in top_sentences]) + '.'
    
    return "Summary (generated locally):\n\n" + summary

def parse_youtube_url(url):
    """Extract video ID from different YouTube URL formats"""
    try:
        if "youtube.com/watch" in url:
            # Regular youtube.com/watch?v=VIDEO_ID format
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            else:
                raise ValueError("Invalid YouTube URL format")
        elif "youtu.be" in url:
            # Short youtu.be/VIDEO_ID format
            video_id = url.split("/")[-1].split("?")[0]
        elif "youtube.com/embed" in url:
            # Embed format
            video_id = url.split("/")[-1].split("?")[0]
        elif "youtube.com/v" in url:
            # Old v format
            video_id = url.split("/")[-1].split("?")[0]
        else:
            raise ValueError("Unrecognized YouTube URL format")
        
        return video_id
    except Exception as e:
        raise ValueError(f"Could not extract video ID: {e}")

def main():
    # Filter the Warnings
    filterwarnings(action='ignore')

    # Streamlit Configuration Setup
    streamlit_config()

    # Initialize the Button Variable
    button = False

    with st.sidebar:
        image_url = 'https://upload.wikimedia.org/wikipedia/commons/e/e1/Logo_of_YouTube_%282015-2017%29.svg'
        st.image(image_url, use_column_width=True)
        add_vertical_space(2)
        
        st.write("### Using Hugging Face API")
        st.info("API Key is already configured. No need to refresh.")
        
        add_vertical_space(1)
        
        # Get YouTube Video Link From User 
        video_link = st.text_input(label='Enter YouTube Video Link')

        if video_link:
            try:
                # Extract the Video ID From URL
                video_id = parse_youtube_url(video_link)
                
                # Extract Language from Video_ID
                with st.spinner("Loading available languages..."):
                    language_list, language_dict = extract_languages(video_id)
                
                # User Select the Transcript Language
                language_input = st.selectbox(label='Select Transcript Language', 
                                            options=language_list)
                
                # Get Language_code from Dict
                language = language_dict[language_input]

                # Click Submit Button
                add_vertical_space(1)
                button = st.button(label='Submit')
            except Exception as e:
                st.error(f"Error processing video link: {str(e)}")

    # User Enter the Video Link and Click Submit Button
    if button and video_link:
        try:
            # Get video ID again (in case it was reloaded)
            video_id = parse_youtube_url(video_link)
            
            # UI Split into Columns
            _, col2, _ = st.columns([0.07,0.83,0.1])

            # Display the Video Thumbnail Image
            with col2:
                st.image(image=f'http://img.youtube.com/vi/{video_id}/0.jpg', 
                        use_column_width=True)
                st.markdown(f"[Open video on YouTube](https://www.youtube.com/watch?v={video_id})")

            # Extract Transcript from YouTube Video
            add_vertical_space(2)
            with st.spinner(text='Extracting Transcript...'):
                transcript_text = extract_transcript(video_id, language)

            if transcript_text:
                # Generating Summary using Hugging Face API
                with st.spinner(text='Generating Summary...'):
                    summary = generate_summary_with_huggingface(transcript_text)

                # Display the Summary
                if summary:
                    st.markdown("## Summary")
                    st.write(summary)
                    
                    # Show full transcript in expander
                    with st.expander("View Full Transcript"):
                        st.write(transcript_text)
                        
                    # Download options
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="Download Summary",
                            data=summary,
                            file_name=f"summary_{video_id}.txt",
                            mime="text/plain"
                        )
                    with col2:
                        st.download_button(
                            label="Download Transcript",
                            data=transcript_text,
                            file_name=f"transcript_{video_id}.txt",
                            mime="text/plain"
                        )
                else:
                    st.error("Failed to generate summary. Please try another video.")
            else:
                st.error("Failed to extract transcript. Please check if the video has captions.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        add_vertical_space(5)
        st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)