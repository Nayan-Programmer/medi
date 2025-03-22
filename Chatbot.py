import re
import random
import json
import logging

# Load medical information for chatbot responses
def load_medical_info():
    try:
        with open('data/symptoms_diseases.json', 'r') as file:
            symptoms_diseases = json.load(file)
        
        with open('data/medical_recommendations.json', 'r') as file:
            recommendations = json.load(file)
        
        # Extract all symptoms from all diseases
        all_symptoms = []
        for disease, info in symptoms_diseases.items():
            all_symptoms.extend(info.get('symptoms', []))
        
        # Remove duplicates
        all_symptoms = list(set(all_symptoms))
        
        return {
            "symptoms": all_symptoms,
            "diseases": symptoms_diseases,
            "recommendations": recommendations
        }
    except Exception as e:
        logging.error(f"Error loading medical info: {str(e)}")
        return {"symptoms": [], "diseases": {}, "recommendations": {}}

# Define response patterns
GREETING_PATTERNS = [
    r'hi', r'hello', r'hey', r'greetings', r'howdy'
]

SYMPTOM_PATTERNS = [
    r'symptom', r'i feel', r'i have', r'suffering from', r'experiencing'
]

DISEASE_PATTERNS = [
    r'disease', r'condition', r'diagnosis', r'what is', r'tell me about',
    r'information on', r'details about'
]

TREATMENT_PATTERNS = [
    r'treatment', r'medicine', r'medication', r'cure', r'remedy', r'how to treat',
    r'what should i do'
]

FAREWELL_PATTERNS = [
    r'bye', r'goodbye', r'see you', r'farewell', r'thanks', r'thank you'
]

# Responses for each category
GREETING_RESPONSES = [
    "Hello! I'm your medical assistant. How can I help you today?",
    "Hi there! I can provide basic medical information. What would you like to know?",
    "Hello! I'm here to help with basic health queries. What's on your mind?"
]

SYMPTOM_RESPONSES = [
    "I see you're experiencing {}. You might want to try our symptom diagnosis tool for a more detailed assessment.",
    "I understand you're dealing with {}. For a proper diagnosis, please use our main diagnosis tool.",
    "I notice you mentioned {}. Consider using our full diagnosis system for a comprehensive analysis."
]

DISEASE_RESPONSES = [
    "Regarding {}, it's a condition characterized by the following symptoms: {}. Please consult a healthcare professional for proper diagnosis.",
    "{} typically presents with symptoms such as {}. Always seek medical advice for accurate information.",
    "{} is a health condition with symptoms including {}. Remember, I can only provide general information, not diagnose."
]

TREATMENT_RESPONSES = [
    "For {}, general recommendations include: {}. Always follow your doctor's advice.",
    "Treatment for {} may include: {}. Please consult with a healthcare professional for personalized advice.",
    "Some approaches for {} include: {}. Make sure to discuss with your doctor before trying any treatment."
]

FAREWELL_RESPONSES = [
    "Goodbye! Take care of your health!",
    "Thank you for chatting. Stay healthy!",
    "Feel better soon! Remember to consult healthcare professionals for medical advice."
]

DEFAULT_RESPONSES = [
    "I'm sorry, I don't have enough information to help with that. Please try using more specific health-related terms.",
    "I don't understand that query. Could you rephrase it with more medical details?",
    "That's outside my knowledge area. For better assistance, please use our main diagnosis tool or consult a healthcare professional."
]

# Main function to get chatbot response
def get_chatbot_response(user_message):
    """
    Process user message and return appropriate chatbot response
    """
    if not user_message:
        return "Please type a message to start a conversation."
    
    # Convert to lowercase for easier matching
    message = user_message.lower()
    
    # Check for greetings
    if any(re.search(pattern, message) for pattern in GREETING_PATTERNS):
        return random.choice(GREETING_RESPONSES)
    
    # Check for farewells
    if any(re.search(pattern, message) for pattern in FAREWELL_PATTERNS):
        return random.choice(FAREWELL_RESPONSES)
    
    # Load medical info
    medical_info = load_medical_info()
    
    # Check for disease information request
    for pattern in DISEASE_PATTERNS:
        if re.search(pattern, message):
            # Try to identify which disease they're asking about
            for disease_name in medical_info["diseases"].keys():
                if disease_name.lower() in message:
                    disease_info = medical_info["diseases"][disease_name]
                    symptoms_list = ", ".join(disease_info.get("symptoms", [])[:5])
                    
                    return random.choice(DISEASE_RESPONSES).format(
                        disease_name, 
                        symptoms_list or "various symptoms"
                    )
            
            return "If you'd like to learn about a specific condition, please mention its name or use our diagnosis tool."
    
    # Check for treatment advice
    for pattern in TREATMENT_PATTERNS:
        if re.search(pattern, message):
            # Try to identify which disease they're asking about treatment for
            for disease_name, recommendations in medical_info["recommendations"].items():
                if disease_name.lower() in message:
                    treatment = recommendations.get("general", "seeking professional medical advice")
                    
                    return random.choice(TREATMENT_RESPONSES).format(
                        disease_name,
                        treatment
                    )
            
            return "For treatment information, please specify the condition you're asking about or consult a healthcare professional."
    
    # Check for symptom information
    for pattern in SYMPTOM_PATTERNS:
        if re.search(pattern, message):
            # Try to extract mentioned symptoms
            mentioned_symptoms = []
            for symptom in medical_info["symptoms"]:
                if symptom.lower() in message:
                    mentioned_symptoms.append(symptom)
            
            if mentioned_symptoms:
                symptoms_text = ", ".join(mentioned_symptoms)
                return random.choice(SYMPTOM_RESPONSES).format(symptoms_text)
            
            return "Could you describe your symptoms in more detail? Or try using our diagnosis tool for a comprehensive assessment."
    
    # Default response if no pattern matched
    return random.choice(DEFAULT_RESPONSES)
