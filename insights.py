import streamlit as st
import os
from llama_index.core import (
    VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings, load_index_from_storage
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.groq import Groq
import requests
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Sample insights and metrics data for visualization
data = {
    "performance": "low",
    "valuation": "high",
    "growth": "low",
    "profitability": "high",
    "entry point": "avg",
    "red flags": "low"
}
insights = [
    "Hasn't fared well - amongst the low performers",
    "Seems to be overvalued vs the market average",
    "Lagging behind the market in financial growth",
    "Showing good signs of profitability & efficiency",
    "The stock is overpriced but is not in the overbought zone"
]

# Sidebar for option selection and styling
st.sidebar.title("Select Company")
import streamlit as st

# Define URL based on the Streamlit choice
choice = st.sidebar.radio("Choose:", ["HDFC", "Reliance"])
URL = (
    "https://www.tickertape.in/stocks/hdfc-bank-HDBK"
    if choice == "HDFC"
    else "https://www.tickertape.in/stocks/reliance-industries-RELI"
)

# Function for content scraping (Code 1)
def scrape_content(url):
    driver_path = "/Users/aryansood/Downloads/chromedriver-mac-arm64/chromedriver"  # Update path
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "p")))
    elements = driver.find_elements(By.XPATH, "//p | //h1 | //h2 | //h3 | //h4 | //h5 | //h6 | //li | //span | //div")
    content = " ".join(element.text for element in elements if element.text.strip())
    driver.quit()
    return content

# Run scraper based on choice
if choice.lower() == "hdfc":
    url = "https://www.tickertape.in/stocks/hdfc-bank-HDBK"
elif choice.lower() == "reliance":
    url = "https://www.tickertape.in/stocks/reliance-industries-RELI"

# Define the file path
file_path = f"temp_files/{choice}.txt"

# Check if the file already exists
if os.path.exists(file_path):
    print("not scraped")
    # If it exists, read the content from the file
    with open(file_path, "r") as file:
        scraped_content = file.read()
else:
    # If it doesn't exist, scrape the content
    scraped_content = scrape_content(url)
    # Save the scraped content to the file
    with open(file_path, "w") as file:
        file.write(scraped_content)


# Function to process scraped data (part of Code 1)
def legality(file_path):
    GROQ_API_KEY = "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"
    Settings.llm = Groq(model="llama3-8b-8192", api_key= GROQ_API_KEY)
    Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Settings.node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=200)

    reader = SimpleDirectoryReader(input_dir=file_path)
    documents = reader.load_data()
    nodes = Settings.node_parser.get_nodes_from_documents(documents, show_progress=True)

    vector_index = VectorStoreIndex.from_documents(documents, node_parser=nodes)
    vector_index.storage_context.persist(persist_dir="storage_mini")
    storage_context = StorageContext.from_defaults(persist_dir="storage_mini")
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
    q6 = """Return the financial quantifiers in JSON format:
    { "performance" : low/avg/high, "valuation" : low/avg/high, "growth" : low/avg/high,
      "profitability" :  low/avg/high, "entry point" :  low/avg/high, "red flags" :  low/avg/high, }
      Also return all the insights written on the page."""
    return str(query_engine.query(q6))

# Display scraped data
a = legality("temp_files/")

# Color mapping for metrics and darker font colors
color_map = {"low": "#FFCCCC", "high": "#CCFFCC", "avg": "#FFFF99"}
text_color_map = {"low": "#990000", "high": "#006600", "avg": "#CCCC00"}

# Sidebar CSS for gradient background
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #6a1b9a, #8e24aa);
        color: white;
    }
    .metric-box {
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Display metrics in sidebar
st.sidebar.header("Financial Metrics")
for key, value in data.items():
    st.sidebar.markdown(f"""
        <div class="metric-box" style="background-color: {color_map[value]}; color: {text_color_map[value]};">
            {key.capitalize()}: {value.capitalize()}
        </div>
    """, unsafe_allow_html=True)

# Main insights area
st.title("Insights")
st.markdown("""
    <style>
    .insights {
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #d1c4e9; /* Subtle outline color */
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Slight shadow for depth */
    }
    </style>
""", unsafe_allow_html=True)

for insight in insights:
    st.markdown(f"<div class='insights'>• {insight}</div>", unsafe_allow_html=True)

