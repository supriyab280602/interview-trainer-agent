from fastapi import APIRouter, Depends, HTTPException, Header, Request, status, Response
from fastapi.responses import StreamingResponse
from typing import Optional, List
import io
from api.auth_routes import get_current_user
from schemas.interview import InterviewStartRequest, AnswerSubmitRequest
from services.interview_service import InterviewService
from utils.pdf_generator import generate_interview_pdf

router = APIRouter(prefix="/api/interview", tags=["Interviews"])

def get_interview_service(request: Request) -> InterviewService:
    return request.app.state.interview_service


@router.post("/start")
async def start_interview(
    req: InterviewStartRequest,
    current_user: dict = Depends(get_current_user),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """
    Start a new interview session under the user's active career profile.
    """
    interview = await interview_service.start_interview(
        user_id=current_user["email"],
        profile_name=req.profile_name,
        interview_type=req.interview_type,
        difficulty=req.difficulty,
        length=req.length
    )
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate interview session."
        )
    return interview


@router.post("/answer")
async def submit_answer(
    req: AnswerSubmitRequest,
    current_user: dict = Depends(get_current_user),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """
    Submit answer to the current question. 
    Triggers Granite-based evaluation, increments score, and returns the next question.
    """
    result = await interview_service.submit_answer(req)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI evaluation service returned no response. Please check IBM watsonx.ai credentials."
        )
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    return result


@router.post("/end")
async def end_interview(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """
    Conclude the interview session, calculate overall scores, and write
    the final evaluation summary.
    """
    summary = await interview_service.end_and_summarize_interview(interview_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to compile summary. Ensure all questions have been answered."
        )
    return summary


@router.get("/history")
async def get_history(
    current_user: dict = Depends(get_current_user),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """
    Retrieve list of past interviews completed by the user.
    """
    history = await interview_service.get_history_by_user(current_user["email"])
    return history


@router.get("/{interview_id}/report")
async def export_report_pdf(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """
    Generate and download a beautifully styled PDF report of the interview.
    """
    # Fetch interview doc
    interview = await interview_service.db.get_document("interviews", interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview report session not found."
        )

    # Security check: Ensure it belongs to the logged-in user
    if interview["user_id"] != current_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this interview report."
        )

    if interview.get("status") != "COMPLETED" or not interview.get("summary"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is not yet concluded. Cannot generate report."
        )

    try:
        pdf_bytes = generate_interview_pdf(interview, current_user["full_name"])
        
        # Return as downloadable binary stream
        headers = {
            "Content-Disposition": f'attachment; filename="interview_report_{interview_id}.pdf"'
        }
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers=headers
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error compiling PDF: {str(e)}"
        )
