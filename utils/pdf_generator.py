from fpdf import FPDF
import io
import logging
from typing import Dict, Any

logger = logging.getLogger("PDFGenerator")

class PDFReportGenerator(FPDF):
    """
    Premium PDF generator styling for compiling interview session reports.
    Uses IBM-inspired typography and spacing standards.
    """
    
    def header(self) -> None:
        # Title brand block
        self.set_fill_color(15, 98, 254) # IBM Blue: #0F62FE
        self.rect(0, 0, 210, 15, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, -2, "IBM INTERNSHIP CHALLENGE - AI INTERVIEW TRAINER REPORT", align="C")
        self.ln(10)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(111, 111, 111)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def generate_interview_pdf(interview: Dict[str, Any], user_name: str) -> bytes:
    """
    Compiles full interview questions, candidate answers, evaluations, 
    and aggregate AI summaries into a structured, printable PDF document.
    
    Returns:
        bytes: Binary content of the generated PDF file.
    """
    try:
        logger.info("Initializing PDF compilation...")
        pdf = PDFReportGenerator()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Doc Title
        pdf.ln(5)
        pdf.set_text_color(22, 22, 22) # Primary Text
        pdf.set_font("Helvetica", "B", 22)
        pdf.cell(0, 10, "Interview Performance Report", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(111, 111, 111) # Secondary Text
        pdf.cell(0, 5, f"Candidate Name: {user_name}  |  Date: {interview.get('started_time', '')[:10]}", ln=True)
        pdf.cell(0, 5, f"Target Job Role: {interview.get('role', 'N/A')}  |  Type: {interview.get('interview_type', 'N/A')}", ln=True)
        pdf.cell(0, 5, f"Configured Difficulty: {interview.get('difficulty', 'N/A')}", ln=True)
        pdf.ln(8)
        
        # Horizontal Rule
        pdf.set_draw_color(221, 225, 230) # Border #DDE1E6
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Overall Summary Section
        pdf.set_text_color(15, 98, 254) # Blue Header
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "1. Executive AI Summary", ln=True)
        pdf.ln(2)
        
        summary = interview.get("summary", {})
        pdf.set_text_color(22, 22, 22)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 6, f"Overall Score: {round(interview.get('overall_score', 0.0), 2)}/10", ln=True)
        pdf.cell(0, 6, f"Readiness Level: {summary.get('readiness_level', 'Needs Practice')}", ln=True)
        pdf.ln(2)
        
        # Sub-scores
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Performance Dimensions:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        scores = summary.get("scores", {})
        pdf.cell(0, 5, f"- Technical Capability: {scores.get('technical_score', 0.0)}/10", ln=True)
        pdf.cell(0, 5, f"- HR / Behavior Alignment: {scores.get('hr_score', 0.0)}/10", ln=True)
        pdf.cell(0, 5, f"- STAR Methodology Adaptability: {scores.get('behavioural_score', 0.0)}/10", ln=True)
        pdf.cell(0, 5, f"- Communication Clarity: {scores.get('communication_score', 0.0)}/10", ln=True)
        pdf.cell(0, 5, f"- Delivery Confidence: {scores.get('confidence_score', 0.0)}/10", ln=True)
        pdf.ln(4)
        
        # Strengths & Weaknesses
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Strength Analysis:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, summary.get("strength_analysis", "No strengths compiled."))
        pdf.ln(3)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Areas for Improvement:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, summary.get("weakness_analysis", "No weakness analysis compiled."))
        pdf.ln(3)

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Final AI Recommendation:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, summary.get("final_ai_recommendation", ""))
        pdf.ln(3)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Study & Practice Plan:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, summary.get("recommended_study_plan", "N/A"))
        pdf.ln(8)
        
        # Questions & Answers Detailed breakdown
        pdf.add_page()
        pdf.set_text_color(15, 98, 254)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "2. Detailed Q&A Evaluation", ln=True)
        pdf.ln(4)
        
        questions = interview.get("questions", [])
        answers = interview.get("answers", [])
        evals = interview.get("evaluations", [])
        
        for idx in range(len(answers)):
            pdf.set_draw_color(221, 225, 230)
            pdf.set_text_color(22, 22, 22)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 6, f"Question {idx+1}: {questions[idx]}", ln=True)
            pdf.ln(1)
            
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(69, 137, 255) # Secondary Blue
            pdf.cell(0, 5, "Candidate Answer:", ln=True)
            pdf.set_text_color(22, 22, 22)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, answers[idx])
            pdf.ln(2)
            
            if idx < len(evals):
                ev = evals[idx]
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 5, f"Evaluation Score: {ev.get('overall_score')}/10", ln=True)
                
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 5, f"Strengths: {ev.get('strengths')}")
                pdf.multi_cell(0, 5, f"Constructive Tips: {ev.get('improvement_tips')}")
                
                # Check model answer
                model_ans = ev.get("ideal_model_answer")
                if model_ans:
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(0, 5, "Ideal Model Answer Reference:", ln=True)
                    pdf.set_font("Helvetica", "", 9)
                    pdf.set_text_color(111, 111, 111)
                    pdf.multi_cell(0, 4.5, model_ans)
                    pdf.set_text_color(22, 22, 22)
                
                # Divider between QA items
                pdf.ln(4)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(4)
                
        # Return PDF bytes
        pdf_bytes = pdf.output(dest="S")
        logger.info("PDF generated successfully.")
        return pdf_bytes
    except Exception as e:
        logger.error(f"Error compiling PDF: {str(e)}", exc_info=True)
        raise e
