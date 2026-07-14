import logging
from typing import Dict, Any, List
from services.cloudant_service import CloudantService

logger = logging.getLogger("AnalyticsService")

class AnalyticsService:
    """
    AnalyticsService computes aggregated statistics and performance trends 
    over the user's interview history.
    """
    
    def __init__(self, db_service: CloudantService) -> None:
        self.db = db_service

    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Query all interviews for a user and calculate performance metrics:
        - Averages, minimums, maximums
        - Progress trends over time (list of scores/dates)
        - Weakest/strongest skills/topics
        - Completion rates
        """
        try:
            logger.info(f"Computing interview analytics for user '{user_id}'...")
            
            # Fetch all interviews
            query = {"selector": {"user_id": user_id}}
            interviews = await self.db.query_documents("interviews", query)
            
            if not interviews:
                # Return empty state structure
                return {
                    "total_interviews": 0,
                    "completed_interviews": 0,
                    "completion_rate": 0.0,
                    "average_score": 0.0,
                    "highest_score": 0.0,
                    "lowest_score": 0.0,
                    "questions_attempted": 0,
                    "strongest_skills": [],
                    "weakest_skills": [],
                    "missed_topics": [],
                    "progress_trend": []
                }

            completed_interviews = [i for i in interviews if i.get("status") == "COMPLETED"]
            total_count = len(interviews)
            completed_count = len(completed_interviews)
            completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0.0

            # Calculate question attempts
            total_questions_attempted = sum(len(i.get("answers", [])) for i in interviews)

            # Scores list for averages/trends
            overall_scores = [i.get("overall_score", 0.0) for i in completed_interviews]
            
            avg_score = sum(overall_scores) / completed_count if completed_count > 0 else 0.0
            highest_score = max(overall_scores) if overall_scores else 0.0
            lowest_score = min(overall_scores) if overall_scores else 0.0

            # Aggregating strengths, weaknesses, and missed topics
            strength_topics: Dict[str, int] = {}
            weakness_topics: Dict[str, int] = {}
            missed_topics_freq: Dict[str, int] = {}

            for interview in completed_interviews:
                summary = interview.get("summary", {})
                if not summary:
                    continue
                
                # aggregate frequently missed topics
                for topic in summary.get("frequently_missed_topics", []):
                    missed_topics_freq[topic] = missed_topics_freq.get(topic, 0) + 1

                # aggregate from individual questions evaluations
                evals = interview.get("evaluations", [])
                for ev in evals:
                    # Collect recommended learning topics as weak areas
                    for topic in ev.get("recommended_learning_topics", []):
                        weakness_topics[topic] = weakness_topics.get(topic, 0) + 1
                    # Collect missing concepts
                    for concept in ev.get("missing_concepts", []):
                        missed_topics_freq[concept] = missed_topics_freq.get(concept, 0) + 1
                    # Collect strongest dimensions from per-question scores
                    scores = ev.get("scores", {})
                    if scores:
                        for dim, val in scores.items():
                            dim_label = dim.replace("_", " ").title()
                            score_val = int(val) if isinstance(val, (int, float)) else 0
                            if score_val >= 7:
                                strength_topics[dim_label] = strength_topics.get(dim_label, 0) + 1

            # Sort skills by frequency
            sorted_missed = sorted(missed_topics_freq.items(), key=lambda x: x[1], reverse=True)
            sorted_weak = sorted(weakness_topics.items(), key=lambda x: x[1], reverse=True)
            sorted_strong = sorted(strength_topics.items(), key=lambda x: x[1], reverse=True)

            # Build progress timeline trend
            # Format: list of {"date": "ISO date", "score": float, "role": "Software Developer"}
            progress_trend = []
            # Sort interviews by started time to draw chronological line charts
            chronological_interviews = sorted(completed_interviews, key=lambda x: x.get("started_time", ""))
            for i in chronological_interviews:
                progress_trend.append({
                    "date": i.get("started_time", "")[:10], # Extract YYYY-MM-DD
                    "score": round(i.get("overall_score", 0.0), 2),
                    "role": i.get("role", "Unknown"),
                    "type": i.get("interview_type", "Mixed")
                })

            analytics_result = {
                "total_interviews": total_count,
                "completed_interviews": completed_count,
                "completion_rate": round(completion_rate, 2),
                "average_score": round(avg_score, 2),
                "highest_score": round(highest_score, 2),
                "lowest_score": round(lowest_score, 2),
                "questions_attempted": total_questions_attempted,
                "strongest_skills": [t[0] for t in sorted_strong[:5]],
                "weakest_skills": [t[0] for t in sorted_weak[:5]],
                "missed_topics": [t[0] for t in sorted_missed[:5]],
                "progress_trend": progress_trend
            }

            logger.info("Analytics computed successfully.")
            return analytics_result
        except Exception as e:
            logger.error(f"Error computing user analytics: {str(e)}", exc_info=True)
            raise e
