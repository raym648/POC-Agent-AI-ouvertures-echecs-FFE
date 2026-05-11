# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/api/v1/videos.py

from fastapi import APIRouter, HTTPException
from app.services.youtube_service import YouTubeService
from app.models.video_schema import VideoResponse

router = APIRouter()


@router.get("/videos/{opening}", response_model=VideoResponse)
def get_videos(opening: str):
    """
    Endpoint REST pour récupérer des vidéos YouTube
    liées à une ouverture d'échecs.
    """

    try:
        service = YouTubeService()

        videos = service.search_videos(opening)

        return VideoResponse(
            opening=opening,
            count=len(videos),
            videos=videos
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
