# Evaluation prompt template for IBM Granite

EVALUATION_PROMPT = """You are an expert interviewer evaluating a candidate's answer to an interview question.

Question:
{question}

Candidate's Answer:
{answer}

Evaluation Rubric & reference guidelines:
{retrieved_context}

Your task is to analyze the candidate's response across multiple dimensions. 

CRITICAL EVALUATION RULES:
1. Identify the TYPE of the question:
   - CONCEPTUAL/DESIGN/SCENARIO (e.g. "How does X work?", "What security features would you use?"):
     - Focus on accuracy, depth of knowledge, trade-offs, and conceptual clarity.
     - Do NOT penalize the candidate or ask for metrics/outcomes. Project metrics do not apply here.
     - Judge the answer based on whether the chosen design/concept is technically sound and thorough.
   - BEHAVIORAL/PAST PROJECT (e.g. "Tell me about a time...", "Describe a project you built"):
     - Focus on actions, problem-solving, and quantifiable metrics/results (STAR method).
     - It is appropriate to look for metrics and outcomes here.
     
2. Assign integer scores between 1 and 10 for each dimension:
   - Mediocre: 4-6 | Good: 7-8 | Excellent: 9-10.
   - Do NOT default to 7.0 for everything. Give an honest, differentiated score based on actual answer depth.
   - A score of 0 is NOT allowed.

Provide your complete evaluation in JSON format matching the exact structure below.
You must output ONLY valid JSON. Do not include markdown syntax, backticks, or prefix explanations.

JSON Structure:
{{
  "overall_score": 7.5,
  "scores": {{
    "technical_accuracy": 8,
    "communication": 7,
    "problem_solving": 7,
    "confidence": 8,
    "completeness": 7,
    "clarity": 8,
    "professionalism": 8,
    "relevance": 8,
    "depth_of_knowledge": 7
  }},
  "strengths": "Detailed explanation of what the candidate did well.",
  "weaknesses": "Constructive explanation of what was lacking or wrong.",
  "missing_concepts": ["concept1", "concept2"],
  "improvement_tips": "Clear action steps for the candidate to improve.",
  "alternative_better_answer": "A suggestion of a better/more structured way to phrase their answer.",
  "ideal_model_answer": "The ideal, high-scoring model answer for this question.",
  "recommended_learning_topics": ["topic1", "topic2"],
  "confidence_feedback": "Observation on their speaking style and delivery confidence.",
  "interviewers_remarks": "Summary thoughts from the interviewer."
}}
"""
