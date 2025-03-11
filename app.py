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

with open("valid_proxies2.txt", "r") as f:
    proxies= f.read().split("\n")
    
    
counter = 0

def get_transcript(url_link):
    global counter
    
    try:
        video_id = url_link.split("watch?v=")[-1]
        
        # Print which proxy we're using
        print(f"Using the proxy: {proxies[counter]}")
        
        # Set up proxy configuration
        proxy_dict = {
            "http": proxies[counter],
            "https": proxies[counter]
        }
        
        # Get transcript using the current proxy
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            proxies=proxy_dict
        )
        
        # Join the transcript text
        transcript_joined = ""
        for line in transcript:
            transcript_joined += " " + line['text']
            
        return transcript_joined
    
    except Exception as e:
        print("Failed")
        raise e
    
    finally:
        # Increment counter and wrap around if needed
        counter += 1
        if counter >= len(proxies):
            counter = 0
            
def get_transcript_with_retry(url_link, max_retries=3):
    for _ in range(max_retries):
        try:
            return get_transcript(url_link)
        except Exception as e:
            print(f"Retry due to: {e}")
    
    raise Exception(f"Failed after {max_retries} attempts with different proxies")



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
    # max_tokens=256, # Maximum number of tokens in the response
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
    # transcript=get_transcript(url_link)
    transcript=get_transcript_with_retry(url_link)
    
    
    if transcript:
        prompt = f'"Summarize this video transcript in less than 250 words , make sure you understand its from a youtube video: \ntext = {transcript}"'
        summary=generate_summary(transcript,prompt)
        
        st.markdown("Summary: ")
        st.write(summary)
        
if st.button("Get Detailed Notes"):
    transcript=get_transcript_with_retry(url_link)
    
    if transcript:
        prompt = f'"Generate detailed notes as key points from this video transcript , make sure you understand its from a youtube video: \ntext = {transcript}"'
        notes=generate_detailed_notes(transcript,prompt)
        
        st.markdown("Key Points: ")
        st.write(notes)
