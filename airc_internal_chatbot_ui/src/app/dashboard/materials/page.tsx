'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Card, Table, Tag, Typography, Alert, Empty, Spin, Select, Button } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { DownloadOutlined } from '@ant-design/icons';
import AuthGuard from '@/components/Auth/AuthGuard';
import academicService, {
    LearningMaterial,
    MATERIAL_TYPES,
    MATERIAL_TYPE_LABELS,
} from '@/services/academicService';
import courseService, { Course } from '@/services/courseService';
import { AxiosError } from 'axios';

const { Title, Text } = Typography;

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

function MaterialsPage() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [materials, setMaterials] = useState<LearningMaterial[]>([]);
    const [courses, setCourses] = useState<Course[]>([]);
    const [courseId, setCourseId] = useState<string | undefined>();
    const [materialType, setMaterialType] = useState<string | undefined>();

    const courseMap = useMemo(() => {
        const map = new Map<string, Course>();
        courses.forEach((c) => map.set(c.id, c));
        return map;
    }, [courses]);

    useEffect(() => {
        courseService.listCourses().then(setCourses).catch(() => setCourses([]));
    }, []);

    const load = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const mats = await academicService.listMaterials({
                course_id: courseId,
                material_type: materialType,
            });
            setMaterials(mats || []);
        } catch (err: unknown) {
            const axiosErr = err as AxiosError<{ detail?: string }>;
            setError(axiosErr.response?.data?.detail || 'Không tải được tài liệu học tập.');
        } finally {
            setLoading(false);
        }
    }, [courseId, materialType]);

    useEffect(() => {
        load();
    }, [load]);

    const openFile = (material: LearningMaterial) => {
        if (material.file_id) {
            window.open(`${API_URL}/files/${material.file_id}/view`, '_blank');
            return;
        }
        if (material.file_url) {
            window.open(material.file_url, '_blank');
        }
    };

    const columns: ColumnsType<LearningMaterial> = [
        {
            title: 'Tài liệu',
            dataIndex: 'title',
            key: 'title',
            render: (title: string) => <Text strong>{title}</Text>,
        },
        {
            title: 'Môn học',
            dataIndex: 'course_id',
            key: 'course_id',
            render: (id: string) => {
                const course = courseMap.get(id);
                return course ? `${course.course_code} · ${course.course_name}` : id;
            },
        },
        {
            title: 'Loại',
            dataIndex: 'material_type',
            key: 'material_type',
            render: (type: string) => (
                <Tag color="geekblue">{MATERIAL_TYPE_LABELS[type] || type}</Tag>
            ),
        },
        {
            title: 'Hành động',
            key: 'action',
            width: 120,
            render: (_, record) => (
                <Button
                    size="small"
                    icon={<DownloadOutlined />}
                    disabled={!record.file_id && !record.file_url}
                    onClick={() => openFile(record)}
                >
                    Mở
                </Button>
            ),
        },
    ];

    return (
        <AuthGuard requiredRole="student">
            <div className="h-full overflow-auto p-4 md:p-6">
                <div className="max-w-6xl mx-auto">
                    <Title level={3} className="!mb-1">Tài liệu học tập</Title>
                    <Text type="secondary">Lọc theo môn và loại tài liệu (đề cương, slide, giáo trình, đề thi).</Text>

                    <div className="flex flex-wrap gap-3 mt-4 mb-3">
                        <Select
                            allowClear
                            showSearch
                            placeholder="Tất cả môn"
                            className="min-w-[240px]"
                            optionFilterProp="label"
                            value={courseId}
                            onChange={(value) => setCourseId(value)}
                            options={courses.map((c) => ({
                                value: c.id,
                                label: `${c.course_code} · ${c.course_name}`,
                            }))}
                        />
                        <Select
                            allowClear
                            placeholder="Tất cả loại"
                            className="min-w-[180px]"
                            value={materialType}
                            onChange={(value) => setMaterialType(value)}
                            options={MATERIAL_TYPES.map((type) => ({
                                value: type,
                                label: MATERIAL_TYPE_LABELS[type],
                            }))}
                        />
                    </div>

                    <Card className="shadow-sm border-0" styles={{ body: { padding: 0 } }}>
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
                                dataSource={materials}
                                pagination={false}
                                locale={{
                                    emptyText: (
                                        <Empty description="Chưa có tài liệu phù hợp bộ lọc" />
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

export default MaterialsPage;
