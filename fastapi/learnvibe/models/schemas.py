from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Question(BaseModel):
    id: int
    text: str
    options: List[str]
    correct_answer: int
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    skill_name: Optional[str] = None
    topic_name: Optional[str] = None
    category: Optional[str] = None
    explanation: Optional[str] = None

class CareerLevel(BaseModel):
    name: str
    description: str
    min_score: int
    max_score: int

class GoalRequest(BaseModel):
    goal: str = Field(..., description="Career goal or target role")
    session_id: Optional[str] = None

class GoalResponse(BaseModel):
    goal: str
    custom_levels: List[str]
    questions: List[Question]
    total_questions: int
    points_per_question: float
    session_id: str

class AnswerRequest(BaseModel):
    goal: str
    answers: List[int]
    questions: List[Question]
    session_id: str

class AssessmentResult(BaseModel):
    score: float = Field(..., ge=0, le=100)
    correct_answers: int
    total_questions: int
    assigned_level: str
    feedback: str
    detailed_feedback: Optional[Dict[str, Any]] = None
    improvement_areas: List[str] = []

class AnswerResponse(AssessmentResult):
    session_id: str

class Prerequisite(BaseModel):
    name: str
    description: str
    importance: str  # "high", "medium", "low"
    estimated_time: str  # e.g., "2-4 weeks"
    resources: List[str] = []

class SkillNode(BaseModel):
    name: str
    description: str
    level: str  # "beginner", "intermediate", "advanced"
    prerequisites: List[str] = []
    children: List['SkillNode'] = []
    resources: List[str] = []
    estimated_duration: str = ""

class Roadmap(BaseModel):
    career_goal: str
    levels: List[CareerLevel]
    skill_tree: SkillNode
    prerequisites: List[Prerequisite]
    timeline_estimate: str