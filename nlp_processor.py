import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import json
import os
import logging

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Load our symptoms dataset
def load_symptoms():
    try:
        with open('data/symptoms_diseases.json', 'r') as file:
            data = json.load(file)
            # Extract all symptoms from all diseases
            all_symptoms = []
            for disease, info in data.items():
                all_symptoms.extend(info.get('symptoms', []))
            
            # Remove duplicates
            all_symptoms = list(set(all_symptoms))
            return all_symptoms
    except FileNotFoundError:
        logging.error("Symptoms data file not found")
        return []
    except json.JSONDecodeError:
        logging.error("Invalid JSON in symptoms file")
        return []

# Pre-process symptoms input
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and numbers
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stop words and lemmatize
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    
    return tokens

# Match input symptoms with known symptoms
def match_symptoms(processed_tokens, known_symptoms):
    matched_symptoms = []
    
    # Create phrases from consecutive tokens (bigrams and trigrams)
    phrases = []
    if len(processed_tokens) >= 2:
        for i in range(len(processed_tokens) - 1):
            phrases.append(processed_tokens[i] + " " + processed_tokens[i+1])
    
    if len(processed_tokens) >= 3:
        for i in range(len(processed_tokens) - 2):
            phrases.append(processed_tokens[i] + " " + processed_tokens[i+1] + " " + processed_tokens[i+2])
    
    for symptom in known_symptoms:
        symptom_lower = symptom.lower()
        
        # Check if any phrase matches
        for phrase in phrases:
            if phrase in symptom_lower or symptom_lower in phrase:
                if symptom not in matched_symptoms:
                    matched_symptoms.append(symptom)
                    break
        
        # Check individual tokens
        for token in processed_tokens:
            # If token length > 3 and is part of symptom or vice versa
            if len(token) > 3 and (token in symptom_lower or symptom_lower in token):
                if symptom not in matched_symptoms:
                    matched_symptoms.append(symptom)
                    break
    
    return matched_symptoms

# Main function to process symptoms
def process_symptoms(symptoms_text):
    """
    Process the raw symptoms text and return structured symptoms
    """
    # Preprocess the input text
    processed_tokens = preprocess_text(symptoms_text)
    
    # Load known symptoms
    known_symptoms = load_symptoms()
    
    # Match with known symptoms
    matched_symptoms = match_symptoms(processed_tokens, known_symptoms)
    
    # If no matches, use the processed tokens as generic symptoms
    if not matched_symptoms:
        # Filter tokens to potentially meaningful ones (longer than 3 chars)
        matched_symptoms = [token for token in processed_tokens if len(token) > 3]
    
    logging.debug(f"Processed symptoms: {matched_symptoms}")
    return matched_symptoms
