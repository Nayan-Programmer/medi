from app import app
import nltk
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Download required NLTK resources
def download_nltk_resources():
    try:
        resources = ['punkt', 'punkt_tab', 'stopwords', 'wordnet']
        for resource in resources:
            try:
                nltk.download(resource, quiet=True)
                logging.info(f"NLTK resource '{resource}' downloaded successfully")
            except Exception as e:
                logging.error(f"Error downloading NLTK resource '{resource}': {str(e)}")
    except Exception as e:
        logging.error(f"Error in download_nltk_resources: {str(e)}")

# Download resources
download_nltk_resources()

# For Vercel deployment
app.debug = False

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
