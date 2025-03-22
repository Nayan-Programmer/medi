import json
import random
import logging
from collections import Counter

def load_disease_data():
    """
    Load disease-symptom mapping data
    """
    try:
        with open('data/symptoms_diseases.json', 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        logging.error("Disease data file not found")
        return {}
    except json.JSONDecodeError:
        logging.error("Invalid JSON in disease data file")
        return {}

def predict_disease(symptoms):
    """
    Predict disease based on symptoms using a simple matching algorithm
    In a real system, this would use a trained ML model
    """
    if not symptoms:
        return "Insufficient information"
    
    # Load disease data
    disease_data = load_disease_data()
    
    if not disease_data:
        return "Unknown condition"
    
    # Calculate matching scores for each disease
    disease_scores = {}
    
    for disease_name, disease_info in disease_data.items():
        disease_symptoms = disease_info.get("symptoms", [])
        
        # Count matching symptoms
        matching_symptoms = [s for s in symptoms if any(ds.lower() in s.lower() or s.lower() in ds.lower() for ds in disease_symptoms)]
        match_score = len(matching_symptoms)
        
        # Adjust score based on percentage of disease's symptoms matched
        if disease_symptoms:
            coverage_score = match_score / len(disease_symptoms)
            # Weight coverage more heavily to avoid diseases with many symptoms always winning
            adjusted_score = match_score + (coverage_score * 2)
            disease_scores[disease_name] = adjusted_score
    
    # Sort diseases by score
    sorted_diseases = sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return highest scoring disease, or "Unknown" if no good matches
    if sorted_diseases and sorted_diseases[0][1] > 0:
        return sorted_diseases[0][0]
    else:
        return "Unknown condition"

def assess_risk_level(disease, symptoms):
    """
    Assess the risk level (low, moderate, high) based on the disease and symptoms
    """
    # Load disease data
    disease_data = load_disease_data()
    
    # If disease is unknown or not in our database, use symptom count for risk assessment
    if disease == "Unknown condition" or disease not in disease_data:
        if len(symptoms) >= 5:
            return "high"
        elif len(symptoms) >= 3:
            return "moderate"
        else:
            return "low"
    
    # Get disease information
    disease_info = disease_data.get(disease, {})
    
    # Get risk factors
    risk_factors = disease_info.get("risk_factors", [])
    
    # Calculate risk based on percentage of disease's symptoms matched
    disease_symptoms = disease_info.get("symptoms", [])
    
    if not disease_symptoms:
        return "moderate"  # Default if no symptom data
    
    # Check how many symptoms match
    matching_symptoms = [s for s in symptoms if any(ds.lower() in s.lower() or s.lower() in ds.lower() for ds in disease_symptoms)]
    symptom_coverage = len(matching_symptoms) / len(disease_symptoms)
    
    # Check for severe symptoms or multiple symptoms indicating high risk
    severe_conditions = {
        "difficulty breathing", "chest pain", "shortness of breath", "severe pain",
        "high fever", "cannot move", "unconscious", "confused", "blurred vision",
        "sudden weakness", "numbness", "slurred speech", "severe headache",
        "blood", "coughing blood", "vomiting blood", "severe bleeding"
    }
    
    severe_count = sum(1 for s in symptoms if any(sc in s.lower() for sc in severe_conditions))
    
    # Determine risk level based on symptom coverage, severe symptoms, and number of symptoms
    if severe_count >= 1 or symptom_coverage >= 0.7 or len(matching_symptoms) >= 5:
        return "high"
    elif symptom_coverage >= 0.4 or len(matching_symptoms) >= 3:
        return "moderate"
    else:
        return "low"
