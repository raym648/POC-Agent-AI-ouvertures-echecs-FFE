# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/api/v1/moves.py

from fastapi import APIRouter, HTTPException

from app.agents.langgraph_agent import run_agent


router = APIRouter(
    prefix="/moves",
    tags=["Moves"],
)


@router.get("/{fen:path}")
async def get_moves(fen: str):

    try:

        result = await run_agent(
            fen,
            mode="moves",
        )

        # =================================================
        # ERREURS
        # =================================================

        if result.get("error"):
            raise HTTPException(
                status_code=400,
                detail=result["error"],
            )

        # =================================================
        # AUCUNE THEORIE TROUVEE
        # =================================================

        if not result.get("moves"):

            return {
                "fen": fen,
                "moves": [],
                "opening": result.get("opening"),
                "videos": result.get("videos", []),
                "rag_context": result.get("rag_context", []),
                "message": (
                    "Aucun coup théorique trouvé "
                    "via Lichess."
                ),
            }

        # =================================================
        # SUCCESS
        # =================================================

        return {
            "fen": fen,
            "moves": result.get("moves", []),
            "opening": result.get("opening"),
            "videos": result.get("videos", []),
            "rag_context": result.get("rag_context", []),
            "source": result.get("source"),
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
