from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Request, status
from typing import Optional
from api.auth_routes import get_current_user, get_auth_service
from services.resume_service import ResumeService

router = APIRouter(prefix="/api/resume", tags=["Resumes"])

def get_resume_service(request: Request) -> ResumeService:
    return request.app.state.resume_service

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
    auth_service = Depends(get_auth_service)
):
    """
    Upload and parse candidate resume PDF. 
    Limits file size to 5MB and requires PDF extension.
    """
    # 1. Validate PDF extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid file format. Only PDF files are supported."
        )

    # 2. Validate file size (e.g. 5MB)
    max_size = 5 * 1024 * 1024
    file_bytes = await file.read()
    if len(file_bytes) > max_size:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File size exceeds maximum limit of 5MB."
        )

    # 3. Parse and upload
    resume_doc = await resume_service.parse_and_save_resume(
        user_id=current_user["email"],
        file_bytes=file_bytes,
        file_name=file.filename
    )

    if not resume_doc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse or process the uploaded resume."
        )

    # 4. Link to active profile
    active_profile = current_user.get("active_profile_name")
    if active_profile:
        await auth_service.create_or_update_profile(
            email=current_user["email"],
            profile_name=active_profile,
            exp_level=current_user["profiles"][active_profile]["experience_level"],
            role=current_user["profiles"][active_profile]["target_role"]
        )
        # Update user doc to attach resume_id
        current_user["profiles"][active_profile]["resume_id"] = resume_doc["_id"]
        # Update Cloudant
        await resume_service.db.update_document("users", current_user["email"], current_user)

    return {"message": "Resume uploaded and analyzed successfully", "resume": resume_doc}


@router.get("")
async def get_resume(
    current_user: dict = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service)
):
    """
    Get the metadata details of the currently uploaded resume linked with the active profile.
    """
    active_profile = current_user.get("active_profile_name")
    if not active_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active career profile configured."
        )

    resume_id = current_user["profiles"][active_profile].get("resume_id")
    if not resume_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume uploaded for the active profile."
        )

    resume = await resume_service.get_resume_by_id(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume metadata record not found in database."
        )
    return resume


@router.delete("")
async def delete_resume(
    current_user: dict = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service)
):
    """
    Delete the active profile resume from database and storage.
    """
    active_profile = current_user.get("active_profile_name")
    if not active_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active career profile configured."
        )

    resume_id = current_user["profiles"][active_profile].get("resume_id")
    if not resume_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found to delete."
        )

    success = await resume_service.delete_resume(resume_id, current_user["email"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resume files."
        )

    # Remove resume link from active profile
    current_user["profiles"][active_profile]["resume_id"] = None
    await resume_service.db.update_document("users", current_user["email"], current_user)

    return {"message": "Resume deleted successfully"}
