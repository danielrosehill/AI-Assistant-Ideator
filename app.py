import streamlit as st
import json
import pandas as pd
import base64
import io
import zipfile
import random
import requests
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="AI Assistant Ideator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
    }
    .feature-box {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
        background-color: #f9f9f9;
    }
    .copy-btn {
        float: right;
    }
    .idea-container {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
    }
    .system-prompt-container {
        border: 1px solid #d1e7dd;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        background-color: #f8f9fa;
    }
    .feature-tag {
        display: inline-block;
        padding: 3px 8px;
        margin: 3px;
        border-radius: 15px;
        font-size: 0.8em;
        background-color: #e9ecef;
    }
    .feature-tag.active {
        background-color: #28a745;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ideas' not in st.session_state:
    st.session_state.ideas = []
if 'system_prompts' not in st.session_state:
    st.session_state.system_prompts = []
if 'current_idea' not in st.session_state:
    st.session_state.current_idea = None
if 'current_system_prompt' not in st.session_state:
    st.session_state.current_system_prompt = None
if 'saved_items' not in st.session_state:
    st.session_state.saved_items = []

# Function to get API key from session state or browser cache
def get_api_key():
    if 'api_key' in st.session_state and st.session_state.api_key:
        return st.session_state.api_key
    return None

# Function to make a request to Open Router API
def open_router_completion(prompt, system_prompt="You are a helpful assistant.", json_response=False):
    api_key = get_api_key()
    if not api_key:
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-4-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }
    
    if json_response:
        payload["response_format"] = {"type": "json_object"}
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error making API request: {str(e)}")
        return None

# Function to generate an AI assistant idea
def generate_idea(category=None):
    prompt = """Generate a creative and detailed idea for an AI assistant. 
    The idea should include:
    1. A clear name and concept
    2. Detailed description of functionality
    3. Target users and use cases
    4. Benefits and unique selling points
    5. Indicate if the assistant would require:
       - Context/RAG capabilities
       - Vision capabilities
       - Tool use capabilities
    
    Format the response as a JSON with the following structure:
    {
        "name": "Assistant Name",
        "description": "Detailed description",
        "target_users": "Description of target users",
        "use_cases": ["Use case 1", "Use case 2", "Use case 3"],
        "benefits": ["Benefit 1", "Benefit 2", "Benefit 3"],
        "features": {
            "context_rag": true/false,
            "vision": true/false,
            "tool_use": true/false
        }
    }
    """
    
    if category and category != "Random":
        prompt += f"\nThe assistant should be focused on the {category} domain."
    
    response = open_router_completion(
        prompt=prompt,
        system_prompt="You are a creative AI assistant designer.",
        json_response=True
    )
    
    if not response:
        st.error("Please enter your Open Router API key")
        return None
    
    try:
        idea_json = json.loads(response["choices"][0]["message"]["content"])
        return idea_json
    except Exception as e:
        st.error(f"Error parsing response: {str(e)}")
        return None

# Function to generate a system prompt for an AI assistant idea
def generate_system_prompt(idea):
    features = []
    if idea["features"]["context_rag"]:
        features.append("context/RAG capabilities")
    if idea["features"]["vision"]:
        features.append("vision capabilities")
    if idea["features"]["tool_use"]:
        features.append("tool use capabilities")
    
    features_text = ", ".join(features) if features else "no special capabilities"
    
    prompt = f"""Create a detailed system prompt for an AI assistant with the following specifications:

    Name: {idea["name"]}
    Description: {idea["description"]}
    Target Users: {idea["target_users"]}
    Use Cases: {", ".join(idea["use_cases"])}
    Benefits: {", ".join(idea["benefits"])}
    Special Features: {features_text}
    
    The system prompt should:
    1. Clearly define the assistant's role and capabilities
    2. Set appropriate tone and communication style
    3. Include specific instructions on how to handle different types of user requests
    4. Establish any limitations or boundaries
    5. Provide guidance on how to leverage the special features mentioned
    
    Format the response as a markdown-formatted system prompt that could be directly used with an LLM.
    """
    
    response = open_router_completion(
        prompt=prompt,
        system_prompt="You are an expert at creating system prompts for AI assistants."
    )
    
    if not response:
        st.error("Please enter your Open Router API key")
        return None
    
    try:
        system_prompt = response["choices"][0]["message"]["content"]
        return system_prompt
    except Exception as e:
        st.error(f"Error parsing response: {str(e)}")
        return None

# Function to save an item (idea or system prompt)
def save_item(item_type, content, name):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    item = {
        "id": f"{item_type}_{timestamp}",
        "type": item_type,
        "content": content,
        "name": name,
        "timestamp": timestamp
    }
    st.session_state.saved_items.append(item)
    return item

