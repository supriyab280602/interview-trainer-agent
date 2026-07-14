from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class QuestionEvaluation(BaseModel):
    """
    Sub-model for evaluation details of a single answer.
    """
    overall_score: float
    scores: Dict[str, int]
    strengths: str
    weaknesses: str
    missing_concepts: List[str]
    improvement_tips: str
    alternative_better_answer: str
    ideal_model_answer: str
    recommended_learning_topics: List[str]
    confidence_feedback: str
    interviewers_remarks: str

class InterviewSummary(BaseModel):
    """
    Sub-model for the final interview summary report.
    """
    overall_score: float
    scores: Dict[str, float]
    strength_analysis: str
    weakness_analysis: str
    frequently_missed_topics: List[str]
    recommended_study_plan: str
    readiness_level: str
    final_ai_recommendation: str

class Interview(BaseModel):
    """
    Pydantic database representation of an Interview session.
    """
    id: str = Field(..., alias="_id")
    user_id: str
    profile_name: Optional[str] = None
    resume_id: Optional[str] = None
    role: str
    interview_type: str
    difficulty: str
    length: int = 5

    started_time: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_time: Optional[str] = None
    questions: List[str] = Field(default_factory=list)
    answers: List[str] = Field(default_factory=list)
    evaluations: List[QuestionEvaluation] = Field(default_factory=list)
    overall_score: float = 0.0
    summary: Optional[InterviewSummary] = None
    status: str = "IN_PROGRESS" # IN_PROGRESS, COMPLETED
