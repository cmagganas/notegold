#!/usr/bin/env python3

import os
import sys
import argparse
import time
from datetime import datetime

from src.utils.file_utils import (
    setup_meeting_directory,
    save_json,
    load_text
)
from src.utils.graph_utils import (
    load_graph,
    create_default_graph,
    execute_graph
)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process meeting notes")
    parser.add_argument('meeting_notes_path', help='Path to the meeting notes file')
    parser.add_argument('--meeting-id', help='Meeting ID (defaults to filename if not provided)')
    parser.add_argument('--graph-path', help='Path to the processing graph')
    parser.add_argument('--output-dir', help='Output directory', default='.')
    
    return parser.parse_args()

def process_meeting_notes(meeting_notes_path, meeting_id=None, graph_path=None, output_dir='.'):
    """
    Process meeting notes through the content flywheel.
    
    Args:
        meeting_notes_path: Path to the meeting notes file
        meeting_id: Meeting ID (defaults to filename if not provided)
        graph_path: Path to the processing graph (defaults to built-in graph)
        output_dir: Output directory (defaults to current directory)
    
    Returns:
        Dictionary with processing results
    """
    # Setup directory structure
    directories = setup_meeting_directory(meeting_notes_path, meeting_id, output_dir)
    
    # Log the start of processing
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{start_time}] Starting to process meeting notes: {meeting_notes_path}")
    
    # Load the meeting notes
    meeting_notes = load_text(directories["meeting_notes_path"])
    
    # Load or create the processing graph
    if graph_path:
        graph = load_graph(graph_path)
    else:
        graph = create_default_graph()
    
    # Prepare initial context
    context = {
        "meeting_notes_path": directories["meeting_notes_path"],
        "artifacts_dir": directories["artifacts_dir"],
        "outputs_dir": directories["outputs_dir"],
        "metadata_dir": directories["metadata_dir"],
        "logs_dir": directories["logs_dir"],
        "meeting_id": directories["meeting_id"]
    }
    
    # Execute the graph
    try:
        result_context = execute_graph(graph, context)
        
        # Add metadata about the run
        metadata = {
            "meeting_id": directories["meeting_id"],
            "processed_at": datetime.now().isoformat(),
            "status": "success",
            "graph_name": graph.name
        }
        
        # Save processing metadata
        metadata_path = os.path.join(directories["metadata_dir"], "processing_metadata.json")
        save_json(metadata, metadata_path)
        
        # Print success message with completion time
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execution_time = time.time() - time.mktime(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").timetuple())
        print(f"[{end_time}] ✅ Meeting notes processed successfully in {execution_time:.2f} seconds")
        
        # If we have a processing summary, print it
        if "processing_summary" in result_context:
            print("\nProcessing Summary:")
            print(result_context["processing_summary"])
        
        return {
            "status": "success",
            "meeting_id": directories["meeting_id"],
            "artifacts": result_context
        }
        
    except Exception as e:
        # Log the error
        error_metadata = {
            "meeting_id": directories["meeting_id"],
            "processed_at": datetime.now().isoformat(),
            "status": "error",
            "error": str(e),
            "graph_name": graph.name
        }
        
        # Save error metadata
        error_path = os.path.join(directories["metadata_dir"], "processing_error.json")
        save_json(error_metadata, error_path)
        
        # Print error message
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{end_time}] ❌ Error processing meeting notes: {str(e)}")
        
        # Re-raise the exception
        raise e

def interactive_start():
    """Interactive version of the command to walk users through the process."""
    import os
    
    # Get meeting notes path
    meeting_notes_path = input("Path to meeting notes file: ").strip()
    if not os.path.exists(meeting_notes_path):
        print(f"Error: File not found: {meeting_notes_path}")
        return 1
    
    # Optional meeting ID
    meeting_id = input("Meeting ID (optional, press Enter to use default): ").strip()
    if not meeting_id:
        meeting_id = None
    
    # Output directory (with default)
    output_dir = input("Output directory (optional, press Enter for current directory): ").strip()
    if not output_dir:
        output_dir = "."
    
    # Call the main processing function
    try:
        return process_meeting_notes(
            meeting_notes_path=meeting_notes_path,
            meeting_id=meeting_id,
            graph_path=None,  # Use default graph
            output_dir=output_dir
        )
    except Exception as e:
        print(f"Error processing meeting notes: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Process meeting notes")
    
    # Add a subparser for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # "process" command - original functionality
    process_parser = subparsers.add_parser("process", help="Process meeting notes with all options")
    process_parser.add_argument("meeting_notes_path", help="Path to the meeting notes file")
    process_parser.add_argument("--meeting-id", help="Meeting ID (defaults to filename if not provided)")
    process_parser.add_argument("--graph-path", help="Path to the processing graph")
    process_parser.add_argument("--output-dir", default=".", help="Output directory")
    
    # "start" command - simplified interactive version
    subparsers.add_parser("start", help="Interactive guided setup")
    
    args = parser.parse_args()
    
    if args.command == "start":
        return interactive_start()
    elif args.command == "process":
        try:
            return process_meeting_notes(
                meeting_notes_path=args.meeting_notes_path,
                meeting_id=args.meeting_id,
                graph_path=args.graph_path,
                output_dir=args.output_dir
            )
        except Exception as e:
            print(f"Error processing meeting notes: {e}")
            return 1
    else:
        # Default to showing help if no command specified
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main()) 