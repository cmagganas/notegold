from typing import Dict, List, Any
import os
import json
import re
from notegold.src.models.data_models import AIDAContent
from notegold.src.utils.llm_utils import chat_completion
from notegold.src.utils.file_utils import load_json, save_json

def apply_aida_format(ranked_topics_path: str, artifacts_dir: str, outputs_dir: str, top_n: int = 3) -> Dict[str, Any]:
    """
    Apply AIDA format to top-ranked topics.
    
    Args:
        ranked_topics_path: Path to ranked topics JSON
        artifacts_dir: Directory to save artifacts
        outputs_dir: Directory to save outputs
        top_n: Number of top topics to format
        
    Returns:
        Dictionary with AIDA content and output paths
    """
    # Load ranked topics
    ranked_topics = load_json(ranked_topics_path)
    
    # Take top N topics
    top_topics = ranked_topics[:top_n]
    
    aida_contents = []
    output_paths = []
    
    for topic in top_topics:
        # Create prompt for AIDA formatting
        system_message = """
        You are an expert content strategist who specializes in the AIDA framework:
        - Attention: Grab interest with a hook that speaks directly to a pain point
        - Interest: Build credibility with relevant insights and information
        - Desire: Create a vivid picture of the outcome readers want
        - Action: Provide a clear next step
        
        Format your response with clear sections for each AIDA component, followed by a combined full version.
        """
        
        prompt = f"""
        Apply the AIDA framework to this content topic:
        
        Title: {topic["title"]}
        Description: {topic["description"]}
        Pain Point: {topic["pain_point"]}
        Value Proposition: {topic["value_proposition"]}
        
        Create:
        1. Attention: A hook that grabs interest by speaking directly to the pain point
        2. Interest: Build credibility with relevant insights and information
        3. Desire: Create a vivid picture of the outcome readers want
        4. Action: Provide a clear next step
        5. Full Content: Combine all components into a cohesive piece
        
        Format your response with markdown headings for each section.
        """
        
        # Get AIDA content using LLM
        response = chat_completion(prompt, system_message)
        
        # Create AIDAContent object
        aida_content = AIDAContent(
            topic=topic,
            full_content=response
        )
        
        # Try to extract individual AIDA components from the response
        attention_match = re.search(r'#+\s*Attention[:\s]+(.*?)(?=#+\s*Interest|$)', response, re.DOTALL)
        interest_match = re.search(r'#+\s*Interest[:\s]+(.*?)(?=#+\s*Desire|$)', response, re.DOTALL)
        desire_match = re.search(r'#+\s*Desire[:\s]+(.*?)(?=#+\s*Action|$)', response, re.DOTALL)
        action_match = re.search(r'#+\s*Action[:\s]+(.*?)(?=#+\s*Full Content|$)', response, re.DOTALL)
        
        if attention_match:
            aida_content.attention = attention_match.group(1).strip()
        if interest_match:
            aida_content.interest = interest_match.group(1).strip()
        if desire_match:
            aida_content.desire = desire_match.group(1).strip()
        if action_match:
            aida_content.action = action_match.group(1).strip()
        
        # Create clean title for filename
        clean_title = ''.join(c if c.isalnum() else '_' for c in topic["title"])
        
        # Save AIDA content to markdown file in outputs directory
        output_path = os.path.join(outputs_dir, f"aida_{clean_title}.md")
        
        with open(output_path, 'w') as f:
            f.write(f"# AIDA Format: {topic['title']}\n\n")
            f.write("## Attention\n\n")
            f.write(f"{aida_content.attention}\n\n")
            f.write("## Interest\n\n")
            f.write(f"{aida_content.interest}\n\n")
            f.write("## Desire\n\n")
            f.write(f"{aida_content.desire}\n\n")
            f.write("## Action\n\n")
            f.write(f"{aida_content.action}\n\n")
            f.write("## Full Content\n\n")
            f.write(f"{aida_content.full_content}")
        
        aida_contents.append(aida_content.__dict__)
        output_paths.append(output_path)
    
    # Save all AIDA content to JSON file in artifacts directory
    json_output_path = os.path.join(artifacts_dir, "aida_content.json")
    save_json(aida_contents, json_output_path)
    
    return {
        "aida_contents": aida_contents,
        "aida_content_path": json_output_path,
        "output_paths": output_paths
    } 