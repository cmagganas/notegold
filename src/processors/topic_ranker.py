from typing import Dict, List, Any
import os
import json
from src.models.data_models import RankedTopic
from src.utils.llm_utils import chat_completion, extract_json_from_response
from src.utils.file_utils import load_json, save_json

def rank_topics(topics_path: str, artifacts_dir: str) -> Dict[str, Any]:
    """
    Rank topics using the Value Equation.
    
    Args:
        topics_path: Path to topic ideas JSON
        artifacts_dir: Directory to save artifacts
        
    Returns:
        Dictionary with ranked topics and output path
    """
    # Load topics
    topics = load_json(topics_path)
    
    # Create prompt for topic ranking
    system_message = """
    You are an expert content strategist who evaluates content ideas using the Value Equation:
    Value = (Dream Outcome × Probability of Success) ÷ (Time × Effort)
    
    For each topic, score each component on a scale of 1-10:
    - Dream Outcome: How compelling is the potential outcome for the audience?
    - Probability of Success: How likely is the content to deliver on its promise?
    - Time: How much time would it take to create this content? (Lower is better)
    - Effort: How complex would it be to create this content? (Lower is better)
    """
    
    prompt = f"""
    Evaluate each of these content topics using the Value Equation: 
    Value = (Dream Outcome × Probability of Success) ÷ (Time × Effort)
    
    Topics:
    {json.dumps(topics, indent=2)}
    
    For each topic, score these components on a scale of 1-10:
    1. Dream Outcome: How compelling is the potential outcome for the audience?
    2. Probability of Success: How likely is the content to deliver on its promise?
    3. Time: How much time would it take to create this content? (Lower is better)
    4. Effort: How complex would it be to create this content? (Lower is better)
    
    Calculate the Value Score using the equation, then categorize each topic as High, Medium, or Low priority.
    
    Format your response as a JSON array with the original topic data plus these additional fields:
    - dream_outcome_score (integer 1-10)
    - probability_score (integer 1-10)
    - time_score (integer 1-10)
    - effort_score (integer 1-10)
    - value_score (float)
    - priority (string: "High", "Medium", or "Low")
    """
    
    # Get ranked topics using LLM
    response = chat_completion(prompt, system_message)
    ranked_data = extract_json_from_response(response)
    
    # Handle case where response might not be an array
    if not isinstance(ranked_data, list):
        if "topics" in ranked_data and isinstance(ranked_data["topics"], list):
            ranked_data = ranked_data["topics"]
        else:
            ranked_data = []
    
    # Create RankedTopic objects
    ranked_topics = []
    for item in ranked_data:
        topic = RankedTopic(
            title=item.get("title", "Untitled Topic"),
            description=item.get("description", ""),
            pain_point=item.get("pain_point", ""),
            value_proposition=item.get("value_proposition", ""),
            audience=item.get("audience", ""),
            content_format=item.get("content_format", "blog"),
            dream_outcome_score=item.get("dream_outcome_score", 5),
            probability_score=item.get("probability_score", 5),
            time_score=item.get("time_score", 5),
            effort_score=item.get("effort_score", 5),
            value_score=item.get("value_score", 0.0),
            priority=item.get("priority", "Medium")
        )
        # Calculate value score if not provided
        if not topic.value_score:
            topic.calculate_value_score()
        
        ranked_topics.append(topic.__dict__)
    
    # Sort topics by value score in descending order
    ranked_topics.sort(key=lambda x: x["value_score"], reverse=True)
    
    # Save ranked topics to JSON file
    output_path = os.path.join(artifacts_dir, "ranked_topics.json")
    save_json(ranked_topics, output_path)
    
    return {
        "ranked_topics": ranked_topics,
        "ranked_topics_path": output_path
    } 