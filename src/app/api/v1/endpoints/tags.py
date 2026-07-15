from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.models.catalog import Tag
from app.modules.tags.schemas import TagCreate, TagRead, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])

DatabaseSession: TypeAlias = Annotated[AsyncSession, Depends(get_db_session)]


async def _get_tag(session: AsyncSession, tag_id: int) -> Tag:
    tag = await session.scalar(select(Tag).where(Tag.id == tag_id))
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")
    return tag


@router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(data: TagCreate, session: DatabaseSession) -> Tag:
    tag = Tag(**data.model_dump())
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return tag


@router.get("/", response_model=list[TagRead])
async def list_tags(session: DatabaseSession) -> list[Tag]:
    tags = await session.scalars(select(Tag).order_by(Tag.id))
    return list(tags)


@router.get("/{tag_id}", response_model=TagRead)
async def get_tag(tag_id: int, session: DatabaseSession) -> Tag:
    return await _get_tag(session, tag_id)


@router.put("/{tag_id}", response_model=TagRead)
async def update_tag(
    tag_id: int,
    data: TagUpdate,
    session: DatabaseSession,
) -> Tag:
    tag = await _get_tag(session, tag_id)

    for field, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(tag, field, value)

    await session.commit()
    await session.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, session: DatabaseSession) -> Response:
    tag = await _get_tag(session, tag_id)
    await session.delete(tag)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
