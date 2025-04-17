#!/usr/bin/env python3

import os
import sys
import argparse
from typing import Dict, Any, Optional

from .utils.file_utils import setup_meeting_directory, load_text
from .utils.graph_utils import create_default_graph, save_graph, load_graph, execute_graph

def process_meeting_notes(meeting_notes_path: str, meeting_id: Optional[str] = None, graph_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Process meeting notes through the content flywheel.
    
    Args:
        meeting_notes_path: Path to the meeting notes file
        meeting_id: Optional meeting ID (generated if not provided)
        graph_path: Optional path to a custom processing graph
        
    Returns:
        Results from the processing pipeline
    """
    # Setup meeting directory
    dir_paths = setup_meeting_directory(meeting_notes_path, meeting_id)
    
    # Create initial context
    context = {
        "transcript_path": dir_paths["meeting_notes_path"],
        "artifacts_dir": dir_paths["artifacts_dir"],
        "outputs_dir": dir_paths["outputs_dir"],
        "metadata_dir": dir_paths["metadata_dir"]
    }
    
    # Load or create processing graph
    if graph_path and os.path.exists(graph_path):
        graph = load_graph(graph_path)
    else:
        graph = create_default_graph()
        # Save default graph to metadata directory
        graph_path = os.path.join(dir_paths["metadata_dir"], "processing_graph.json")
        save_graph(graph, graph_path)
    
    # Execute the processing graph
    results = execute_graph(graph, context)
    
    return results

def main():
    """Main entry point for the notegold CLI."""
    parser = argparse.ArgumentParser(description="Notegold: Meeting notes to content flywheel")
    
    parser.add_argument("meeting_notes", help="Path to meeting notes file")
    parser.add_argument("--meeting-id", help="Custom meeting ID (optional)")
    parser.add_argument("--graph", help="Path to custom processing graph (optional)")
    
    args = parser.parse_args()
    
    # Check if meeting notes file exists
    if not os.path.exists(args.meeting_notes):
        print(f"Error: Meeting notes file not found: {args.meeting_notes}")
        sys.exit(1)
    
    # Process the meeting notes
    try:
        results = process_meeting_notes(
            meeting_notes_path=args.meeting_notes,
            meeting_id=args.meeting_id,
            graph_path=args.graph
        )
        
        # Print summary of results
        print("\nContent Flywheel Processing Complete!")
        print("===================================")
        
        # Show paths to generated content
        if "social_content_paths" in results:
            print("\nSocial Media Content:")
            for path in results["social_content_paths"]:
                print(f"- {path}")
        
        base_dir = os.path.dirname(results.get("metadata_path", ""))
        if base_dir:
            print(f"\nAll artifacts available in: {base_dir}")
            
    except Exception as e:
        print(f"Error processing meeting notes: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 