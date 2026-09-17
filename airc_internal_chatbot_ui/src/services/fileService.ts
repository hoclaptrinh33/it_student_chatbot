import { fileRepository } from '@/infrastructure/repositories/FileRepository';
import { coreClient } from '@/infrastructure/http/core.client';

// URL API Backend (Core Service) - NEXT_PUBLIC_API_URL = /api/v1
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface FileUploadResponse {
    id: string;
    name: string;
    size: number;
    mime_type: string;
    status: string;
    uploaded_at: string;
}

export interface FileInfo {
    id: string;
    name: string;
    size: number;
    mime_type: string;
    status: string;
    uploaded_at: string;
    processed_at?: string;
    error?: string;
}

/**
 * Service xử lý File Upload và Management
 */
const fileService = {
    /**
     * Upload file lên server
     */
    uploadFile: async (
        file: File,
        options?: { course_id?: string; material_type?: string },
    ): Promise<FileUploadResponse> => {
        return await fileRepository.uploadFile(file, options);
    },

    /**
     * Lấy danh sách files
     */
    getFiles: async (): Promise<FileInfo[]> => {
        try {
            const response = await fileRepository.getFiles();
            return Array.isArray(response) ? response : [];
        } catch (error) {
            console.error('getFiles error:', error);
            return [];
        }
    },

    /**
     * Lấy thông tin file
     */
    getFile: async (id: string): Promise<FileInfo> => {
        return await fileRepository.getFile(id);
    },

    /**
     * Get View File URL
     */
    viewFileUrl: (id: string): string => {
        return `${API_URL}/files/${id}/view`;
    },

    /**
     * Mở hoặc tải file an toàn có đính kèm Bearer token xác thực
     */
    openFileInBrowser: async (fileId: string, fileName?: string): Promise<void> => {
        const response = await coreClient.get(`/files/${fileId}/view`, {
            responseType: 'blob',
        });
        const contentType = response.headers['content-type'] || 'application/pdf';
        const blob = new Blob([response.data], { type: contentType });
        const url = URL.createObjectURL(blob);
        const opened = window.open(url, '_blank', 'noopener,noreferrer');
        if (!opened) {
            const link = document.createElement('a');
            link.href = url;
            link.download = fileName || 'document.pdf';
            link.click();
        }
        setTimeout(() => URL.revokeObjectURL(url), 60_000);
    },
};

export default fileService;
