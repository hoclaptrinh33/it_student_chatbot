import { coreClient } from '@/infrastructure/http/core.client';

export const RECORD_STATUSES = ['PASSED', 'FAILED', 'IN_PROGRESS'] as const;
export const MATERIAL_TYPES = ['SYLLABUS', 'SLIDE', 'TEXTBOOK', 'EXAM'] as const;

export type RecordStatus = (typeof RECORD_STATUSES)[number];
export type MaterialType = (typeof MATERIAL_TYPES)[number];

export interface AcademicRecord {
    id: string;
    user_id: string;
    course_id: string;
    course_code?: string | null;
    course_name?: string | null;
    credits?: number | null;
    status: string;
    grade?: number | null;
    semester_taken?: string | null;
    attempt_count?: number;
    recorded_at?: string | null;
}

export interface Transcript {
    user_id: string;
    student_code?: string | null;
    full_name?: string | null;
    records: AcademicRecord[];
}

export interface EligibleCourse {
    course_id: string;
    course_code: string;
    course_name: string;
    credits?: number | null;
    semester?: number | null;
    career_track?: string | null;
    is_mandatory?: boolean | null;
    missing_prereq_codes: string[];
    recommended_previous: string[];
}

export interface EligibleCourses {
    user_id: string;
    student_code?: string | null;
    courses: EligibleCourse[];
}

export interface RecordUpsertPayload {
    user_id: string;
    course_code: string;
    status: RecordStatus | string;
    grade?: number | null;
    semester_taken?: string | null;
    attempt_count?: number | null;
}

export interface CsvImportError {
    row: number;
    reason: string;
}

export interface CsvImportResult {
    imported: number;
    errors: CsvImportError[];
    total: number;
}

export interface LearningMaterial {
    id: string;
    course_id: string;
    title: string;
    material_type: string;
    file_url?: string | null;
    qdrant_point_id?: string | null;
    file_id?: string | null;
    dataset_id?: string | null;
    created_at?: string | null;
}

export const RECORD_STATUS_LABELS: Record<string, string> = {
    PASSED: 'Đạt',
    FAILED: 'Không đạt',
    IN_PROGRESS: 'Đang học',
};

export const MATERIAL_TYPE_LABELS: Record<string, string> = {
    SYLLABUS: 'Đề cương',
    SLIDE: 'Slide',
    TEXTBOOK: 'Giáo trình',
    EXAM: 'Đề thi',
};

export interface CreateMaterialPayload {
    course_id: string;
    title: string;
    material_type: MaterialType | string;
    file_url?: string | null;
    file_id?: string | null;
    dataset_id?: string | null;
}

export interface UpdateMaterialPayload {
    title?: string;
    course_id?: string;
    material_type?: MaterialType | string;
    file_url?: string | null;
    file_id?: string | null;
    dataset_id?: string | null;
}

const academicService = {
    getMyTranscript: async (): Promise<Transcript> => {
        const response = await coreClient.get<Transcript>('/academic/me/transcript');
        return response.data;
    },

    getMyEligibleCourses: async (): Promise<EligibleCourses> => {
        const response = await coreClient.get<EligibleCourses>('/academic/me/eligible-courses');
        return response.data;
    },

    getStudentTranscript: async (userId: string): Promise<Transcript> => {
        const response = await coreClient.get<Transcript>(`/academic/students/${userId}/transcript`);
        return response.data;
    },

    getStudentEligibleCourses: async (userId: string): Promise<EligibleCourses> => {
        const response = await coreClient.get<EligibleCourses>(`/academic/students/${userId}/eligible-courses`);
        return response.data;
    },

    upsertRecord: async (payload: RecordUpsertPayload): Promise<AcademicRecord> => {
        const response = await coreClient.put<AcademicRecord>('/academic/records', payload);
        return response.data;
    },

    importRecords: async (
        file: File,
        options?: { strict?: boolean; create_users?: boolean },
    ): Promise<CsvImportResult> => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await coreClient.post<CsvImportResult>('/academic/records/import', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            params: {
                strict: options?.strict ?? false,
                create_users: options?.create_users ?? false,
            },
        });
        return response.data;
    },

    deleteRecord: async (recordId: string): Promise<void> => {
        await coreClient.delete(`/academic/records/${recordId}`);
    },

    listMaterials: async (params?: {
        course_id?: string;
        material_type?: string;
    }): Promise<LearningMaterial[]> => {
        const response = await coreClient.get<LearningMaterial[]>('/academic/materials', { params });
        return response.data;
    },

    bindMaterial: async (payload: CreateMaterialPayload): Promise<LearningMaterial> => {
        const response = await coreClient.post<LearningMaterial>('/academic/materials', payload);
        return response.data;
    },

    updateMaterial: async (materialId: string, payload: UpdateMaterialPayload): Promise<LearningMaterial> => {
        const response = await coreClient.patch<LearningMaterial>(`/academic/materials/${materialId}`, payload);
        return response.data;
    },

    deleteMaterial: async (materialId: string): Promise<void> => {
        await coreClient.delete(`/academic/materials/${materialId}`);
    },
};

export default academicService;
