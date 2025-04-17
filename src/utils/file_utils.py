import os
import json
import shutil
from typing import Any, Dict, Optional

def ensure_dir(directory: str) -> str:
    """Ensure directory exists, create if it doesn't."""
    os.makedirs(directory, exist_ok=True)
    return directory

def save_json(data: Any, filepath: str) -> str:
    """Save data as JSON to specified filepath."""
    directory = os.path.dirname(filepath)
    ensure_dir(directory)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    return filepath

def load_json(filepath: str) -> Dict:
    """Load JSON data from filepath."""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_text(text: str, filepath: str) -> str:
    """Save text to specified filepath."""
    directory = os.path.dirname(filepath)
    ensure_dir(directory)
    
    with open(filepath, 'w') as f:
        f.write(text)
    
    return filepath

def load_text(filepath: str) -> str:
    """Load text from filepath."""
    with open(filepath, 'r') as f:
        return f.read()

def setup_meeting_directory(meeting_notes_path: str, meeting_id: Optional[str] = None, output_dir: str = '.') -> Dict[str, str]:
    """
    Set up the directory structure for a meeting.
    
    Args:
        meeting_notes_path: Path to the meeting notes file
        meeting_id: Optional custom meeting ID (derived from filename if not provided)
        output_dir: Base output directory (defaults to current directory)
    
    Returns:
        Dict with paths to different directories and meeting ID
    """
    # If meeting_id not provided, generate one
    if not meeting_id:
        # Extract the base filename without extension
        notes_filename = os.path.basename(meeting_notes_path)
        base_name = os.path.splitext(notes_filename)[0]
        
        # Only prefix with "meeting_" if not already prefixed
        if not base_name.startswith("meeting_"):
            meeting_id = f"meeting_{base_name}"
        else:
            meeting_id = base_name
    
    # Create meetings directory within output_dir
    meetings_dir = os.path.join(output_dir, "meetings")
    ensure_dir(meetings_dir)
    
    # Create meeting-specific directory
    meeting_dir = os.path.join(meetings_dir, meeting_id)
    ensure_dir(meeting_dir)
    
    # Create subdirectories
    notes_dir = os.path.join(meeting_dir, "notes")
    artifacts_dir = os.path.join(meeting_dir, "artifacts")
    outputs_dir = os.path.join(meeting_dir, "outputs")
    metadata_dir = os.path.join(meeting_dir, "metadata")
    logs_dir = os.path.join(meeting_dir, "logs")
    
    ensure_dir(notes_dir)
    ensure_dir(artifacts_dir)
    ensure_dir(outputs_dir)
    ensure_dir(metadata_dir)
    ensure_dir(logs_dir)
    
    # Copy meeting notes to notes directory
    notes_filename = os.path.basename(meeting_notes_path)
    new_notes_path = os.path.join(notes_dir, notes_filename)
    
    # Only copy if source and destination are different
    if os.path.abspath(meeting_notes_path) != os.path.abspath(new_notes_path):
        shutil.copy(meeting_notes_path, new_notes_path)
    
    return {
        "meeting_dir": meeting_dir,
        "notes_dir": notes_dir,
        "meeting_notes_path": new_notes_path,
        "artifacts_dir": artifacts_dir,
        "outputs_dir": outputs_dir,
        "metadata_dir": metadata_dir,
        "logs_dir": logs_dir,
        "meeting_id": meeting_id
    } 