import { FileUploadResponse, FileInfo } from '@/services/fileService';

export interface FileUploadOptions {
    course_id?: string;
    material_type?: string;
}

export interface IFileRepository {
    uploadFile(file: File, options?: FileUploadOptions): Promise<FileUploadResponse>;
    getFiles(): Promise<FileInfo[]>;
    getFile(id: string): Promise<FileInfo>;
}
