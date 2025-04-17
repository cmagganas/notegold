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

def setup_meeting_directory(meeting_notes_path: str, meeting_id: Optional[str] = None) -> Dict[str, str]:
    """
    Set up the directory structure for a meeting.
    Returns dict with paths to different directories.
    """
    # If meeting_id not provided, generate one
    if not meeting_id:
        meeting_id = f"meeting_{os.path.basename(meeting_notes_path).split('.')[0]}"
    
    # Create base directory
    base_dir = f"{meeting_id}"
    ensure_dir(base_dir)
    
    # Create subdirectories
    meeting_notes_dir = os.path.join(base_dir, "meeting_notes")
    artifacts_dir = os.path.join(base_dir, "artifacts")
    outputs_dir = os.path.join(base_dir, "outputs")
    metadata_dir = os.path.join(base_dir, "metadata")
    
    ensure_dir(meeting_notes_dir)
    ensure_dir(artifacts_dir)
    ensure_dir(outputs_dir)
    ensure_dir(metadata_dir)
    
    # Copy meeting notes to meeting_notes directory
    notes_filename = os.path.basename(meeting_notes_path)
    new_notes_path = os.path.join(meeting_notes_dir, notes_filename)
    shutil.copy(meeting_notes_path, new_notes_path)
    
    return {
        "base_dir": base_dir,
        "meeting_notes_dir": meeting_notes_dir,
        "meeting_notes_path": new_notes_path,
        "artifacts_dir": artifacts_dir,
        "outputs_dir": outputs_dir,
        "metadata_dir": metadata_dir
    } 