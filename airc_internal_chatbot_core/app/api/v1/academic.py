"""Academic transcript, eligible courses, grades, and materials."""
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.api.dependencies import (
    get_learning_material_service,
    get_student_record_service,
    require_any_permission,
    require_permission,
)
from app.models.academic_schemas import (
    AcademicFactsDebug,
    CsvImportResponse,
    EligibleCoursesResponse,
    MaterialCreate,
    MaterialResponse,
    MaterialUpdate,
    RecordResponse,
    RecordUpsert,
    TranscriptResponse,
)
from app.models.auth import Permission, User
from app.services.learning_material_service import LearningMaterialService
from app.services.student_record_service import StudentRecordService

router = APIRouter()
records_own_or_any = require_any_permission(Permission.RECORDS_VIEW_OWN, Permission.RECORDS_VIEW_ANY)
records_any = require_permission(Permission.RECORDS_VIEW_ANY)
records_update = require_permission(Permission.RECORDS_UPDATE)
materials_view = require_permission(Permission.MATERIALS_VIEW)
materials_manage = require_permission(Permission.MATERIALS_MANAGE)


@router.get("/me/transcript", response_model=TranscriptResponse)
async def get_my_transcript(
    current_user: User = Depends(records_own_or_any),
    record_service: StudentRecordService = Depends(get_student_record_service),
):
    data = await record_service.get_transcript(current_user.user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return data


@router.get("/me/eligible-courses", response_model=EligibleCoursesResponse)
async def get_my_eligible_courses(
    current_user: User = Depends(records_own_or_any),
    record_service: StudentRecordService = Depends(get_student_record_service),
):
    data = await record_service.get_eligible_courses(current_user.user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return data


@router.get("/me/facts", response_model=AcademicFactsDebug)
async def get_my_facts(
    current_user: User = Depends(records_own_or_any),
    record_service: StudentRecordService = Depends(get_student_record_service),
):
    data = await record_service.get_facts(current_user.user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return data


@router.get("/students/{user_id}/transcript", response_model=TranscriptResponse)
async def get_student_transcript(
    user_id: str,
    current_user: User = Depends(records_any),
    record_service: StudentRecordService = Depends(get_student_record_service),
):
    data = await record_service.get_transcript(user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return data


@router.get("/students/{user_id}/eligible-courses", response_model=EligibleCoursesResponse)
async def get_student_eligible_courses(
    user_id: str,
    current_user: User = Depends(records_any),
    record_service: StudentRecordService = Depends(get_student_record_service),
):
    data = await record_service.get_eligible_courses(user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return data


@router.put("/records", response_model=RecordResponse)
async def upsert_record(
    payload: RecordUpsert,
    current_user: User = Depends(records_update),
    record_service: StudentRecordService = Depends(get_student_record_service),
):
    try:
        return await record_service.upsert(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/records/import", response_model=CsvImportResponse)
async def import_records(
    file: UploadFile = File(...),
    strict: bool = Query(default=False),
    create_users: bool = Query(default=False),
    current_user: User = Depends(records_update),
    record_service: StudentRecordService = Depends(get_student_record_service),
):
    raw = await file.read()
    try:
        result = await record_service.import_csv(raw, strict=strict, create_users=create_users)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if strict and result.get("errors"):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    record_id: str,
    current_user: User = Depends(records_update),
    record_service: StudentRecordService = Depends(get_student_record_service),
):
    deleted = await record_service.delete_record(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")


@router.get("/materials", response_model=List[MaterialResponse])
async def list_materials(
    course_id: Optional[str] = None,
    material_type: Optional[str] = None,
    current_user: User = Depends(materials_view),
    material_service: LearningMaterialService = Depends(get_learning_material_service),
):
    return await material_service.list_materials(course_id=course_id, material_type=material_type)


@router.post("/materials", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def bind_material(
    payload: MaterialCreate,
    current_user: User = Depends(materials_manage),
    material_service: LearningMaterialService = Depends(get_learning_material_service),
):
    try:
        return await material_service.bind_material(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/materials/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: str,
    payload: MaterialUpdate,
    current_user: User = Depends(materials_manage),
    material_service: LearningMaterialService = Depends(get_learning_material_service),
):
    try:
        material = await material_service.update_material(material_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.delete("/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: str,
    current_user: User = Depends(materials_manage),
    material_service: LearningMaterialService = Depends(get_learning_material_service),
):
    deleted = await material_service.delete_material(material_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Material not found")
