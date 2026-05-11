# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/api/v1/videos.py

from fastapi import APIRouter, HTTPException

from app.agents.langgraph_agent import run_agent


router = APIRouter()


@router.get("/videos/{opening}")
async def get_videos(opening: str):

    try:

        result = await run_agent(
            opening,
            mode="videos",
        )

        if result.get("error"):

            raise HTTPException(
                status_code=400,
                detail=result["error"],
            )

        return {
            "opening": result.get("opening"),
            "videos": result.get("videos", []),
            "source": result.get("source"),
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