# Function to generate a download link for a file
def get_download_link(file_content, file_name, link_text):
    b64 = base64.b64encode(file_content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{file_name}">{link_text}</a>'

# Function to create a zip file with all saved items
def create_zip_file():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for item in st.session_state.saved_items:
            file_name = f"{item['type']}_{item['name'].replace(' ', '_')}_{item['timestamp']}.md"
            zip_file.writestr(file_name, item['content'])
    
    buffer.seek(0)
    return buffer.getvalue()

# Sidebar
with st.sidebar:
    st.title("AI Assistant Ideator")
    st.markdown("Generate creative ideas for AI assistants and system prompts")
    
    # API Key input
    api_key = st.text_input("Enter your Open Router API key", type="password")
    if api_key:
        st.session_state.api_key = api_key
        st.markdown("""
        <div style='background-color: #d1e7dd; padding: 10px; border-radius: 5px;'>
            ✅ API key saved in browser cache
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Category selection
    category_options = ["Random", "Productivity", "Time Management", "Business", "Education", 
                        "Health & Wellness", "Creative", "Personal Finance", "Custom"]
    selected_category = st.selectbox("Select category", category_options)
    
    # Custom category input
    custom_category = None
    if selected_category == "Custom":
        custom_category = st.text_input("Enter custom category")
        if custom_category:
            selected_category = custom_category
    
    # Generate idea button
    if st.button("Generate Idea"):
        with st.spinner("Generating AI assistant idea..."):
            idea = generate_idea(selected_category if selected_category != "Random" else None)
            if idea:
                st.session_state.current_idea = idea
                st.session_state.ideas.append(idea)
                st.session_state.current_system_prompt = None
    
    st.divider()
    
    # Saved items section
    st.subheader("Saved Items")
    if st.session_state.saved_items:
        for i, item in enumerate(st.session_state.saved_items):
            st.markdown(f"**{i+1}. {item['type'].title()}:** {item['name']}")
        
        # Download buttons
        if st.button("Download All (ZIP)"):
            zip_data = create_zip_file()
            b64_zip = base64.b64encode(zip_data).decode()
            href = f'<a href="data:application/zip;base64,{b64_zip}" download="ai_assistant_ideas.zip">Download ZIP File</a>'
            st.markdown(href, unsafe_allow_html=True)
    else:
        st.info("No saved items yet. Save ideas or system prompts to see them here.")

# Main content
st.title("AI Assistant Ideator")

# Next idea button at the top
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Next Idea ➡️"):
        with st.spinner("Generating new AI assistant idea..."):
            idea = generate_idea(selected_category if selected_category != "Random" else None)
            if idea:
                st.session_state.current_idea = idea
                st.session_state.ideas.append(idea)
                st.session_state.current_system_prompt = None

# Display current idea
if st.session_state.current_idea:
    idea = st.session_state.current_idea
    
    with st.container():
        st.markdown(f"<div class='idea-container'>", unsafe_allow_html=True)
        
        # Idea header
        st.subheader(f"💡 {idea['name']}")
        
        # Description
        st.markdown(f"**Description:**\n{idea['description']}")
        
        # Target users and use cases
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Target Users:**\n{idea['target_users']}")
        
        with col2:
            st.markdown("**Use Cases:**")
            for use_case in idea['use_cases']:
                st.markdown(f"- {use_case}")
        
        # Benefits
        st.markdown("**Benefits:**")
        for benefit in idea['benefits']:
            st.markdown(f"- {benefit}")
        
        # Features
        st.markdown("**Required Capabilities:**")
        features = idea['features']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            is_active = features['context_rag']
            st.markdown(
                f"<div class='feature-tag {'active' if is_active else ''}'>"
                f"{'✅' if is_active else '❌'} Context/RAG"
                f"</div>", 
                unsafe_allow_html=True
            )
        
        with col2:
            is_active = features['vision']
            st.markdown(
                f"<div class='feature-tag {'active' if is_active else ''}'>"
                f"{'✅' if is_active else '❌'} Vision"
                f"</div>", 
                unsafe_allow_html=True
            )
        
        with col3:
            is_active = features['tool_use']
            st.markdown(
                f"<div class='feature-tag {'active' if is_active else ''}'>"
                f"{'✅' if is_active else '❌'} Tool Use"
                f"</div>", 
                unsafe_allow_html=True
            )
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate System Prompt"):
                with st.spinner("Generating system prompt..."):
                    system_prompt = generate_system_prompt(idea)
                    if system_prompt:
                        st.session_state.current_system_prompt = system_prompt
        
        with col2:
            if st.button("Save Idea"):
                save_item("idea", json.dumps(idea, indent=2), idea["name"])
                st.success(f"Idea '{idea['name']}' saved!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display current system prompt
    if st.session_state.current_system_prompt:
        system_prompt = st.session_state.current_system_prompt
        
        with st.container():
            st.markdown(f"<div class='system-prompt-container'>", unsafe_allow_html=True)
            
            st.subheader("System Prompt")
            st.markdown(system_prompt)
            
            # Action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Copy System Prompt"):
                    st.code(system_prompt)
            
            with col2:
                if st.button("Save System Prompt"):
                    save_item("system_prompt", system_prompt, idea["name"])
                    st.success(f"System prompt for '{idea['name']}' saved!")
            
            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Click 'Generate Idea' to create an AI assistant concept")

# Footer
st.markdown("---")
st.markdown("AI Assistant Ideator - Generate creative AI assistant ideas and system prompts")
