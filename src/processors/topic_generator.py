from typing import Dict, List, Any
import os
import json
from notegold.src.models.data_models import TopicIdea
from notegold.src.utils.llm_utils import chat_completion, extract_json_from_response
from notegold.src.utils.file_utils import load_json, save_json

def generate_topics(metadata_path: str, artifacts_dir: str, transcript_path: str = None) -> Dict[str, Any]:
    """
    Generate topic ideas from meeting metadata.
    
    Args:
        metadata_path: Path to meeting metadata JSON
        artifacts_dir: Directory to save artifacts
        transcript_path: Optional path to transcript (if additional context needed)
        
    Returns:
        Dictionary with topics list and output path
    """
    # Load metadata
    metadata = load_json(metadata_path)
    
    # Load transcript if provided
    transcript_text = ""
    if transcript_path:
        with open(transcript_path, 'r') as f:
            transcript_text = f.read()
    
    # Create prompt for topic generation
    system_message = """
    You are an expert content strategist for AI consultants.
    Generate potential content topics based on meeting data that would be valuable to the client and similar audiences.
    Provide each topic in JSON format.
    """
    
    prompt = f"""
    Based on this meeting data, generate 5-7 potential content topics that would be valuable for the client and similar audiences.
    
    Meeting metadata:
    {json.dumps(metadata, indent=2)}
    
    {"Transcript excerpt:\n" + transcript_text[:2000] + "..." if transcript_text else ""}
    
    For each topic, provide:
    1. A compelling title using the AIDA framework principles
    2. A brief description of what this content would cover
    3. The specific pain point it addresses
    4. The value proposition (what the audience will gain)
    5. The target audience
    6. Recommended content format (blog post, video script, tweet thread, etc.)
    
    Format your response as a JSON array of topics, with each topic having these fields:
    - title (string)
    - description (string)
    - pain_point (string)
    - value_proposition (string)
    - audience (string)
    - content_format (string)
    """
    
    # Get topics using LLM
    response = chat_completion(prompt, system_message)
    topics_data = extract_json_from_response(response)
    
    # Handle case where response might not be an array
    if not isinstance(topics_data, list):
        if "topics" in topics_data and isinstance(topics_data["topics"], list):
            topics_data = topics_data["topics"]
        else:
            topics_data = []
    
    # Create TopicIdea objects
    topics = []
    for item in topics_data:
        topic = TopicIdea(
            title=item.get("title", "Untitled Topic"),
            description=item.get("description", ""),
            pain_point=item.get("pain_point", ""),
            value_proposition=item.get("value_proposition", ""),
            audience=item.get("audience", ""),
            content_format=item.get("content_format", "blog")
        )
        topics.append(topic.__dict__)
    
    # Save topics to JSON file
    output_path = os.path.join(artifacts_dir, "topic_ideas.json")
    save_json(topics, output_path)
    
    return {
        "topics": topics,
        "topics_path": output_path
    } 