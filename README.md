# AI-Assistant-Ideator

A Streamlit application that generates ideas for AI assistants and creates system prompts for them.

## Features

- Generate random AI assistant ideas
- Filter ideas by category (productivity, time management, business, etc.)
- Create system prompts for generated ideas
- Save and download ideas and system prompts
- Stores OpenAI API key in browser cache for convenience

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Enter your OpenAI API key (it will be stored in your browser's local storage)
2. Select a category for AI assistant ideas or choose "Random"
3. Click "Generate Idea" to create a new AI assistant concept
4. Review the generated idea and its features
5. Click "Generate System Prompt" to create a system prompt for the assistant
6. Use the "Save" button to store ideas or prompts for later download
7. Click "Next Idea" to generate a new assistant concept

## Requirements

- Python 3.7+
- Streamlit
- OpenAI API key
