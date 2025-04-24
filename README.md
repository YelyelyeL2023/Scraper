# Advanced Search Analysis

This project is a Streamlit-based web application that performs advanced search analysis by combining text and image search results. It leverages large language models (LLMs) and vision models to provide comprehensive, multi-modal insights for any user query.

## Features

- **Text Search & Analysis:** Uses [SerpAPI](https://serpapi.com/) to fetch and analyze search results for a given query.
- **Image Scraping & Analysis:** Scrapes images from Google Images, validates them, and uses a vision LLM (LLaVA) to describe and analyze each image.
- **Combined Multi-Modal Analysis:** Merges textual and visual information into a single, coherent analysis using an LLM.
- **Persistent Storage:** Stores search results in a local ChromaDB vector database for future retrieval and analysis.
- **User-Friendly Interface:** Built with Streamlit for easy interaction.

## Project Structure

```
.
├── .gitignore
├── main.py
└── chromadb_data/
    ├── chroma.sqlite3
    └── ... (ChromaDB vector storage files)
```

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com/) (for running LLMs locally)
- [Streamlit](https://streamlit.io/)
- [LangChain](https://python.langchain.com/)
- [ChromaDB](https://docs.trychroma.com/)
- [SerpAPI](https://serpapi.com/) account and API key
- Other dependencies: `requests`, `beautifulsoup4`, `Pillow`, `python-dotenv`

## Installation

1. **Clone the repository:**
    ```sh
    git clone <your-repo-url>
    cd Scraper-main
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
    *(Create `requirements.txt` with the following content if not present:)*

    ```
    streamlit
    langchain
    langchain_community
    langchain_ollama
    chromadb
    requests
    beautifulsoup4
    pillow
    python-dotenv
    ```

3. **Set up environment variables:**

    Create a `.env` file in the project root with your SerpAPI key:
    ```
    SERPAPI_API_KEY=your_serpapi_api_key
    ```

4. **Install and run Ollama:**

    - Download and install Ollama from [https://ollama.com/](https://ollama.com/)
    - Pull the required models:
        ```sh
        ollama pull llama2
        ollama pull llava
        ```

## Usage

1. **Start the Streamlit app:**
    ```sh
    streamlit run main.py
    ```

2. **Interact with the app:**
    - Enter your search query in the input box.
    - Click "Search and Analyze".
    - View the text analysis, image analysis, and combined insights.

## How It Works

- **Text Analysis:**  
  The app uses SerpAPI to fetch search results for the query and analyzes them using the `llama2` LLM.

- **Image Analysis:**  
  The app scrapes images from Google Images, validates them, and uses the `llava` vision model to generate descriptions.

- **Combined Analysis:**  
  The app prompts the LLM to synthesize both text and image analyses into a comprehensive report.

- **Data Storage:**  
  All search results are stored in a local ChromaDB vector database for future reference.

## File Overview

- [`main.py`](main.py): Main application code containing all logic for search, scraping, analysis, and UI.
- [`chromadb_data/`](chromadb_data/): Directory for persistent ChromaDB storage.
- [`.gitignore`](.gitignore): Ignores `.env` and other sensitive files.

## Notes

- **SerpAPI**: You must have a valid SerpAPI key in your `.env` file.
- **Ollama**: Ensure Ollama is running and the required models are available.
- **Google Images Scraping**: This is done via HTML parsing and may break if Google changes its markup.
- **Image Analysis**: Only images in JPEG/JPG/PNG format and larger than 100x100 pixels are processed.

## Troubleshooting

- If you encounter issues with model loading, ensure Ollama is running and the models are pulled.
- If image scraping fails, check your internet connection and ensure Google Images is accessible.
- For SerpAPI errors, verify your API key and usage limits.

## License

This project is for educational and research purposes only.

---

**Author:**  
Yelarys
