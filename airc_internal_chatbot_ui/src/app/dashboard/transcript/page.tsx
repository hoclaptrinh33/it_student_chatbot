'use client';

import React, { useEffect, useState } from 'react';
import { Card, Table, Tag, Typography, Alert, Empty, Spin } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import AuthGuard from '@/components/Auth/AuthGuard';
import academicService, { AcademicRecord, RECORD_STATUS_LABELS } from '@/services/academicService';
import { AxiosError } from 'axios';

const { Title, Text } = Typography;

const STATUS_COLOR: Record<string, string> = {
    PASSED: 'green',
    FAILED: 'red',
    IN_PROGRESS: 'blue',
};

function TranscriptPage() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [studentLabel, setStudentLabel] = useState<string>('');
    const [records, setRecords] = useState<AcademicRecord[]>([]);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await academicService.getMyTranscript();
                setRecords(data.records || []);
                const parts = [data.full_name, data.student_code].filter(Boolean);
                setStudentLabel(parts.join(' · '));
            } catch (err: unknown) {
                const axiosErr = err as AxiosError<{ detail?: string }>;
                setError(axiosErr.response?.data?.detail || 'Không tải được bảng điểm.');
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    const columns: ColumnsType<AcademicRecord> = [
        {
            title: 'Mã môn',
            dataIndex: 'course_code',
            key: 'course_code',
            render: (code?: string | null) => <Text strong>{code || '—'}</Text>,
        },
        {
            title: 'Tên môn',
            dataIndex: 'course_name',
            key: 'course_name',
            render: (name?: string | null) => name || '—',
        },
        {
            title: 'TC',
            dataIndex: 'credits',
            key: 'credits',
            width: 72,
            render: (credits?: number | null) => credits ?? '—',
        },
        {
            title: 'Điểm',
            dataIndex: 'grade',
            key: 'grade',
            width: 88,
            render: (grade?: number | null) => (grade == null ? '—' : grade.toFixed(2)),
        },
        {
            title: 'Trạng thái',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => (
                <Tag color={STATUS_COLOR[status] || 'default'}>
                    {RECORD_STATUS_LABELS[status] || status}
                </Tag>
            ),
        },
        {
            title: 'Học kỳ',
            dataIndex: 'semester_taken',
            key: 'semester_taken',
            render: (sem?: string | null) => sem || '—',
        },
        {
            title: 'Lần học',
            dataIndex: 'attempt_count',
            key: 'attempt_count',
            width: 96,
            render: (n?: number) => n ?? 1,
        },
    ];

    return (
        <AuthGuard requiredRole="student">
            <div className="h-full overflow-auto p-4 md:p-6">
                <div className="max-w-6xl mx-auto">
                    <Title level={3} className="!mb-1">Bảng điểm</Title>
                    <Text type="secondary">
                        {studentLabel || 'Bảng điểm cá nhân theo hệ thống học vụ'}
                    </Text>

                    <Card className="mt-4 shadow-sm border-0" styles={{ body: { padding: 0 } }}>
                        {error && (
                            <Alert type="error" showIcon message={error} className="m-4" />
                        )}
                        {loading ? (
                            <div className="flex justify-center py-16">
                                <Spin />
                            </div>
                        ) : (
                            <Table
                                rowKey="id"
                                columns={columns}
                                dataSource={records}
                                pagination={false}
                                locale={{
                                    emptyText: (
                                        <Empty description="chưa có bảng điểm" />
                                    ),
                                }}
                            />
                        )}
                    </Card>
                </div>
            </div>
        </AuthGuard>
    );
}

export default TranscriptPage;
