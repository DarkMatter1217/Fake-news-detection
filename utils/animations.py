import streamlit as st
import time

def show_spyglass_loader(status_text, duration=None):
    """Display animated spyglass loader with optional duration"""
    loader_html = f"""
    <div class="spyglass-loader">
        <div class="spyglass-animation">
            <div class="spyglass-lens"></div>
            <div class="spyglass-handle"></div>
            <div class="spyglass-grip"></div>
            <div class="search-waves">
                <div class="search-wave"></div>
                <div class="search-wave"></div>
                <div class="search-wave"></div>
            </div>
        </div>
    </div>
    <div class="loading-text">{status_text}</div>
    """
    
    placeholder = st.empty()
    placeholder.markdown(loader_html, unsafe_allow_html=True)
    
    if duration:
        time.sleep(duration)
        placeholder.empty()
    
    return placeholder

def show_pulse_loader(text="Loading..."):
    """Simple pulsing text loader"""
    return st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <div class="pulse-loader">{text}</div>
    </div>
    """, unsafe_allow_html=True)

def show_typing_animation(text, delay=0.05):
    """Typing animation effect"""
    placeholder = st.empty()
    displayed_text = ""
    
    for char in text:
        displayed_text += char
        placeholder.markdown(f"""
        <div class="typing-animation">
            {displayed_text}<span class="cursor">|</span>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(delay)
    
    return placeholder
