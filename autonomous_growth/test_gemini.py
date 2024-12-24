import google.generativeai as genai
import streamlit as st
import toml

# Load secrets
with open('.streamlit/secrets.toml', 'r', encoding='utf-8') as f:
    secrets = toml.load(f)

# Configure API key
genai.configure(api_key=secrets['ai_models']['gemini_api_key'])

def test_gemini_connection():
    try:
        # Initialize Gemini Pro model
        model = genai.GenerativeModel('gemini-pro')
        
        # Test with a simple prompt
        response = model.generate_content("Say 'Hello! Connection test successful!' if you can read this.")
        
        print("API Connection Test Results:")
        print("----------------------------")
        print("[SUCCESS] Successfully connected to Gemini API")
        print("[RESPONSE]", response.text)
        return True
        
    except Exception as e:
        print("[ERROR] Error connecting to Gemini API:")
        print(e)
        return False

if __name__ == "__main__":
    test_gemini_connection()
