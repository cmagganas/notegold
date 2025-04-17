from typing import Dict, List, Any
import os
import json
import re
from src.models.data_models import TopicIdea
from src.utils.llm_utils import chat_completion, extract_json_from_response
from src.utils.file_utils import save_json

def extract_topics_from_response(text: str) -> List[Dict[str, Any]]:
    """
    Extract topic data from text when JSON parsing fails.
    
    Args:
        text: Text response from LLM
        
    Returns:
        List of topic dictionaries
    """
    topics = []
    
    # Try to find title patterns like "Topic 1: Title" or "1. Title" or "- Title"
    title_pattern = r'(?:Topic\s+\d+:|^\d+\.|\-)\s*([^\n]+)'
    titles = re.findall(title_pattern, text, re.MULTILINE)
    
    # If no titles found, look for "Title:" or "# Title"
    if not titles:
        title_pattern = r'(?:Title:|#)\s*([^\n]+)'
        titles = re.findall(title_pattern, text, re.MULTILINE)
    
    for title in titles:
        # Create a simple topic with the title
        topic = {
            "title": title.strip(),
            "description": "Extracted from text response",
            "pain_point": "",
            "value_proposition": "",
            "audience": "General audience",
            "content_format": "blog"
        }
        
        # Try to extract description
        desc_match = re.search(f'{re.escape(title)}.*?(?:Description:|:)\s*([^\n]+)', text, re.DOTALL)
        if desc_match:
            topic["description"] = desc_match.group(1).strip()
        
        # Try to extract pain point
        pain_match = re.search(r'Pain\s+Point.*?:\s*([^\n]+)', text, re.DOTALL)
        if pain_match:
            topic["pain_point"] = pain_match.group(1).strip()
        
        # Try to extract value proposition
        value_match = re.search(r'Value\s+Proposition.*?:\s*([^\n]+)', text, re.DOTALL)
        if value_match:
            topic["value_proposition"] = value_match.group(1).strip()
        
        # Try to extract audience
        audience_match = re.search(r'(?:Target\s+)?Audience.*?:\s*([^\n]+)', text, re.DOTALL)
        if audience_match:
            topic["audience"] = audience_match.group(1).strip()
        
        # Try to extract content format
        format_match = re.search(r'(?:Content\s+)?Format.*?:\s*([^\n]+)', text, re.DOTALL)
        if format_match:
            topic["content_format"] = format_match.group(1).strip()
        
        topics.append(topic)
    
    # If we still couldn't find any topics, create a single generic one
    if not topics:
        topics.append({
            "title": "Generated Topic",
            "description": "Topic extracted from response",
            "pain_point": "",
            "value_proposition": "",
            "audience": "General audience",
            "content_format": "blog"
        })
    
    return topics

def generate_topics(metadata_path: str, artifacts_dir: str, meeting_notes_path: str = None) -> Dict[str, Any]:
    """
    Generate potential content topics based on meeting data.
    
    Args:
        metadata_path: Path to meeting metadata JSON
        artifacts_dir: Directory to save artifacts
        meeting_notes_path: Optional path to meeting notes for additional context
        
    Returns:
        Dictionary with list of topics and output path
    """
    # Load meeting metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Optionally load transcript for additional context
    transcript_text = ""
    if meeting_notes_path:
        with open(meeting_notes_path, 'r') as f:
            transcript_text = f.read()
    
    # Create prompt for topic generation
    system_message = """
    You are an expert content strategist who specializes in B2B content marketing.
    Based on meeting data, suggest relevant content topics that address the client's needs.
    
    For each topic, include:
    1. Title (clear, compelling headline)
    2. Description (1-2 sentence summary)
    3. Pain point (specific problem it addresses)
    4. Value proposition (how it helps the audience)
    5. Target audience (who would benefit most)
    6. Recommended content format (blog, whitepaper, case study, video, etc.)
    
    Format your response as a JSON array with these fields for each topic.
    """
    
    # Format metadata into structured prompt
    prompt = f"""
    Generate content topic ideas based on this meeting data:
    
    Client: {metadata.get('client_name', '')}
    Industry: {metadata.get('industry', '')}
    Pain Points: {', '.join(metadata.get('pain_points', []))}
    Goals: {', '.join(metadata.get('goals', []))}
    
    For each topic, provide:
    - title: A clear, compelling headline
    - description: 1-2 sentence summary
    - pain_point: Specific problem it addresses
    - value_proposition: How it helps the audience
    - audience: Who would benefit most
    - content_format: Recommended format (blog, whitepaper, case study, video, etc.)
    
    Format your response as a JSON array of topic objects.
    
    Additional context from meeting notes:
    {transcript_text[:2000] if transcript_text else "No additional context provided."}
    """
    
    # Get topic ideas using LLM
    response = chat_completion(prompt, system_message)
    
    try:
        # Try to parse as JSON
        topics_data = extract_json_from_response(response)
        
        # Ensure it's a list
        if not isinstance(topics_data, list):
            # If not a list but has a topics key that is a list
            if isinstance(topics_data, dict) and 'topics' in topics_data and isinstance(topics_data['topics'], list):
                topics_data = topics_data['topics']
            else:
                # Fallback to extraction
                topics_data = extract_topics_from_response(response)
    except:
        # Fallback to extraction
        topics_data = extract_topics_from_response(response)
    
    # Create Topic objects
    topics = [TopicIdea(**topic) for topic in topics_data]
    
    # Save topics to JSON file
    output_path = os.path.join(artifacts_dir, "topic_ideas.json")
    save_json([topic.__dict__ for topic in topics], output_path)
    
    return {
        "topics": [topic.__dict__ for topic in topics],
        "topics_path": output_path
    } 