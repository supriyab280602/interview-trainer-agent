import logging
import uuid
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from config import settings
from services.cloudant_service import CloudantService
from services.resume_service import ResumeService
from services.granite_service import GraniteService
from services.rag_service import RAGService
from services.evaluation_service import EvaluationService
from prompts.question_prompt import QUESTION_GENERATION_PROMPT
from prompts.summary_prompt import SUMMARY_PROMPT
from models.interview import Interview, QuestionEvaluation, InterviewSummary

logger = logging.getLogger("InterviewService")

class InterviewService:
    """
    InterviewService manages the interview session lifecycle: 
    - Session start & Resume context binding
    - Question generation (RAG-supported)
    - Response submissions and evaluations (Adaptive difficulty)
    - Interview completion aggregation (PDF/Cloudant reports)
    """
    
    def __init__(
        self, 
        db_service: CloudantService, 
        resume_service: ResumeService, 
        granite_service: GraniteService,
        rag_service: RAGService,
        evaluation_service: EvaluationService
    ) -> None:
        self.db = db_service
        self.resume = resume_service
        self.granite = granite_service
        self.rag = rag_service
        self.evaluation = evaluation_service

    async def _get_profile_and_resume(self, user_id: str, profile_name: str) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Helper to fetch user career profile settings and associated parsed resume.
        """
        user_doc = await self.db.get_document("users", user_id)
        if not user_doc:
            return None, None
            
        profiles = user_doc.get("profiles", {})
        profile = profiles.get(profile_name)
        if not profile:
            return None, None
            
        resume_id = profile.get("resume_id")
        resume = None
        if resume_id:
            resume = await self.resume.get_resume_by_id(resume_id)
            
        return profile, resume

    async def start_interview(self, user_id: str, profile_name: str, interview_type: str, difficulty: str, length: int) -> Optional[Dict[str, Any]]:
        """
        Configure and start a new interview session.
        Generates the first question immediately.
        """
        try:
            logger.info(f"Starting interview config for user '{user_id}' profile '{profile_name}'...")
            
            # Fetch profile and resume info
            profile, resume = await self._get_profile_and_resume(user_id, profile_name)
            if not profile:
                logger.error(f"Career profile '{profile_name}' not found for user '{user_id}'")
                return None
                
            interview_id = f"interview_{uuid.uuid4().hex}"
            resume_id = resume.get("_id") if resume else None

            # Construct empty interview model
            interview = Interview(
                _id=interview_id,
                user_id=user_id,
                profile_name=profile_name,
                resume_id=resume_id,
                role=profile["target_role"],
                interview_type=interview_type,
                difficulty=difficulty,
                length=length,
                questions=[],
                answers=[],
                evaluations=[],
                status="IN_PROGRESS"
            )

            # Ingest resume into RAG if resume is uploaded
            # Ingesting the resume context helps retrieve specific skills or project domains
            if resume:
                resume_text = f"Candidate Profile: Name {resume.get('candidate_name')}. Skills: {', '.join(resume.get('skills', []))}. Experience: {json.dumps(resume.get('work_experience', []))}. Projects: {json.dumps(resume.get('projects', []))}."
                self.rag.ingest_document(
                    text=resume_text,
                    source_metadata={
                        "source": f"resume_{resume_id}",
                        "source_id": resume_id,
                        "category": "CandidateResume",
                        "domain": profile["target_role"]
                    },
                    collection_name=f"resume_coll_{interview_id}"
                )

            # Generate first question
            first_question = await self._generate_question_text(interview, profile, resume)
            interview.questions.append(first_question)

            # Save in Cloudant
            success = await self.db.create_document("interviews", interview_id, interview.model_dump(by_alias=True))
            if success:
                logger.info(f"Interview '{interview_id}' started. First question generated.")
                return interview.model_dump(by_alias=True)
            return None
        except Exception as e:
            logger.error(f"Error starting interview: {str(e)}", exc_info=True)
            return None

    async def _generate_question_text(self, interview: Interview, profile: Dict[str, Any], resume: Optional[Dict[str, Any]]) -> str:
        """
        Orchestrate RAG retrieval and template assembly to generate the next question using Granite.
        """
        # Determine current difficulty (handling Adaptive modes)
        current_difficulty = interview.difficulty
        if interview.difficulty == "Adaptive" and len(interview.evaluations) > 0:
            last_score = interview.evaluations[-1].overall_score
            if last_score >= 8.5:
                current_difficulty = "Hard"
            elif last_score <= 5.0:
                current_difficulty = "Easy"
            else:
                current_difficulty = "Medium"
        elif interview.difficulty == "Adaptive":
            current_difficulty = "Medium" # Default fallback for first question in adaptive mode

        # Assemble candidate profile block
        profile_block = (
            f"Target Role: {profile['target_role']}\n"
            f"Experience level: {profile['experience_level']}\n"
        )
        if resume:
            profile_block += (
                f"Skills: {', '.join(resume.get('skills', []))}\n"
                f"Programming Languages: {', '.join(resume.get('programming_languages', []))}\n"
                f"Frameworks: {', '.join(resume.get('frameworks', []))}\n"
                f"Projects: {json.dumps(resume.get('projects', []))}\n"
            )

        # Retrieve RAG context from knowledge base
        query = f"Interview questions for {profile['target_role']} {interview.interview_type} {current_difficulty}"
        retrieved_context = self.rag.retrieve_context(
            query=query,
            collection_name="kb_questions",
            n_results=2,
            filters={"category": interview.interview_type} if interview.interview_type in ["HR", "Technical", "Behavioral"] else None
        )
        
        # If candidate-specific resume was ingested, search it for projects to ask about
        if resume:
            resume_query = "Resume projects achievements skills"
            resume_context = self.rag.retrieve_context(
                query=resume_query,
                collection_name=f"resume_coll_{interview.id}",
                n_results=1
            )
            retrieved_context += f"\n\nCandidate Experience Context:\n{resume_context}"

        # Construct progress history block
        history = ""
        for idx, (q, a) in enumerate(zip(interview.questions, interview.answers)):
            history += f"Q{idx+1}: {q}\nA{idx+1}: {a}\n\n"

        prompt = QUESTION_GENERATION_PROMPT.format(
            interview_type=interview.interview_type,
            role=profile["target_role"],
            experience_level=profile["experience_level"],
            difficulty=current_difficulty,
            candidate_profile=profile_block,
            retrieved_context=retrieved_context,
            question_index=len(interview.questions) + 1,
            history=history if history else "This is the start of the interview. Ask the first question."
        )

        logger.info(f"Generating question {len(interview.questions) + 1} with Granite...")
        # Use sampling with temperature to avoid generating the same question repeatedly
        question = self.granite.generate(prompt, params={
            "decoding_method": "sample",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_new_tokens": 256
        })
        # Strip common prefixes the model may add
        question = question.strip()
        
        # Remove any leading interviewer/question tags
        question = re.sub(r'^(?:Interviewer|Question|Next Question)\s*:\s*', '', question, flags=re.IGNORECASE)
        
        # Strip instruction guidelines that might be leaked by the LLM
        # Split into sentences to filter out leaked system instructions
        sentences = re.split(r'(?<=[.!?])\s+', question)
        filtered_sentences = []
        for s in sentences:
            s_clean = s.strip()
            # If it's a leaked instruction sentence, skip it
            s_lower = s_clean.lower()
            if any(instr in s_lower for instr in [
                "keep the question", "ideally no longer", "sentences", "tone should be", 
                "professional, neutral", "do not include", "preamble", "preface", 
                "guideline", "pleasantries", "greeting", "interviewer", "expert interviewer"
            ]):
                continue
            # Remove any trailing/inline list indexes like "8."
            s_clean = re.sub(r'^\d+[\.\:\)]\s*', '', s_clean)
            if s_clean:
                filtered_sentences.append(s_clean)
        
        if filtered_sentences:
            question = " ".join(filtered_sentences).strip()
        return question

    async def submit_answer(self, req: AnswerSubmitRequest) -> Optional[Dict[str, Any]]:
        """
        Submit a candidate response:
        1. Grade the answer using EvaluationService.
        2. Append answer and score details to session.
        3. If length limits not reached, generate next question.
        4. Save session back to Cloudant.
        """
        try:
            logger.info(f"Submitting answer for question index {req.question_index} in interview '{req.interview_id}'...")
            
            interview_doc = await self.db.get_document("interviews", req.interview_id)
            if not interview_doc:
                logger.error(f"Interview '{req.interview_id}' not found.")
                return None
                
            interview = Interview(**interview_doc)
            
            # Index check
            if req.question_index != len(interview.answers):
                logger.error(f"Mismatch: Submitting answer for index {req.question_index} when answers count is {len(interview.answers)}.")
                return None

            # Get the question asked
            question = interview.questions[req.question_index]

            # Grade the response
            eval_dict = await self.evaluation.evaluate_answer(
                question=question,
                answer=req.answer,
                category=interview.interview_type,
                domain=interview.role
            )
            
            if not eval_dict:
                logger.error("Answer evaluation failed — IBM watsonx.ai did not return valid scores.")
                return {"error": "AI evaluation failed. Please check your IBM watsonx.ai credentials and try again."}

            # Save answer and evaluation
            interview.answers.append(req.answer)
            interview.evaluations.append(QuestionEvaluation(**eval_dict))

            # Decide whether to generate the next question or terminate
            is_complete = len(interview.answers) >= len(interview.questions) # Check if all generated questions are answered
            max_questions_reached = len(interview.answers) >= interview_doc.get("length", 5)

            next_question = None
            if not max_questions_reached:
                # Retrieve profile details to build next question using profile_name
                profile_name_to_use = interview.profile_name
                if not profile_name_to_use:
                    user_doc = await self.db.get_document("users", interview.user_id)
                    profile_name_to_use = user_doc.get("active_profile_name") if user_doc else None
                
                profile, resume = await self._get_profile_and_resume(interview.user_id, profile_name_to_use)
                if profile:
                    try:
                        next_question = await self._generate_question_text(interview, profile, resume)
                        interview.questions.append(next_question)
                    except Exception as qe:
                        logger.error(f"Failed to generate next question: {str(qe)}", exc_info=True)
                        return {"error": f"Answer was evaluated, but next question generation failed: {str(qe)}"}
            else:
                interview.status = "COMPLETED"
                interview.completed_time = datetime.utcnow().isoformat()

            # Update interview doc in db
            updated_data = interview.model_dump(by_alias=True)
            # Calculate running average overall score from evaluations
            if interview.evaluations:
                eval_scores = [e.overall_score for e in interview.evaluations]
                avg_score = sum(eval_scores) / len(eval_scores)
                # If all scores are 0 (broken eval), compute from dimension scores
                if avg_score < 1.0:
                    dim_scores = []
                    for e in interview.evaluations:
                        dim_vals = [v for v in e.scores.values() if isinstance(v, (int, float)) and v > 0]
                        if dim_vals:
                            dim_scores.append(sum(dim_vals) / len(dim_vals))
                    if dim_scores:
                        avg_score = sum(dim_scores) / len(dim_scores)
                updated_data["overall_score"] = round(max(avg_score, 0.0), 2)
                interview.overall_score = updated_data["overall_score"]
                
            success = await self.db.update_document("interviews", req.interview_id, updated_data)
            if success:
                logger.info(f"Answer submitted. Session status: {interview.status}, overall_score: {updated_data.get('overall_score')}")
                return {
                    "evaluation": eval_dict,
                    "next_question": next_question,
                    "status": interview.status,
                    "overall_score": updated_data.get("overall_score", 0.0)
                }
            return {"error": "Failed to save interview progress to database."}
        except Exception as e:
            logger.error(f"Error submitting candidate answer: {str(e)}", exc_info=True)
            return {"error": f"Submission failed: {str(e)}"}

    async def end_and_summarize_interview(self, interview_id: str) -> Optional[Dict[str, Any]]:
        """
        Aggregate individual question scores, compile strengths, weaknesses, 
        and generate a final study plan using Granite.
        """
        try:
            logger.info(f"Summarizing completed interview '{interview_id}'...")
            
            interview_doc = await self.db.get_document("interviews", interview_id)
            if not interview_doc:
                return None
                
            interview = Interview(**interview_doc)
            if not interview.evaluations:
                return None

            # 1. Compile individual question ratings
            evals_summary = ""
            for idx, (q, a, ev) in enumerate(zip(interview.questions, interview.answers, interview.evaluations)):
                evals_summary += (
                    f"Question {idx+1}: {q}\n"
                    f"Answer {idx+1}: {a}\n"
                    f"Score: {ev.overall_score}/10\n"
                    f"Remarks: {ev.interviewers_remarks}\n"
                    f"Missing concepts: {', '.join(ev.missing_concepts)}\n\n"
                )

            # 2. Build prompt
            prompt = SUMMARY_PROMPT.format(
                role=interview.role,
                interview_type=interview.interview_type,
                difficulty=interview.difficulty,
                evaluations=evals_summary
            )

            # 3. Request summary from Granite
            logger.info("Generating aggregate summary analysis from Granite...")
            response = self.granite.generate(prompt)

            # Clean and parse response
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            try:
                summary_data = json.loads(json_str)
            except json.JSONDecodeError:
                match = re.search(r'\{.*\}', json_str, re.DOTALL)
                if match:
                    summary_data = json.loads(match.group(0))
                else:
                    raise ValueError("Summary result could not be parsed as valid JSON.")

            # Cast nested details
            scores = summary_data.get("scores", {})
            cleaned_scores = {
                "technical_score": float(scores.get("technical_score", 5.0)),
                "hr_score": float(scores.get("hr_score", 5.0)),
                "behavioural_score": float(scores.get("behavioural_score", 5.0)),
                "communication_score": float(scores.get("communication_score", 5.0)),
                "confidence_score": float(scores.get("confidence_score", 5.0))
            }

            final_summary = InterviewSummary(
                overall_score=float(summary_data.get("overall_score", 5.0)),
                scores=cleaned_scores,
                strength_analysis=summary_data.get("strength_analysis", "No strength analysis compiled."),
                weakness_analysis=summary_data.get("weakness_analysis", "No weakness analysis compiled."),
                frequently_missed_topics=summary_data.get("frequently_missed_topics", []),
                recommended_study_plan=summary_data.get("recommended_study_plan", "No study plan created."),
                readiness_level=summary_data.get("readiness_level", "Needs Practice"),
                final_ai_recommendation=summary_data.get("final_ai_recommendation", "")
            )

            # 4. Save summary details to Database
            interview.summary = final_summary
            interview.status = "COMPLETED"
            interview.completed_time = datetime.utcnow().isoformat()
            
            # Ensure overall score is matching
            interview.overall_score = final_summary.overall_score

            # Clear temporary RAG resume collection if exists
            self.rag.clear_collection(f"resume_coll_{interview_id}")

            # Save in database
            await self.db.update_document("interviews", interview_id, interview.model_dump(by_alias=True))
            logger.info("Final interview summary successfully compiled and stored.")
            return interview.model_dump(by_alias=True)
        except Exception as e:
            logger.error(f"Error compiling final summary report: {str(e)}", exc_info=True)
            return None

    async def get_history_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all completed or current interviews for a user.
        """
        try:
            query = {"selector": {"user_id": user_id}}
            docs = await self.db.query_documents("interviews", query)
            # Sort by started_time desc
            docs.sort(key=lambda x: x.get("started_time", ""), reverse=True)
            return docs
        except Exception as e:
            logger.error(f"Error getting interview history: {str(e)}")
            return []
