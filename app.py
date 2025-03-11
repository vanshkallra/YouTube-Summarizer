import streamlit as st

from dotenv import load_dotenv
load_dotenv()  #load the env variables

import os

from openai import OpenAI
# from google.generativeai as genai

from youtube_transcript_api import YouTubeTranscriptApi

import requests
import random
from itertools import cycle

with open("valid_proxies.txt", "r") as f:
    proxies= f.read().split("\n")

# Rotate through proxies using itertools
proxy_pool = cycle(proxies)

def get_transcript(url_link):
    try:
        video_id = url_link.split("watch?v=")[-1]
        
        # Get next proxy from pool
        current_proxy = next(proxy_pool)
        proxies = {
            "http": f"http://{current_proxy}",
            "https": f"http://{current_proxy}"
        }
        
        # Add retry logic with proxy rotation
        max_retries = 3
        for attempt in range(max_retries):
            try:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id, 
                    proxies=proxies
                )
                transcript_joined = " ".join([line['text'] for line in transcript])
                return transcript_joined
                
            except Exception as e:
                if attempt < max_retries - 1:
                    # Rotate proxy on failure
                    current_proxy = next(proxy_pool)
                    proxies = {
                        "http": f"http://{current_proxy}",
                        "https": f"http://{current_proxy}"
                    }
                    continue
                raise e
                
    except Exception as e:
        st.error(f"Failed to get transcript: {str(e)}")
        return None


# # GETTING THE TRANSCRIPT
# def get_transcript(url_link):
#     try:
#         video_id=url_link.split("watch?v=")[-1]
#         transcript=YouTubeTranscriptApi.get_transcript(video_id)
#         transcript_joined=""
#         for line in transcript:
#             transcript_joined += " " + line['text']
            
#         return transcript_joined
    
#     except Exception as e:
#         raise e
    


# Check for API key in secrets or environment variables
api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in secrets or environment variables.")


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key
)

# GENERATING SUMMARY FROM TRANSCRIPT USING PROMPT AND DEEPSEEL R1 MODEL
def generate_summary(transcript, prompt):
    completion = client.chat.completions.create(
    extra_body={},
    messages=[
        {
        "role": "user",
        "content": prompt
        }
    ],
    model="deepseek/deepseek-chat:free",
    temperature=1, # Temperature controls randomness in the response
    max_tokens=256, # Maximum number of tokens in the response
    top_p=1, # Top-p (nucleus) sampling parameter, higher values make output more focused
    frequency_penalty=0, # Frequency penalty discourages the model from repeating words or phrases
    presence_penalty=0 # Presence penaty discourages the model from adding verbose or unnecessary words

    )
    return completion.choices[0].message.content


# GENERATING DETAILED NOTES
def generate_detailed_notes(transcript, prompt):
    completion = client.chat.completions.create(
    extra_body={},
    messages=[
        {
        "role": "user",
        "content": prompt
        }
    ],
    model="deepseek/deepseek-chat:free",
    temperature=1, # Temperature controls randomness in the response
    )
    return completion.choices[0].message.content



# MAKING THE FRONTEND 
st.title("Youtube Video Summarizer")
url_link=st.text_input("Enter the YouTube Video Link: ")

if url_link:
    video_id=url_link.split("watch?v=")[-1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    
if st.button("Get Summary"):
    transcript=get_transcript(url_link)
    
    if transcript:
        prompt = f'"Summarize this video transcript , make sure you understand its from a youtube video: \ntext = {transcript}"'
        summary=generate_summary(transcript,prompt)
        
        st.markdown("Summary: ")
        st.write(summary)
        
if st.button("Get Detailed Notes"):
    transcript=get_transcript(url_link)
    
    if transcript:
        prompt = f'"Generate detailed notes as key points from this video transcript , make sure you understand its from a youtube video: \ntext = {transcript}"'
        notes=generate_detailed_notes(transcript,prompt)
        
        st.markdown("Key Points: ")
        st.write(notes)
