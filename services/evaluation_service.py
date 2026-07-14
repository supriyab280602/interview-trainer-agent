import logging
import json
import re
from typing import Dict, Any, Optional, List
from services.granite_service import GraniteService
from services.rag_service import RAGService
from prompts.evaluation_prompt import EVALUATION_PROMPT
from models.interview import QuestionEvaluation

logger = logging.getLogger("EvaluationService")

class EvaluationService:
    """
    EvaluationService handles scoring candidate answers by first retrieving relevant
    rubrics and expected concepts from the knowledge base using the RAG service,
    and then generating structured grading using IBM Granite.
    """
    
    def __init__(self, RAG_service: RAGService, granite_service: GraniteService) -> None:
        self.rag = RAG_service
        self.granite = granite_service

    async def evaluate_answer(self, question: str, answer: str, category: str, domain: str) -> Optional[Dict[str, Any]]:
        """
        Grades a single candidate response.
        
        Args:
            question (str): The interview question asked.
            answer (str): The candidate's text response.
            category (str): Category (e.g. Technical, Behavioral, HR, General).
            domain (str): Subject domain (e.g. Software Engineering, AI/ML, Cloud Computing).
            
        Returns:
            Optional[Dict[str, Any]]: The parsed Granite JSON response mapping to QuestionEvaluation.
        """
        try:
            logger.info(f"Starting answer evaluation for {category} question in {domain}...")
            
            # 1. Retrieve RAG context (Top K rubrics, STAR guides, or technical concepts)
            # Create a rich query combining the question and domain
            query = f"{category} rubric {domain} : {question}"
            retrieved_context = self.rag.retrieve_context(
                query=query,
                collection_name="kb_questions",
                n_results=2,
                filters={"category": category} if category in ["HR", "Technical", "Behavioral"] else None
            )
            
            if not retrieved_context or retrieved_context == "No relevant context found.":
                # Fallback to general grading expectations
                retrieved_context = (
                    "Standard grading expectations:\n"
                    "- Technical Accuracy: Code concepts and practices should be correct.\n"
                    "- Communication: Easy to understand, concise and professional.\n"
                    "- STAR Method: Behavioral questions should explain Situation, Task, Action, Result."
                )

            # 2. Build parameterizable prompt
            prompt = EVALUATION_PROMPT.format(
                question=question,
                answer=answer,
                retrieved_context=retrieved_context
            )
            
            # 3. Call Granite with sampling to avoid copying placeholder scores
            logger.info("Executing Granite evaluation inference...")
            response = self.granite.generate(prompt, params={
                "decoding_method": "sample",
                "temperature": 0.3,
                "top_p": 0.95,
                "max_new_tokens": 1024
            })
            logger.info(f"Raw Granite evaluation response: {response}")
            
            # 4. Clean and parse JSON
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
                
            try:
                parsed_eval = json.loads(json_str)
            except json.JSONDecodeError as je:
                logger.warning("Failed to parse evaluation JSON directly. Trying regex match...")
                match = re.search(r'\{.*\}', json_str, re.DOTALL)
                if match:
                    parsed_eval = json.loads(match.group(0))
                else:
                    raise ValueError("Granite output could not be parsed as valid JSON.") from je
            
            # Ensure required keys exist and format values
            # Cast scores to integers, overall_score to float
            scores = parsed_eval.get("scores", {})
            cleaned_scores = {
                "technical_accuracy": max(1, int(scores.get("technical_accuracy", 5))),
                "communication": max(1, int(scores.get("communication", 5))),
                "problem_solving": max(1, int(scores.get("problem_solving", 5))),
                "confidence": max(1, int(scores.get("confidence", 5))),
                "completeness": max(1, int(scores.get("completeness", 5))),
                "clarity": max(1, int(scores.get("clarity", 5))),
                "professionalism": max(1, int(scores.get("professionalism", 5))),
                "relevance": max(1, int(scores.get("relevance", 5))),
                "depth_of_knowledge": max(1, int(scores.get("depth_of_knowledge", 5)))
            }
            
            # Calculate overall_score from dimension scores if Granite returned 0
            raw_overall = float(parsed_eval.get("overall_score", 0))
            if raw_overall < 1.0:
                avg = sum(cleaned_scores.values()) / len(cleaned_scores)
                raw_overall = round(avg, 1)
                logger.warning(f"Granite returned overall_score=0. Computed from dimensions: {raw_overall}")
            
            final_eval = {
                "overall_score": raw_overall,
                "scores": cleaned_scores,
                "strengths": parsed_eval.get("strengths", "No strengths listed."),
                "weaknesses": parsed_eval.get("weaknesses", "No weaknesses listed."),
                "missing_concepts": parsed_eval.get("missing_concepts", []),
                "improvement_tips": parsed_eval.get("improvement_tips", "Practice communicating core concepts."),
                "alternative_better_answer": parsed_eval.get("alternative_better_answer", ""),
                "ideal_model_answer": parsed_eval.get("ideal_model_answer", "No model answer provided."),
                "recommended_learning_topics": parsed_eval.get("recommended_learning_topics", []),
                "confidence_feedback": parsed_eval.get("confidence_feedback", ""),
                "interviewers_remarks": parsed_eval.get("interviewers_remarks", "")
            }
            
            logger.info(f"Evaluation completed with overall score: {final_eval['overall_score']}")
            return final_eval
        except Exception as e:
            logger.error(f"Error evaluating candidate response: {str(e)}", exc_info=True)
            # Do NOT return hardcoded/fake scores — let the caller handle the real error
            return None
