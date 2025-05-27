import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from utils.preprocessing import preprocess_text

class RoBERTaNewsClassifier:
    def __init__(self, model_name="cardiffnlp/twitter-roberta-base-sentiment-latest"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.load_model()
    
    @st.cache_resource
    def load_model(_self):
        
        try:
            _self.tokenizer = AutoTokenizer.from_pretrained(_self.model_name)
            _self.model = AutoModelForSequenceClassification.from_pretrained(_self.model_name)
            _self.model.to(_self.device)
            _self.model.eval()
            return True
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            return False
    
    def predict(self, text):
        """Predict if news is fake or real"""
        if not self.model or not self.tokenizer:
            return None, 0.0
        
        if not text or not isinstance(text, str):
            return "unknown", 0.0
        
        try:
            processed_text = preprocess_text(text)
            
            if not processed_text or not processed_text.strip():
                return "unknown", 0.0
            
            inputs = self.tokenizer(
                processed_text, 
                return_tensors="pt", 
                truncation=True, 
                padding=True, 
                max_length=512
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
            # Get prediction and confidence
            predicted_class = torch.argmax(predictions, dim=-1).item()
            confidence = torch.max(predictions).item()
            
            
            if predicted_class == 2:  
                label = "real"
            elif predicted_class == 0:  
                label = "fake"
            else:  # Neutral
                label = "uncertain"
                confidence = confidence * 0.7  
            
            return label, confidence
            
        except Exception as e:
            st.error(f"Error in prediction: {str(e)}")
            return "unknown", 0.0
    
    def get_model_info(self):
        """Get model information"""
        return {
            "model_name": self.model_name,
            "device": str(self.device),
            "loaded": self.model is not None
        }

@st.cache_resource
def get_classifier():
    return RoBERTaNewsClassifier()
