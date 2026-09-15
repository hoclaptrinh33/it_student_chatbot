import { FileUploadOptions, IFileRepository } from '@/core/repositories/IFileRepository';
import { FileUploadResponse, FileInfo } from '@/services/fileService';
import { coreClient } from '@/infrastructure/http/core.client';

export const fileRepository: IFileRepository = {
    async uploadFile(file: File, options?: FileUploadOptions): Promise<FileUploadResponse> {
        const formData = new FormData();
        formData.append('file', file);
        if (options?.course_id) formData.append('course_id', options.course_id);
        if (options?.material_type) formData.append('material_type', options.material_type);

        const response = await coreClient.post<FileUploadResponse>('/files/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    async getFiles(): Promise<FileInfo[]> {
        const response = await coreClient.get<FileInfo[]>('/files/');
        return response.data;
    },

    async getFile(id: string): Promise<FileInfo> {
        const response = await coreClient.get<FileInfo>(`/files/${id}`);
        return response.data;
    },
};
