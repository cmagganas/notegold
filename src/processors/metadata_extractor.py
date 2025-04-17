from typing import Dict, Any
import os
from src.utils.llm_utils import chat_completion, extract_json_from_response
from src.utils.file_utils import save_json
import time
from datetime import datetime

def extract_metadata(meeting_notes_path: str, artifacts_dir: str) -> Dict[str, Any]:
    """
    Extract metadata from meeting notes.
    
    Args:
        meeting_notes_path: Path to the meeting notes file
        artifacts_dir: Directory to save artifacts
        
    Returns:
        Dictionary with metadata and output path
    """
    # Generate unique meeting ID
    meeting_id = f"meeting_{int(time.time())}"
    
    # Load transcript
    with open(meeting_notes_path, 'r') as f:
        transcript = f.read()
    
    # Create prompt for metadata extraction
    system_message = """
    You are an expert AI consultant analyzing meeting notes.
    Extract key metadata from the meeting notes provided.
    Your response should be valid JSON only.
    """
    
    prompt = f"""
    Extract the following metadata from these meeting notes:
    
    1. Meeting title (descriptive title based on content)
    2. Meeting date (if mentioned, otherwise leave empty)
    3. Attendees (names of people in the meeting)
    4. Client name (the organization being consulted)
    5. Primary contact (main client representative)
    6. Project name (if mentioned)
    7. Main topics discussed (list of 3-5 key topics)
    8. Key pain points (list of problems/challenges mentioned)
    9. Requested deliverables (specific outputs requested by client)
    10. Next steps (agreed follow-up actions)
    
    Meeting notes:
    {transcript[:4000]}
    
    Format your response as a JSON object with these keys:
    - meeting_title (string)
    - meeting_date (string, YYYY-MM-DD format or empty)
    - attendees (array of strings)
    - client_name (string)
    - primary_contact (string)
    - project_name (string)
    - main_topics (array of strings)
    - pain_points (array of strings)
    - requested_deliverables (array of strings)
    - next_steps (array of strings)
    """
    
    # Get metadata using LLM
    response = chat_completion(prompt, system_message)
    metadata = extract_json_from_response(response)
    
    # Add additional metadata
    metadata['meeting_id'] = meeting_id
    metadata['processing_date'] = datetime.now().strftime('%Y-%m-%d')
    metadata['meeting_notes_path'] = meeting_notes_path
    
    # Save metadata to JSON file
    output_path = os.path.join(artifacts_dir, f"{meeting_id}_metadata.json")
    save_json(metadata, output_path)
    
    return {
        "metadata": metadata,
        "metadata_path": output_path
    } 