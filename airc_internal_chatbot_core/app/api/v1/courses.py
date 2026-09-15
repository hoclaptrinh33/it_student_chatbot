"""Course and prerequisite REST API."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_course_service,
    get_prerequisite_service,
    require_permission,
)
from app.models.academic_schemas import (
    CourseCreate,
    CoursePrerequisitesResponse,
    CourseResponse,
    CourseUpdate,
    PrerequisiteCreate,
)
from app.models.auth import Permission, User
from app.services.course_service import CourseConflictError, CourseService
from app.services.prerequisite_service import PrerequisiteService

router = APIRouter()
courses_view = require_permission(Permission.COURSES_VIEW)
courses_manage = require_permission(Permission.COURSES_MANAGE)


@router.get("", response_model=List[CourseResponse])
async def list_courses(
    semester: Optional[int] = Query(default=None, ge=1, le=8),
    career_track: Optional[str] = None,
    q: Optional[str] = None,
    code: Optional[str] = None,
    current_user: User = Depends(courses_view),
    course_service: CourseService = Depends(get_course_service),
):
    return await course_service.list_courses(
        semester=semester,
        career_track=career_track,
        q=q,
        code=code,
    )


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreate,
    current_user: User = Depends(courses_manage),
    course_service: CourseService = Depends(get_course_service),
):
    try:
        return await course_service.create_course(payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{course_id}/prerequisites", response_model=CoursePrerequisitesResponse)
async def get_course_prerequisites(
    course_id: str,
    current_user: User = Depends(courses_view),
    prerequisite_service: PrerequisiteService = Depends(get_prerequisite_service),
):
    data = await prerequisite_service.get_course_prerequisites(course_id)
    if not data:
        raise HTTPException(status_code=404, detail="Course not found")
    return data


@router.post("/{course_id}/prerequisites", status_code=status.HTTP_201_CREATED)
async def add_course_prerequisite(
    course_id: str,
    payload: PrerequisiteCreate,
    current_user: User = Depends(courses_manage),
    prerequisite_service: PrerequisiteService = Depends(get_prerequisite_service),
):
    try:
        return await prerequisite_service.add_prerequisite(course_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Course not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{course_id}/prerequisites/{prereq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course_prerequisite(
    course_id: str,
    prereq_id: str,
    current_user: User = Depends(courses_manage),
    prerequisite_service: PrerequisiteService = Depends(get_prerequisite_service),
):
    deleted = await prerequisite_service.delete_prerequisite(course_id, prereq_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prerequisite not found")


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    code: Optional[str] = Query(default=None, description="Lookup by course code, e.g. INT2104"),
    current_user: User = Depends(courses_view),
    course_service: CourseService = Depends(get_course_service),
):
    course = await course_service.get_course(course_id, code=code)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.patch("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    payload: CourseUpdate,
    current_user: User = Depends(courses_manage),
    course_service: CourseService = Depends(get_course_service),
):
    try:
        course = await course_service.update_course(course_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: str,
    current_user: User = Depends(courses_manage),
    course_service: CourseService = Depends(get_course_service),
):
    try:
        deleted = await course_service.delete_course(course_id)
    except CourseConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Course not found")
