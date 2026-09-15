'use client';

import React, { useEffect, useState } from 'react';
import { Card, Table, Tag, Typography, Alert, Empty, Spin } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import AuthGuard from '@/components/Auth/AuthGuard';
import academicService, { EligibleCourse } from '@/services/academicService';
import { CAREER_TRACK_LABELS } from '@/services/courseService';
import { AxiosError } from 'axios';

const { Title, Text } = Typography;

function EligibleCoursesPage() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [studentCode, setStudentCode] = useState<string | null>(null);
    const [courses, setCourses] = useState<EligibleCourse[]>([]);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await academicService.getMyEligibleCourses();
                setCourses(data.courses || []);
                setStudentCode(data.student_code || null);
            } catch (err: unknown) {
                const axiosErr = err as AxiosError<{ detail?: string }>;
                setError(axiosErr.response?.data?.detail || 'Không tải được danh sách môn đủ điều kiện.');
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    const columns: ColumnsType<EligibleCourse> = [
        {
            title: 'Mã môn',
            dataIndex: 'course_code',
            key: 'course_code',
            render: (code: string) => <Text strong>{code}</Text>,
        },
        {
            title: 'Tên môn',
            dataIndex: 'course_name',
            key: 'course_name',
        },
        {
            title: 'TC',
            dataIndex: 'credits',
            key: 'credits',
            width: 72,
        },
        {
            title: 'HK',
            dataIndex: 'semester',
            key: 'semester',
            width: 72,
            render: (sem?: number | null) => sem ?? '—',
        },
        {
            title: 'Lộ trình',
            dataIndex: 'career_track',
            key: 'career_track',
            render: (track?: string | null) => CAREER_TRACK_LABELS[track || ''] || track || '—',
        },
        {
            title: 'Ghi chú',
            key: 'notes',
            render: (_, record) => (
                <div className="flex flex-wrap gap-1">
                    {record.recommended_previous?.map((code) => (
                        <Tag key={code} color="gold">
                            PREVIOUS {code}
                        </Tag>
                    ))}
                    {record.missing_prereq_codes?.map((code) => (
                        <Tag key={code} color="red">
                            Thiếu {code}
                        </Tag>
                    ))}
                    {!record.recommended_previous?.length && !record.missing_prereq_codes?.length && (
                        <Tag color="green">Đủ ĐK</Tag>
                    )}
                </div>
            ),
        },
    ];

    return (
        <AuthGuard requiredRole="student">
            <div className="h-full overflow-auto p-4 md:p-6">
                <div className="max-w-6xl mx-auto">
                    <Title level={3} className="!mb-1">Môn đủ điều kiện</Title>
                    <Text type="secondary">
                        Các môn bạn có thể đăng ký dựa trên bảng điểm hiện tại
                        {studentCode ? ` · ${studentCode}` : ''}.
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
                                rowKey="course_id"
                                columns={columns}
                                dataSource={courses}
                                pagination={false}
                                locale={{
                                    emptyText: (
                                        <Empty description="Chưa có môn đủ điều kiện" />
                                    ),
                                }}
                            />
                        )}
                    </Card>
                    <Text type="secondary" className="block mt-3 text-xs">
                        Huy hiệu PREVIOUS là gợi ý môn trước (mềm), không chặn đăng ký.
                    </Text>
                </div>
            </div>
        </AuthGuard>
    );
}

export default EligibleCoursesPage;
