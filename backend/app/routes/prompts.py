from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.prompt_version import PromptVersion
from app.schemas.analytics import PromptVersionResponse, PromptVersionCreate, PromptComparisonResult
from app.services.prompt_comparator import compare_prompt_versions

router = APIRouter()


@router.get("", response_model=list[PromptVersionResponse])
async def list_prompts(db: AsyncSession = Depends(get_db)):
    stmt = select(PromptVersion).order_by(desc(PromptVersion.created_at))
    result = await db.execute(stmt)
    versions = result.scalars().all()
    return [
        PromptVersionResponse(
            id=v.id,
            prompt_name=v.prompt_name,
            version=v.version,
            template_text=v.template_text,
            created_at=v.created_at,
            metadata=v.metadata_,
        )
        for v in versions
    ]


@router.post("", response_model=PromptVersionResponse)
async def create_prompt(data: PromptVersionCreate, db: AsyncSession = Depends(get_db)):
    pv = PromptVersion(
        prompt_name=data.prompt_name,
        version=data.version,
        template_text=data.template_text,
        metadata_=data.metadata,
    )
    db.add(pv)
    await db.flush()
    return PromptVersionResponse(
        id=pv.id,
        prompt_name=pv.prompt_name,
        version=pv.version,
        template_text=pv.template_text,
        created_at=pv.created_at,
        metadata=pv.metadata_,
    )


@router.get("/compare", response_model=PromptComparisonResult)
async def compare_prompts(
    v1: UUID = Query(...),
    v2: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    result = await compare_prompt_versions(db, v1, v2)
    if not result:
        raise HTTPException(status_code=404, detail="One or both prompt versions not found")
    return result
