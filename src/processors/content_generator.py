from typing import Dict, List, Any
import os
import json
from src.models.data_models import SocialMediaPost
from src.utils.llm_utils import chat_completion, extract_json_from_response
from src.utils.file_utils import load_json, save_json

def create_social_content(aida_content_path: str, artifacts_dir: str, outputs_dir: str) -> Dict[str, Any]:
    """
    Create social media content variations based on AIDA content.
    
    Args:
        aida_content_path: Path to AIDA content JSON
        artifacts_dir: Directory to save artifacts
        outputs_dir: Directory to save final outputs
        
    Returns:
        Dictionary with social content and output paths
    """
    # Load AIDA content
    aida_contents = load_json(aida_content_path)
    
    all_social_posts = []
    output_paths = []
    
    for content in aida_contents:
        topic_title = content.get("topic", {}).get("title", "Untitled Topic")
        
        # Create prompt for social content variations
        system_message = """
        You are a social media content expert who creates engaging variations to test content ideas.
        For each platform, create multiple approaches to see which resonates best with the audience.
        """
        
        prompt = f"""
        Create 3 different versions of social media posts for this topic:
        
        Topic: {topic_title}
        
        AIDA Content:
        {json.dumps(content, indent=2)}
        
        For each platform (Twitter/X, LinkedIn), create 3 variations:
        
        1. Variation 1: Focus on a surprising insight or statistic
        2. Variation 2: Focus on a common mistake or misconception
        3. Variation 3: Focus on the transformative outcome
        
        Format your response as a JSON array with these fields:
        - platform (string: "Twitter" or "LinkedIn")
        - approach (string: "surprising insight", "common mistake", or "transformative outcome")  
        - content (string: the actual post content)
        - estimated_time (integer: minutes to create this type of content)
        """
        
        # Get social content using LLM
        response = chat_completion(prompt, system_message)
        social_posts_data = extract_json_from_response(response)
        
        # Handle case where response might not be an array
        if not isinstance(social_posts_data, list):
            if "posts" in social_posts_data and isinstance(social_posts_data["posts"], list):
                social_posts_data = social_posts_data["posts"]
            else:
                social_posts_data = []
        
        # Create SocialMediaPost objects
        social_posts = []
        for item in social_posts_data:
            post = SocialMediaPost(
                topic_title=topic_title,
                platform=item.get("platform", ""),
                approach=item.get("approach", ""),
                content=item.get("content", ""),
                estimated_time=item.get("estimated_time", 15)
            )
            social_posts.append(post.__dict__)
        
        # Create clean title for filename
        clean_title = ''.join(c if c.isalnum() else '_' for c in topic_title)
        
        # Save social posts to markdown file
        output_path = os.path.join(outputs_dir, f"social_posts_{clean_title}.md")
        
        with open(output_path, 'w') as f:
            f.write(f"# Social Media Content: {topic_title}\n\n")
            
            # Group by platform
            platforms = set(post["platform"] for post in social_posts)
            
            for platform in platforms:
                f.write(f"## {platform}\n\n")
                platform_posts = [p for p in social_posts if p["platform"] == platform]
                
                for post in platform_posts:
                    f.write(f"### Approach: {post['approach']}\n\n")
                    f.write(f"{post['content']}\n\n")
                    f.write(f"*Estimated creation time: {post['estimated_time']} minutes*\n\n")
                    f.write("---\n\n")
        
        all_social_posts.extend(social_posts)
        output_paths.append(output_path)
    
    # Save all social posts to JSON file
    json_output_path = os.path.join(artifacts_dir, "social_posts.json")
    save_json(all_social_posts, json_output_path)
    
    # Generate a summary report
    summary_path = os.path.join(outputs_dir, "content_summary.md")
    
    with open(summary_path, 'w') as f:
        f.write("# Content Flywheel Summary\n\n")
        
        f.write("## Topics Generated\n\n")
        for content in aida_contents:
            topic = content.get("topic", {})
            f.write(f"- **{topic.get('title', 'Untitled')}** (Priority: {topic.get('priority', 'Unknown')})\n")
            f.write(f"  - Value Score: {topic.get('value_score', 0):.2f}\n")
            f.write(f"  - Format: {topic.get('content_format', 'Unknown')}\n\n")
        
        f.write("## Social Media Content\n\n")
        platforms = set(post["platform"] for post in all_social_posts)
        
        for platform in platforms:
            platform_posts = [p for p in all_social_posts if p["platform"] == platform]
            f.write(f"### {platform}\n\n")
            f.write(f"- **Posts Created:** {len(platform_posts)}\n")
            if platform_posts:
                total_time = sum(p.get("estimated_time", 0) for p in platform_posts)
                f.write(f"- **Estimated Creation Time:** {total_time} minutes\n\n")
        
        f.write("\n## Next Steps\n\n")
        f.write("1. Review the social media content and select the most promising variations\n")
        f.write("2. Create and schedule the selected posts\n")
        f.write("3. Monitor engagement and identify which approaches resonate best\n")
        f.write("4. Develop full-length content for the highest-value topics\n")
    
    output_paths.append(summary_path)
    
    return {
        "social_posts": all_social_posts,
        "social_content_paths": output_paths,
        "summary_path": summary_path
    } 