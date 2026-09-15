import { coreClient } from '@/infrastructure/http/core.client';

export const CAREER_TRACKS = ['GENERAL', 'AI', 'WEB', 'SECURITY', 'DATA', 'NETWORK', 'SOFTWARE'] as const;
export const RELATION_TYPES = ['PREREQUISITE', 'PREVIOUS', 'CO_REQUISITE'] as const;

export type CareerTrack = (typeof CAREER_TRACKS)[number];
export type RelationType = (typeof RELATION_TYPES)[number];

export interface Course {
    id: string;
    course_code: string;
    course_name: string;
    credits: number;
    theory_hours?: number;
    practice_hours?: number;
    semester?: number | null;
    is_mandatory?: boolean;
    career_track?: string;
    description?: string | null;
    created_at?: string;
    updated_at?: string;
}

export interface CourseCreatePayload {
    course_code: string;
    course_name: string;
    credits: number;
    theory_hours?: number;
    practice_hours?: number;
    semester?: number | null;
    is_mandatory?: boolean;
    career_track?: string;
    description?: string | null;
}

export type CourseUpdatePayload = Partial<CourseCreatePayload>;

export interface PrerequisiteEdge {
    id?: string;
    course_id?: string;
    prerequisite_course_id?: string;
    course_code?: string;
    course_name?: string;
    prerequisite_code?: string;
    prerequisite_name?: string;
    relation_type: string;
    depth?: number;
}

export interface CoursePrerequisites {
    course_id: string;
    course_code: string;
    course_name: string;
    hard: PrerequisiteEdge[];
    soft: PrerequisiteEdge[];
    closure: PrerequisiteEdge[];
    blocked_reason?: string | null;
}

export interface PrerequisiteCreatePayload {
    prerequisite_course_id: string;
    relation_type?: RelationType | string;
}

export interface CourseListParams {
    semester?: number;
    career_track?: string;
    q?: string;
    code?: string;
}

export const CAREER_TRACK_LABELS: Record<string, string> = {
    GENERAL: 'Chung',
    AI: 'AI',
    WEB: 'Web',
    SECURITY: 'An ninh',
    DATA: 'Dữ liệu',
    NETWORK: 'Mạng',
    SOFTWARE: 'Phần mềm',
};

export const RELATION_TYPE_LABELS: Record<string, string> = {
    PREREQUISITE: 'Tiên quyết (cứng)',
    PREVIOUS: 'Môn trước (mềm)',
    CO_REQUISITE: 'Song hành',
};

const courseService = {
    listCourses: async (params?: CourseListParams): Promise<Course[]> => {
        const response = await coreClient.get<Course[]>('/courses', { params });
        return response.data;
    },

    getCourse: async (courseId: string, code?: string): Promise<Course> => {
        const response = await coreClient.get<Course>(`/courses/${courseId}`, {
            params: code ? { code } : undefined,
        });
        return response.data;
    },

    createCourse: async (payload: CourseCreatePayload): Promise<Course> => {
        const response = await coreClient.post<Course>('/courses', payload);
        return response.data;
    },

    updateCourse: async (courseId: string, payload: CourseUpdatePayload): Promise<Course> => {
        const response = await coreClient.patch<Course>(`/courses/${courseId}`, payload);
        return response.data;
    },

    deleteCourse: async (courseId: string): Promise<void> => {
        await coreClient.delete(`/courses/${courseId}`);
    },

    getPrerequisites: async (courseId: string): Promise<CoursePrerequisites> => {
        const response = await coreClient.get<CoursePrerequisites>(`/courses/${courseId}/prerequisites`);
        return response.data;
    },

    addPrerequisite: async (courseId: string, payload: PrerequisiteCreatePayload): Promise<PrerequisiteEdge> => {
        const response = await coreClient.post<PrerequisiteEdge>(`/courses/${courseId}/prerequisites`, payload);
        return response.data;
    },

    deletePrerequisite: async (courseId: string, prerequisiteCourseId: string): Promise<void> => {
        await coreClient.delete(`/courses/${courseId}/prerequisites/${prerequisiteCourseId}`);
    },
};

export default courseService;
