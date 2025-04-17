def create_default_graph():
    """
    Creates the default processing graph for transforming meeting transcript to content assets
    """
    from src.models.graph_models import ProcessingNode, ProcessingGraph
    
    # Define nodes
    metadata_node = ProcessingNode(
        id="metadata_extractor",
        processor="metadata_extractor",
        input_artifacts={
            "meeting_notes_path": "$INPUT.meeting_notes_path",
            "artifacts_dir": "$CONFIG.artifacts_dir"
        },
        output_artifacts={
            "metadata": "$.metadata",
            "metadata_path": "$.metadata_path"
        }
    )
    
    topic_node = ProcessingNode(
        id="topic_generator",
        processor="topic_generator",
        input_artifacts={
            "metadata_path": "$NODES.metadata_extractor.metadata_path",
            "meeting_notes_path": "$INPUT.meeting_notes_path",
            "artifacts_dir": "$CONFIG.artifacts_dir"
        },
        output_artifacts={
            "topics": "$.topics",
            "topics_path": "$.topics_path"
        }
    )
    
    topic_ranking_node = ProcessingNode(
        id="topic_ranker",
        processor="topic_ranker",
        input_artifacts={
            "topics_path": "$NODES.topic_generator.topics_path",
            "metadata_path": "$NODES.metadata_extractor.metadata_path",
            "artifacts_dir": "$CONFIG.artifacts_dir"
        },
        output_artifacts={
            "ranked_topics": "$.ranked_topics",
            "ranked_topics_path": "$.ranked_topics_path"
        }
    )
    
    aida_node = ProcessingNode(
        id="aida_formatter",
        processor="aida_formatter",
        input_artifacts={
            "ranked_topics_path": "$NODES.topic_ranker.ranked_topics_path",
            "metadata_path": "$NODES.metadata_extractor.metadata_path",
            "meeting_notes_path": "$INPUT.meeting_notes_path",
            "artifacts_dir": "$CONFIG.artifacts_dir"
        },
        output_artifacts={
            "aida_content": "$.aida_content",
            "aida_content_path": "$.aida_content_path"
        }
    )
    
    social_node = ProcessingNode(
        id="social_content_creator",
        processor="social_content_creator",
        input_artifacts={
            "aida_content_path": "$NODES.aida_formatter.aida_content_path",
            "metadata_path": "$NODES.metadata_extractor.metadata_path",
            "artifacts_dir": "$CONFIG.artifacts_dir"
        },
        output_artifacts={
            "social_content": "$.social_content",
            "social_content_path": "$.social_content_path"
        }
    )
    
    # Create graph with nodes
    graph = ProcessingGraph(
        nodes=[
            metadata_node,
            topic_node,
            topic_ranking_node,
            aida_node,
            social_node
        ]
    )
    
    return graph 