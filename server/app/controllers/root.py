from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["Root"])
async def read_root():
    """Simple health check endpoint returning Hello World."""
    return {"message": "Hello World"} 