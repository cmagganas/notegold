import os
import json
import re
from typing import Dict, List, Any, Optional

def initialize_openai_client():
    """Initialize OpenAI client with API key from environment."""
    try:
        import openai
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = api_key
        return openai
    except ImportError:
        raise ImportError("OpenAI package not installed. Install with: pip install openai")

def chat_completion(
    prompt: str, 
    system_message: str = "",
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> str:
    """
    Get completion from OpenAI chat model.
    
    Args:
        prompt: The user prompt
        system_message: Optional system message
        model: Model to use (default: gpt-4)
        temperature: Temperature (0.0 to 1.0)
        max_tokens: Maximum tokens in response
        
    Returns:
        Generated text
    """
    openai = initialize_openai_client()
    
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    
    messages.append({"role": "user", "content": prompt})
    
    params = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }
    
    if max_tokens:
        params["max_tokens"] = max_tokens
    
    response = openai.chat.completions.create(**params)
    return response.choices[0].message.content

def extract_json_from_response(response: str) -> Dict:
    """
    Extract and parse JSON from a text response.
    Handles cases where JSON might be embedded in markdown or other text.
    """
    # Try to find JSON block in markdown
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
    
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to parse the entire response as JSON
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # If all else fails, return an error object
    return {"error": "Could not extract JSON from response", "raw_response": response}

def get_llm_provider():
    """
    Get configured LLM provider based on environment variables.
    Allows for future expansion to other providers.
    """
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        return {
            "name": "openai",
            "chat_completion": chat_completion,
            "default_model": os.environ.get("OPENAI_MODEL", "gpt-4")
        }
    elif provider == "anthropic":
        # Placeholder for future implementation
        raise NotImplementedError("Anthropic provider not yet implemented")
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}") 