import os
import streamlit as st
from langchain.agents import Tool
from langchain.chains import LLMChain
from langchain_community.utilities import SerpAPIWrapper
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
import chromadb
import asyncio
import requests
from bs4 import BeautifulSoup
from PIL import Image
import io
import base64
from dotenv import load_dotenv
import time

# Initialize models and components globally
llm = None
vision_model = None
search = None
collection = None

def initialize_components():
    global llm, vision_model, search, collection
    load_dotenv()
    llm = ChatOllama(model="llama2")
    vision_model = ChatOllama(model="llava")
    search = SerpAPIWrapper()
    chroma_client = chromadb.PersistentClient(path="./chromadb_data")
    collection = chroma_client.get_or_create_collection(
        name="search_results",
        metadata={"hnsw:space": "cosine"}
    )

def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def validate_image(url):
    try:
        response = requests.get(url, timeout=5, stream=True)
        if response.status_code != 200:
            return False
            
        # Check content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            return False
            
        # Validate image by reading first 32KB
        img = Image.open(io.BytesIO(next(response.iter_content(32768))))
        
        # Validate format and size
        if img.format not in ['JPEG', 'JPG', 'PNG']:
            return False
            
        if img.size[0] < 100 or img.size[1] < 100:
            return False
            
        return True
    except Exception:
        return False

def scrape_images(query, num_images=3):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(
            f"https://www.google.com/search?q={query}&tbm=isch",
            headers=headers
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        
        image_urls = []
        for img in soup.find_all('img'):
            if len(image_urls) >= num_images:
                break
                
            if 'src' in img.attrs:
                url = img['src']
                if url.startswith('http') and validate_image(url):
                    image_urls.append(url)
                    
        return image_urls[:num_images]
        
    except Exception as e:
        st.error(f"Error scraping images: {str(e)}")
        return []

def download_image(url, retry_count=3):
    for i in range(retry_count):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                
                # Convert to RGB JPEG
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                    
                temp_path = os.path.abspath(f"temp_image_{time.time()}.jpg")
                img.save(temp_path, format='JPEG', quality=85, optimize=True)
                return temp_path
                
        except Exception as e:
            if i == retry_count - 1:
                raise e
            time.sleep(1)
    return None

def process_image(url, context):
    try:
        temp_path = download_image(url)
        if not temp_path:
            return "Failed to download image"
            
        try:
            import ollama

            res = ollama.chat(
                model='llava',
                messages=[
                    {
                        'role': 'user',
                        'content': 'Describe this image',
                        'images': [temp_path]
                    }
                ]
            )
            return res['message']['content']
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return f"Error processing image: {str(e)}"

def process_images(urls, context):
    return [process_image(url, context) for url in urls]

def generate_combined_analysis(text_results, image_analyses, query):
    prompt = f"""
    Query: {query}
    
    Text Analysis: {text_results}
    
    Image Analyses: {image_analyses}
    
    Separate images by their order in this way:
    Image n
    Content of the image n

    Please provide a comprehensive analysis that:
    1. Connects the visual and textual information
    2. Highlights the most relevant findings
    3. Ensures all information relates to the original query
    4. Identifies any discrepancies or inconsistencies
    """
    return llm.predict(prompt)

def main():
    st.title("Advanced Search Analysis")
    
    # Initialize components 
    initialize_components()
    
    # Single search input
    text_query = st.text_input("Enter your search query")
    search_button = st.button("Search and Analyze")
    
    if search_button and text_query:
        with st.spinner('Processing...'):
            try:
                # Text analysis
                article_list = search.run(text_query)
                
                # Safely add to collection with proper hash
                try:
                    collection.add(
                        documents=[str(text_results)],  # Convert to string
                        metadatas=[{"query": text_query}]
                    )
                except Exception as e:
                    st.warning(f"Failed to store results: {str(e)}")
                
                # Display text results
                st.subheader("Text Analysis")
                st.write(text_results)
                
                # Image analysis with context
                st.subheader("Image Analysis")
                image_urls = scrape_images(text_query)
                
                # Display scraped images
                for url in image_urls:
                    st.image(url, width=200)
                
                # Process images synchronously
                image_analyses = process_images(image_urls, text_query)
                for analysis in image_analyses:
                    st.write(analysis)
                
                # Combined analysis
                st.subheader("Combined Analysis")
                combined_analysis = generate_combined_analysis(text_results, image_analyses, text_query)
                st.write(combined_analysis)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()