from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app, db
from models import Diagnosis
from utils.nlp_processor import process_symptoms
from utils.ml_model import predict_disease, assess_risk_level
from utils.chatbot import get_chatbot_response
from utils.sms_notification import send_sms_notification, generate_notification_message
import json
import os
import logging
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/diagnose', methods=['GET', 'POST'])
def diagnose():
    if request.method == 'POST':
        # Get the symptoms from form
        symptoms_text = request.form.get('symptoms', '')
        
        if not symptoms_text:
            flash('Please enter your symptoms', 'warning')
            return redirect(url_for('diagnose'))
        
        try:
            # Process symptoms using NLP
            processed_symptoms = process_symptoms(symptoms_text)
            
            if not processed_symptoms:
                flash('No recognizable symptoms detected. Please provide more details about your symptoms.', 'warning')
                return redirect(url_for('diagnose'))
            
            # Predict disease and risk level
            predicted_disease = predict_disease(processed_symptoms)
            risk_level = assess_risk_level(predicted_disease, processed_symptoms)
            
            # Generate recommendations
            with open('data/medical_recommendations.json', 'r') as file:
                recommendations_data = json.load(file)
            
            recommendation = "Please consult a healthcare professional for proper diagnosis."
            
            if predicted_disease in recommendations_data:
                recommendation = recommendations_data[predicted_disease]['general']
                if risk_level == 'high':
                    recommendation += " " + recommendations_data[predicted_disease].get('high_risk', 
                                    "Seek immediate medical attention.")
                elif risk_level == 'moderate':
                    recommendation += " " + recommendations_data[predicted_disease].get('moderate_risk', 
                                    "Schedule an appointment with your doctor soon.")
            
            # Store diagnosis in session for results page
            session['diagnosis'] = {
                'symptoms': symptoms_text,
                'processed_symptoms': processed_symptoms,
                'disease': predicted_disease,
                'risk_level': risk_level,
                'recommendation': recommendation,
                'timestamp': datetime.now().strftime('%B %d, %Y at %H:%M')
            }
            
            # Save to database if user is logged in
            # This is just preparation for future login functionality
            diagnosis = Diagnosis(
                symptoms=symptoms_text,
                predicted_disease=predicted_disease,
                risk_level=risk_level,
                recommendation=recommendation
            )
            db.session.add(diagnosis)
            db.session.commit()
            
            return redirect(url_for('diagnosis_result'))
        
        except Exception as e:
            logging.error(f"Error during diagnosis: {str(e)}")
            flash('An error occurred during diagnosis. Please try again.', 'danger')
            return redirect(url_for('diagnose'))
    
    return render_template('index.html')

@app.route('/diagnosis-result')
def diagnosis_result():
    diagnosis = session.get('diagnosis')
    if not diagnosis:
        flash('No diagnosis information found. Please enter your symptoms first.', 'warning')
        return redirect(url_for('diagnose'))
    
    return render_template('diagnosis.html', diagnosis=diagnosis)

@app.route('/sms-notification')
def sms_notification_page():
    diagnosis = session.get('diagnosis')
    if not diagnosis:
        flash('No diagnosis information found. Please enter your symptoms first.', 'warning')
        return redirect(url_for('diagnose'))
    
    # Check if Twilio credentials are available
    from utils.sms_notification import are_twilio_credentials_available
    twilio_available = are_twilio_credentials_available()
    
    return render_template('sms_notification.html', diagnosis=diagnosis, twilio_available=twilio_available)

@app.route('/send-sms-notification', methods=['POST'])
def send_sms_notification_route():
    diagnosis = session.get('diagnosis')
    if not diagnosis:
        flash('No diagnosis information found. Please enter your symptoms first.', 'warning')
        return redirect(url_for('diagnose'))
    
    phone_number = request.form.get('phone_number', '')
    consent = request.form.get('consent') == 'on'
    
    if not phone_number:
        flash('Please enter a valid phone number.', 'warning')
        return redirect(url_for('sms_notification_page'))
    
    if not consent:
        flash('You must consent to receive SMS notifications.', 'warning')
        return redirect(url_for('sms_notification_page'))
    
    # Format phone number with + prefix
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    # Check if Twilio credentials are available
    from utils.sms_notification import are_twilio_credentials_available
    if not are_twilio_credentials_available():
        flash('SMS notifications are currently unavailable. Twilio API credentials are required.', 'warning')
        return redirect(url_for('diagnosis_result'))
    
    # Generate and send message
    message = generate_notification_message(diagnosis)
    success, error_msg = send_sms_notification(phone_number, message)
    
    if success:
        flash('SMS notification sent successfully!', 'success')
    else:
        if "not found in environment variables" in error_msg:
            flash('SMS notifications are currently unavailable. Please try again later or contact support.', 'danger')
        else:
            flash(f'Failed to send SMS notification: {error_msg}', 'danger')
    
    return redirect(url_for('diagnosis_result'))

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Please provide a message'})
    
    response = get_chatbot_response(user_message)
    return jsonify({'response': response})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
