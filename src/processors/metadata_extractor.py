from typing import Dict, List, Any
import os
import json
from notegold.src.models.data_models import MeetingMetadata
from notegold.src.utils.llm_utils import chat_completion, extract_json_from_response
from notegold.src.utils.file_utils import save_json

def extract_metadata(transcript_path: str, artifacts_dir: str) -> Dict[str, Any]:
    """
    Extract metadata from meeting transcript.
    
    Args:
        transcript_path: Path to meeting transcript file
        artifacts_dir: Directory to save artifacts
        
    Returns:
        Dictionary with metadata and output path
    """
    # Read transcript
    with open(transcript_path, 'r') as f:
        transcript = f.read()
    
    # Generate meeting ID from filename
    meeting_id = os.path.basename(transcript_path).split('.')[0]
    
    # Create prompt for metadata extraction
    system_message = """
    You are an expert at analyzing meeting transcripts and extracting key metadata.
    Extract structured information from the meeting transcript in JSON format.
    """
    
    prompt = f"""
    Analyze this meeting transcript and extract the following metadata in JSON format:
    
    1. Client name and company
    2. Industry
    3. Main pain points discussed (list)
    4. Goals or desired outcomes (list)
    5. Key questions asked by the client (list)
    
    Format your response as a JSON object with these fields:
    - client_name (string)
    - company_name (string)
    - industry (string)
    - pain_points (array of strings)
    - goals (array of strings)
    - questions (array of strings)
    
    Transcript:
    {transcript}
    """
    
    # Get metadata using LLM
    response = chat_completion(prompt, system_message)
    extracted_data = extract_json_from_response(response)
    
    # Create MeetingMetadata object
    metadata = MeetingMetadata(
        meeting_id=meeting_id,
        client_name=extracted_data.get("client_name", ""),
        company_name=extracted_data.get("company_name", ""),
        industry=extracted_data.get("industry", ""),
        pain_points=extracted_data.get("pain_points", []),
        goals=extracted_data.get("goals", []),
        questions=extracted_data.get("questions", []),
        transcript_path=transcript_path
    )
    
    # Save metadata to JSON file
    output_path = os.path.join(artifacts_dir, "meeting_metadata.json")
    save_json(metadata.__dict__, output_path)
    
    return {
        "metadata": metadata.__dict__,
        "metadata_path": output_path
    } 