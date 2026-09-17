'use client';

import React, { useMemo, useState } from 'react';
import { Button, Collapse, Tag, Tooltip, Typography, message } from 'antd';
import { FilePdfOutlined, FileTextOutlined, LinkOutlined } from '@ant-design/icons';
import { DatasetSearchResult } from '@/core/entities/Chat';
import { coreClient } from '@/infrastructure/http/core.client';

interface SourceCitationsProps {
    sources?: DatasetSearchResult[];
}

interface SourceFileItem {
    fileId: string;
    fileName: string;
    datasetName?: string;
    score?: number;
    chunkCount: number;
}

async function openSourceFile(fileId: string, fileName?: string) {
    if (!fileId) {
        message.warning('Không tìm thấy mã tài liệu để mở.');
        return;
    }
    try {
        const response = await coreClient.get(`/files/${fileId}/view`, {
            responseType: 'blob',
        });
        const blob = new Blob([response.data], {
            type: response.headers['content-type'] || 'application/octet-stream',
        });
        const url = URL.createObjectURL(blob);
        const opened = window.open(url, '_blank', 'noopener,noreferrer');
        if (!opened) {
            const link = document.createElement('a');
            link.href = url;
            link.download = fileName || 'document';
            link.click();
        }
        setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (err: any) {
        console.error(err);
        if (err?.response?.status === 404) {
            message.warning('Tài liệu này hiện chưa có sẵn trên hệ thống.');
        } else {
            message.error('Không mở được tài liệu nguồn. Vui lòng kiểm tra quyền truy cập.');
        }
    }
}

export default function SourceCitations({ sources }: SourceCitationsProps) {
    const [opening, setOpening] = useState<string | null>(null);

    const uniqueFiles = useMemo(() => {
        const fileMap = new Map<string, SourceFileItem>();

        for (const group of sources || []) {
            for (const result of group.results || []) {
                const key = result.file_id || result.file_name;
                if (!key) continue;

                if (!fileMap.has(key)) {
                    fileMap.set(key, {
                        fileId: result.file_id,
                        fileName: result.file_name || 'Tài liệu tham khảo',
                        datasetName: group.dataset_name,
                        score: typeof result.score === 'number' ? result.score : undefined,
                        chunkCount: 1,
                    });
                } else {
                    const existing = fileMap.get(key)!;
                    existing.chunkCount += 1;
                    if (typeof result.score === 'number') {
                        existing.score = Math.max(existing.score ?? 0, result.score);
                    }
                }
            }
        }

        return Array.from(fileMap.values());
    }, [sources]);

    if (uniqueFiles.length === 0) return null;

    const handleFileClick = async (file: SourceFileItem) => {
        setOpening(file.fileId);
        await openSourceFile(file.fileId, file.fileName);
        setOpening(null);
    };

    return (
        <div className="mt-1 w-full max-w-xl">
            <Collapse
                size="small"
                ghost
                items={[
                    {
                        key: 'sources',
                        label: (
                            <span className="text-xs font-medium text-slate-500 hover:text-[#0F4C81] transition-colors flex items-center gap-1.5 select-none">
                                <LinkOutlined className="text-slate-400" />
                                <span>Tài liệu tham khảo ({uniqueFiles.length})</span>
                            </span>
                        ),
                        children: (
                            <div className="flex flex-col gap-1.5 pt-1">
                                {uniqueFiles.map((file) => {
                                    const isPdf = file.fileName.toLowerCase().endsWith('.pdf');
                                    const isOpeningThis = opening === file.fileId;

                                    return (
                                        <div
                                            key={file.fileId || file.fileName}
                                            onClick={() => handleFileClick(file)}
                                            className="group flex items-center justify-between gap-3 px-3 py-2 rounded-lg border border-slate-200/80 bg-slate-50/70 hover:bg-blue-50/50 hover:border-blue-200 transition-all cursor-pointer shadow-2xs"
                                        >
                                            <div className="flex items-center gap-2.5 min-w-0 flex-1">
                                                {isPdf ? (
                                                    <FilePdfOutlined className="text-rose-500 text-sm shrink-0" />
                                                ) : (
                                                    <FileTextOutlined className="text-[#0F4C81] text-sm shrink-0" />
                                                )}
                                                <span
                                                    className="text-xs font-medium text-slate-700 group-hover:text-[#0F4C81] group-hover:underline truncate select-none transition-colors"
                                                    title={file.fileName}
                                                >
                                                    {file.fileName}
                                                </span>
                                                {file.datasetName && (
                                                    <Tag className="m-0 text-[10px] text-slate-500 bg-white border-slate-200 shrink-0 hidden sm:inline-block">
                                                        {file.datasetName}
                                                    </Tag>
                                                )}
                                            </div>

                                            <div className="flex items-center gap-1 shrink-0">
                                                <Tooltip title="Mở tài liệu">
                                                    <Button
                                                        size="small"
                                                        type="text"
                                                        icon={<LinkOutlined className="text-slate-400 group-hover:text-[#0F4C81] transition-colors" />}
                                                        loading={isOpeningThis}
                                                        className="h-6 w-6 flex items-center justify-center p-0"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleFileClick(file);
                                                        }}
                                                    />
                                                </Tooltip>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        ),
                    },
                ]}
            />
        </div>
    );
}
