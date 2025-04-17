import os
import json
import time
from datetime import datetime
from typing import Dict, Any

class ProcessLogger:
    """
    Logger for tracking the processing steps and artifacts in the content flywheel.
    """
    
    def __init__(self, logs_dir: str):
        """
        Initialize the logger with the directory to store logs.
        
        Args:
            logs_dir: Directory to store log files
        """
        self.logs_dir = logs_dir
        self.process_log_path = os.path.join(logs_dir, "process_log.json")
        self.log_entries = []
        self.current_edge = None
        self.start_time = time.time()
        
        # Initialize log file
        self._save_log()
    
    def log_edge_start(self, source_node: str, target_node: str) -> None:
        """
        Log the start of processing an edge between nodes.
        
        Args:
            source_node: Source node ID
            target_node: Target node ID
        """
        self.current_edge = {
            "source": source_node,
            "target": target_node,
            "status": "processing",
            "start_time": datetime.now().isoformat(),
            "artifacts": [],
            "execution_time_ms": 0
        }
        
        print(f"Processing: {source_node} → {target_node}...")
        self._save_log()
    
    def log_edge_complete(self, execution_time_ms: int, status: str = "complete") -> None:
        """
        Log the completion of processing the current edge.
        
        Args:
            execution_time_ms: Execution time in milliseconds
            status: Status of the edge (complete, error, etc.)
        """
        if self.current_edge:
            self.current_edge["status"] = status
            self.current_edge["execution_time_ms"] = execution_time_ms
            self.log_entries.append(self.current_edge)
            
            source = self.current_edge["source"]
            target = self.current_edge["target"]
            
            print(f"✓ Completed: {source} → {target} ({execution_time_ms}ms)")
            self._save_log()
            self.current_edge = None
    
    def log_artifact(self, artifact_path: str, artifact_type: str) -> None:
        """
        Log the creation of an artifact.
        
        Args:
            artifact_path: Path to the artifact
            artifact_type: Type of artifact (metadata, topics, etc.)
        """
        if self.current_edge:
            artifact = {
                "path": artifact_path,
                "type": artifact_type,
                "created_at": datetime.now().isoformat()
            }
            self.current_edge["artifacts"].append(artifact)
            
            print(f"  Output: {artifact_type} → {os.path.basename(artifact_path)}")
            self._save_log()
    
    def log_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the processing.
        
        Returns:
            Dictionary with summary information
        """
        end_time = time.time()
        total_time_ms = int((end_time - self.start_time) * 1000)
        
        summary = {
            "total_edges": len(self.log_entries),
            "total_artifacts": sum(len(entry["artifacts"]) for entry in self.log_entries),
            "total_time_ms": total_time_ms,
            "completed_at": datetime.now().isoformat()
        }
        
        # Save summary to summary.json
        summary_path = os.path.join(self.logs_dir, "summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Create markdown summary
        markdown_path = os.path.join(self.logs_dir, "summary.md")
        with open(markdown_path, 'w') as f:
            f.write("# Content Flywheel Processing Summary\n\n")
            f.write(f"**Completed at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total processing time:** {total_time_ms/1000:.2f} seconds\n")
            f.write(f"**Total processing steps:** {len(self.log_entries)}\n")
            f.write(f"**Total artifacts:** {summary['total_artifacts']}\n\n")
            
            f.write("## Processing Steps\n\n")
            for i, entry in enumerate(self.log_entries):
                f.write(f"### {i+1}. {entry['source']} → {entry['target']}\n\n")
                f.write(f"- **Status:** {entry['status']}\n")
                f.write(f"- **Execution time:** {entry['execution_time_ms']/1000:.2f} seconds\n")
                
                if entry["artifacts"]:
                    f.write("- **Artifacts:**\n")
                    for artifact in entry["artifacts"]:
                        f.write(f"  - {artifact['type']}: `{artifact['path']}`\n")
                
                f.write("\n")
        
        return summary
    
    def _save_log(self) -> None:
        """Save the current log entries to the log file."""
        log_data = {
            "log_entries": self.log_entries,
            "current_edge": self.current_edge,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.process_log_path, 'w') as f:
            json.dump(log_data, f, indent=2) 