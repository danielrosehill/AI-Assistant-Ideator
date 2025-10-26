# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-Assistant-Ideator is a Streamlit web application that generates creative AI assistant concepts and creates system prompts for them using OpenRouter's API (specifically GPT-4 Turbo).

**Key functionality:**
- Generates AI assistant ideas with structured metadata (name, description, target users, use cases, benefits, required capabilities)
- Creates detailed system prompts for generated assistants
- Categorizes ideas (productivity, time management, business, education, health, creative, finance, custom)
- Saves and downloads ideas/prompts (individual or batch ZIP export)
- Stores OpenRouter API key in browser session state

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

The application runs on the default Streamlit port (8501) and opens in the browser automatically.

## Architecture

### Single-File Application Structure

`app.py` is organized as follows:

1. **Configuration & Styling** (lines 11-65): Page config and custom CSS for UI components
2. **Session State Management** (lines 67-77): Maintains ideas, system prompts, and saved items across interactions
3. **API Integration** (lines 79-117): OpenRouter API client using `requests` library
4. **Core Generation Logic**:
   - `generate_idea()` (lines 119-165): Creates AI assistant concepts via structured JSON responses
   - `generate_system_prompt()` (lines 167-212): Generates markdown-formatted system prompts based on assistant specifications
5. **Data Management** (lines 214-241): Save/download functionality for ideas and prompts
6. **UI Components** (lines 243-417): Sidebar controls and main content area

### API Key Management

The application uses **OpenRouter** (not OpenAI directly, despite the openai package being in requirements). API keys are stored in `st.session_state.api_key` (browser cache) and retrieved via `get_api_key()`.

**Important:** The README mentions "OpenAI API key" but the code actually uses OpenRouter's API at `https://openrouter.ai/api/v1/chat/completions` with model `openai/gpt-4-turbo`.

### State Management

Streamlit session state tracks:
- `ideas`: List of all generated ideas
- `system_prompts`: List of generated system prompts
- `current_idea`: Currently displayed idea
- `current_system_prompt`: Currently displayed system prompt
- `saved_items`: Items marked for download
- `api_key`: OpenRouter API key (browser-cached)

### JSON Response Structure

AI assistant ideas follow this schema:
```json
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
```

## Development Notes

- No tests are included in this codebase
- No build process required (interpreted Python/Streamlit)
- Dependencies are minimal: Streamlit, requests, pandas (though pandas is imported but not actively used in the current code)
- The application uses inline CSS styling (lines 20-64) rather than external stylesheets
- File exports use base64 encoding for download links and zipfile for batch exports

## Customization Points

To modify LLM behavior:
- **Model selection**: Line 97 (`"model": "openai/gpt-4-turbo"`)
- **Idea generation prompt**: Lines 121-145 in `generate_idea()`
- **System prompt generation instructions**: Lines 179-196 in `generate_system_prompt()`
- **Category options**: Line 261 in sidebar

## Known Quirks

- The `openai` package is listed in requirements but the code uses `requests` directly to call OpenRouter API
- `pandas` is imported but not used in current implementation
- API key is stored in session state only (lost on browser close unless re-entered)
