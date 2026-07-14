from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from typing import Optional
from api.auth_routes import get_current_user
from services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api", tags=["Analytics"])

def get_analytics_service(request: Request) -> AnalyticsService:
    return request.app.state.analytics_service


@router.get("/analytics")
async def get_analytics(
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get aggregated performance metrics, skills analytics, and progress timelines.
    """
    result = await analytics_service.get_user_analytics(current_user["email"])
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute analytics."
        )
    return result


@router.get("/dashboard")
async def get_dashboard_summary(
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get quick overview statistics specifically formatted for the main welcome dashboard.
    """
    analytics = await analytics_service.get_user_analytics(current_user["email"])
    
    # Retrieve active career profile details
    active_profile = current_user.get("active_profile_name")
    profile_details = None
    if active_profile and "profiles" in current_user:
        profile_details = current_user["profiles"].get(active_profile)
        
    dashboard_data = {
        "user_name": current_user["full_name"],
        "active_profile": active_profile,
        "profile_details": profile_details,
        "stats": {
            "average_score": analytics.get("average_score", 0.0),
            "highest_score": analytics.get("highest_score", 0.0),
            "total_interviews": analytics.get("total_interviews", 0),
            "completed_interviews": analytics.get("completed_interviews", 0),
            "completion_rate": analytics.get("completion_rate", 0.0)
        },
        "recent_progress": analytics.get("progress_trend", [])[-3:] # Last 3 items
    }
    return dashboard_data
