import json
import os
from typing import Dict, List, Any, Callable, Optional
import importlib
from ..models.data_models import ProcessingGraph, ProcessingNode, ProcessingEdge

def load_graph(graph_path: str) -> ProcessingGraph:
    """
    Load a processing graph from a JSON file.
    
    Args:
        graph_path: Path to the graph JSON file
        
    Returns:
        ProcessingGraph object
    """
    with open(graph_path, 'r') as f:
        graph_data = json.load(f)
    
    # Convert dictionary to ProcessingGraph object
    nodes = [ProcessingNode(**node_data) for node_data in graph_data.get("nodes", [])]
    edges = [ProcessingEdge(**edge_data) for edge_data in graph_data.get("edges", [])]
    
    return ProcessingGraph(
        nodes=nodes,
        edges=edges,
        name=graph_data.get("name", "Default Graph"),
        description=graph_data.get("description", "")
    )

def save_graph(graph: ProcessingGraph, output_path: str) -> str:
    """
    Save a processing graph to a JSON file.
    
    Args:
        graph: ProcessingGraph object
        output_path: Path to save the graph JSON
        
    Returns:
        Path to the saved file
    """
    # Convert ProcessingGraph to dictionary
    graph_dict = {
        "name": graph.name,
        "description": graph.description,
        "nodes": [node.__dict__ for node in graph.nodes],
        "edges": [edge.__dict__ for edge in graph.edges]
    }
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump(graph_dict, f, indent=2)
    
    return output_path

def create_default_graph() -> ProcessingGraph:
    """
    Create the default processing graph for the content flywheel.
    
    Returns:
        ProcessingGraph object
    """
    # Define nodes
    nodes = [
        ProcessingNode(
            id="extract_metadata",
            name="Extract Meeting Metadata",
            description="Extract metadata from meeting transcript",
            processor_function="processors.metadata_extractor.extract_metadata",
            input_artifacts=["transcript_path"],
            output_artifacts=["metadata_path"],
            parameters={}
        ),
        ProcessingNode(
            id="generate_topics",
            name="Generate Topic Ideas",
            description="Generate topic ideas from meeting metadata",
            processor_function="processors.topic_generator.generate_topics",
            input_artifacts=["metadata_path", "transcript_path"],
            output_artifacts=["topics_path"],
            parameters={}
        ),
        ProcessingNode(
            id="rank_topics",
            name="Rank Topics by Potential",
            description="Rank topics using the Value Equation",
            processor_function="processors.topic_ranker.rank_topics",
            input_artifacts=["topics_path"],
            output_artifacts=["ranked_topics_path"],
            parameters={}
        ),
        ProcessingNode(
            id="apply_aida",
            name="Apply AIDA Format",
            description="Apply AIDA format to top-ranked topics",
            processor_function="processors.aida_formatter.apply_aida_format",
            input_artifacts=["ranked_topics_path"],
            output_artifacts=["aida_content_path"],
            parameters={"top_n": 3}
        ),
        ProcessingNode(
            id="create_social",
            name="Create Social Media Content",
            description="Create social media content variations",
            processor_function="processors.content_generator.create_social_content",
            input_artifacts=["aida_content_path"],
            output_artifacts=["social_content_paths"],
            parameters={}
        )
    ]
    
    # Define edges
    edges = [
        ProcessingEdge(
            source_node_id="extract_metadata",
            target_node_id="generate_topics"
        ),
        ProcessingEdge(
            source_node_id="generate_topics",
            target_node_id="rank_topics"
        ),
        ProcessingEdge(
            source_node_id="rank_topics",
            target_node_id="apply_aida"
        ),
        ProcessingEdge(
            source_node_id="apply_aida",
            target_node_id="create_social"
        )
    ]
    
    return ProcessingGraph(
        nodes=nodes,
        edges=edges,
        name="Content Flywheel",
        description="Transform meeting transcripts into valuable content assets"
    )

def import_processor_function(function_path: str) -> Callable:
    """
    Dynamically import a processor function from its path.
    
    Args:
        function_path: Path to the function (e.g., "processors.metadata_extractor.extract_metadata")
        
    Returns:
        Callable function
    """
    module_path, function_name = function_path.rsplit('.', 1)
    module = importlib.import_module(f"src.{module_path}")
    return getattr(module, function_name)

def execute_node(node: ProcessingNode, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a processing node with the given context.
    
    Args:
        node: ProcessingNode to execute
        context: Dictionary with context variables
        
    Returns:
        Node execution result
    """
    # Import the processor function
    processor_func = import_processor_function(node.processor_function)
    
    # Prepare function arguments
    args = {}
    
    # Add input artifacts
    for artifact_name in node.input_artifacts:
        if artifact_name in context:
            args[artifact_name.replace("_path", "")] = context[artifact_name]
    
    # Add parameters
    args.update(node.parameters)
    
    # Execute the function
    return processor_func(**args)

def execute_graph(graph: ProcessingGraph, initial_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a processing graph with the given initial context.
    
    Args:
        graph: ProcessingGraph to execute
        initial_context: Dictionary with initial context variables
        
    Returns:
        Final context after execution
    """
    context = initial_context.copy()
    executed_nodes = set()
    
    # Keep track of node dependencies
    node_dependencies = {node.id: [] for node in graph.nodes}
    for edge in graph.edges:
        node_dependencies[edge.target_node_id].append(edge.source_node_id)
    
    # Execute nodes in topological order
    while len(executed_nodes) < len(graph.nodes):
        executed_node_this_round = False
        
        for node in graph.nodes:
            # Skip already executed nodes
            if node.id in executed_nodes:
                continue
            
            # Check if all dependencies have been executed
            if all(dep in executed_nodes for dep in node_dependencies[node.id]):
                # Execute the node
                result = execute_node(node, context)
                
                # Update context with the results
                context.update(result)
                
                # Mark as executed
                executed_nodes.add(node.id)
                executed_node_this_round = True
        
        # If no nodes were executed in this round, we have a dependency cycle
        if not executed_node_this_round and len(executed_nodes) < len(graph.nodes):
            unexecuted = [node.id for node in graph.nodes if node.id not in executed_nodes]
            raise ValueError(f"Dependency cycle detected in graph. Unexecuted nodes: {unexecuted}")
    
    return context 