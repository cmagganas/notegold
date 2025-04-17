from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class MeetingMetadata:
    meeting_id: str
    client_name: str = ""
    company_name: str = ""
    industry: str = ""
    pain_points: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)
    extraction_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    meeting_notes_path: str = ""

@dataclass
class TopicIdea:
    title: str
    description: str
    pain_point: str = ""
    value_proposition: str = ""
    audience: str = ""
    content_format: str = "blog"

@dataclass
class RankedTopic(TopicIdea):
    dream_outcome_score: int = 0  # 1-10
    probability_score: int = 0    # 1-10
    time_score: int = 0           # 1-10 (lower is better)
    effort_score: int = 0         # 1-10 (lower is better)
    value_score: float = 0.0      # Calculated
    priority: str = "Medium"      # High, Medium, Low
    
    def calculate_value_score(self):
        """Calculate value score using the Value Equation"""
        # Value = (Dream Outcome × Probability) ÷ (Time × Effort)
        if self.time_score > 0 and self.effort_score > 0:
            self.value_score = (self.dream_outcome_score * self.probability_score) / (self.time_score * self.effort_score)
        return self.value_score

@dataclass
class AIDAContent:
    topic: RankedTopic
    attention: str = ""    # Hook to grab attention
    interest: str = ""     # Build credibility with insights
    desire: str = ""       # Create a vivid picture of the outcome
    action: str = ""       # Clear next step
    full_content: str = "" # Combined content

@dataclass
class SocialMediaPost:
    topic_title: str
    platform: str      # Twitter/X, LinkedIn, etc.
    approach: str      # e.g., "surprising insight", "common mistake", "outcome"
    content: str
    estimated_time: int = 0  # Minutes to create
    
@dataclass
class ProcessingNode:
    """Represents a node in the processing graph."""
    id: str
    name: str
    description: str = ""
    processor_function: str = ""  # Function name to call
    input_artifacts: List[str] = field(default_factory=list)
    output_artifacts: List[str] = field(default_factory=list)
    parameters: Dict[str, any] = field(default_factory=dict)

@dataclass
class ProcessingEdge:
    """Represents an edge connecting nodes in the processing graph."""
    source_node_id: str
    target_node_id: str
    condition: str = ""  # Optional condition to evaluate

@dataclass
class ProcessingGraph:
    """Represents the complete processing workflow."""
    nodes: List[ProcessingNode] = field(default_factory=list)
    edges: List[ProcessingEdge] = field(default_factory=list)
    name: str = "Default Graph"
    description: str = "" 