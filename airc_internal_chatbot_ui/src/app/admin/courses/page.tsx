'use client';

import React, { useCallback, useEffect, useState } from 'react';
import {
    Alert,
    Breadcrumb,
    Button,
    Card,
    Drawer,
    Form,
    Input,
    InputNumber,
    Modal,
    Popconfirm,
    Select,
    Space,
    Switch,
    Table,
    Tag,
    Typography,
    notification,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { BookOutlined, DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons';
import { AxiosError } from 'axios';
import AuthGuard from '@/components/Auth/AuthGuard';
import MainLayout from '@/components/Layout/MainLayout';
import courseService, {
    CAREER_TRACKS,
    CAREER_TRACK_LABELS,
    Course,
    CoursePrerequisites,
    PrerequisiteEdge,
    RELATION_TYPES,
    RELATION_TYPE_LABELS,
} from '@/services/courseService';

const { Title, Text } = Typography;

function axiosDetail(err: unknown, fallback: string): string {
    const axiosErr = err as AxiosError<{ detail?: string }>;
    const detail = axiosErr.response?.data?.detail;
    return typeof detail === 'string' ? detail : fallback;
}

export default function AdminCoursesPage() {
    const [courses, setCourses] = useState<Course[]>([]);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [editorOpen, setEditorOpen] = useState(false);
    const [editing, setEditing] = useState<Course | null>(null);
    const [form] = Form.useForm();

    const [prereqOpen, setPrereqOpen] = useState(false);
    const [prereqCourse, setPrereqCourse] = useState<Course | null>(null);
    const [prereqs, setPrereqs] = useState<CoursePrerequisites | null>(null);
    const [prereqLoading, setPrereqLoading] = useState(false);
    const [prereqForm] = Form.useForm();

    const fetchCourses = useCallback(async () => {
        setLoading(true);
        try {
            const data = await courseService.listCourses();
            setCourses(data);
        } catch (err) {
            notification.error({ message: axiosDetail(err, 'Không tải được danh sách môn học') });
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchCourses();
    }, [fetchCourses]);

    const openCreate = () => {
        setEditing(null);
        form.resetFields();
        form.setFieldsValue({
            credits: 3,
            theory_hours: 0,
            practice_hours: 0,
            is_mandatory: true,
            career_track: 'GENERAL',
        });
        setEditorOpen(true);
    };

    const openEdit = (course: Course) => {
        setEditing(course);
        form.setFieldsValue(course);
        setEditorOpen(true);
    };

    const handleSave = async () => {
        const values = await form.validateFields();
        setSaving(true);
        try {
            if (editing) {
                await courseService.updateCourse(editing.id, values);
                notification.success({ message: 'Đã cập nhật môn học' });
            } else {
                await courseService.createCourse(values);
                notification.success({ message: 'Đã tạo môn học' });
            }
            setEditorOpen(false);
            fetchCourses();
        } catch (err) {
            notification.error({ message: axiosDetail(err, 'Không lưu được môn học') });
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async (course: Course) => {
        try {
            await courseService.deleteCourse(course.id);
            notification.success({ message: `Đã xóa ${course.course_code}` });
            fetchCourses();
        } catch (err) {
            notification.error({
                message: axiosDetail(err, 'Không xóa được môn (có thể còn bảng điểm liên kết)'),
            });
        }
    };

    const openPrereqs = async (course: Course) => {
        setPrereqCourse(course);
        setPrereqOpen(true);
        setPrereqLoading(true);
        prereqForm.resetFields();
        try {
            const data = await courseService.getPrerequisites(course.id);
            setPrereqs(data);
        } catch (err) {
            notification.error({ message: axiosDetail(err, 'Không tải được tiên quyết') });
            setPrereqs(null);
        } finally {
            setPrereqLoading(false);
        }
    };

    const handleAddPrereq = async () => {
        if (!prereqCourse) return;
        const values = await prereqForm.validateFields();
        try {
            await courseService.addPrerequisite(prereqCourse.id, values);
            notification.success({ message: 'Đã thêm cạnh tiên quyết' });
            prereqForm.resetFields();
            const data = await courseService.getPrerequisites(prereqCourse.id);
            setPrereqs(data);
        } catch (err) {
            notification.error({ message: axiosDetail(err, 'Không thêm được tiên quyết') });
        }
    };

    const handleDeletePrereq = async (edge: PrerequisiteEdge) => {
        if (!prereqCourse || !edge.prerequisite_course_id) return;
        try {
            await courseService.deletePrerequisite(prereqCourse.id, edge.prerequisite_course_id);
            const data = await courseService.getPrerequisites(prereqCourse.id);
            setPrereqs(data);
        } catch (err) {
            notification.error({ message: axiosDetail(err, 'Không xóa được tiên quyết') });
        }
    };

    const columns: ColumnsType<Course> = [
        {
            title: 'Mã',
            dataIndex: 'course_code',
            key: 'course_code',
            render: (code: string) => <Text strong>{code}</Text>,
        },
        { title: 'Tên môn', dataIndex: 'course_name', key: 'course_name' },
        { title: 'TC', dataIndex: 'credits', key: 'credits', width: 64 },
        {
            title: 'HK',
            dataIndex: 'semester',
            key: 'semester',
            width: 64,
            render: (sem?: number | null) => sem ?? '—',
        },
        {
            title: 'Lộ trình',
            dataIndex: 'career_track',
            key: 'career_track',
            render: (track: string) => CAREER_TRACK_LABELS[track] || track,
        },
        {
            title: 'Bắt buộc',
            dataIndex: 'is_mandatory',
            key: 'is_mandatory',
            render: (v: boolean) => (v ? <Tag color="blue">Bắt buộc</Tag> : <Tag>Tự chọn</Tag>),
        },
        {
            title: 'Hành động',
            key: 'action',
            width: 280,
            render: (_, record) => (
                <Space>
                    <Button size="small" onClick={() => openPrereqs(record)}>
                        Tiên quyết
                    </Button>
                    <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
                    <Popconfirm
                        title="Xóa môn học?"
                        description="Không xóa được nếu còn bảng điểm liên kết."
                        okText="Xóa"
                        cancelText="Hủy"
                        okButtonProps={{ danger: true }}
                        onConfirm={() => handleDelete(record)}
                    >
                        <Button size="small" danger icon={<DeleteOutlined />} />
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    const prereqRows = [...(prereqs?.hard || []), ...(prereqs?.soft || [])];

    return (
        <AuthGuard requiredRole="admin">
            <MainLayout>
                <div className="mb-6">
                    <Breadcrumb
                        items={[
                            { title: 'Dashboard', href: '/dashboard' },
                            { title: 'Admin' },
                            { title: 'Môn học' },
                        ]}
                    />
                    <div className="flex justify-between items-center mt-4">
                        <div className="flex items-center gap-3">
                            <BookOutlined className="text-2xl" style={{ color: '#0F4C81' }} />
                            <Title level={3} className="!mb-0">Quản lý môn học</Title>
                        </div>
                        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
                            Thêm môn
                        </Button>
                    </div>
                </div>

                <Card bordered={false} className="shadow-sm rounded-lg">
                    <Table
                        rowKey="id"
                        loading={loading}
                        columns={columns}
                        dataSource={courses}
                        pagination={{ pageSize: 15 }}
                    />
                </Card>

                <Modal
                    title={editing ? `Sửa ${editing.course_code}` : 'Thêm môn học'}
                    open={editorOpen}
                    onCancel={() => setEditorOpen(false)}
                    onOk={handleSave}
                    confirmLoading={saving}
                    okText="Lưu"
                    cancelText="Hủy"
                    destroyOnHidden
                >
                    <Form form={form} layout="vertical">
                        <Form.Item
                            name="course_code"
                            label="Mã môn"
                            rules={[{ required: true, message: 'Nhập mã môn' }]}
                        >
                            <Input placeholder="INT2104" disabled={!!editing} />
                        </Form.Item>
                        <Form.Item
                            name="course_name"
                            label="Tên môn"
                            rules={[{ required: true, message: 'Nhập tên môn' }]}
                        >
                            <Input placeholder="Lập trình Web" />
                        </Form.Item>
                        <Space className="w-full" size="middle">
                            <Form.Item name="credits" label="Tín chỉ" rules={[{ required: true }]}>
                                <InputNumber min={1} className="w-full" />
                            </Form.Item>
                            <Form.Item name="semester" label="Học kỳ">
                                <InputNumber min={1} max={8} className="w-full" />
                            </Form.Item>
                        </Space>
                        <Space className="w-full" size="middle">
                            <Form.Item name="theory_hours" label="Giờ LT">
                                <InputNumber min={0} className="w-full" />
                            </Form.Item>
                            <Form.Item name="practice_hours" label="Giờ TH">
                                <InputNumber min={0} className="w-full" />
                            </Form.Item>
                        </Space>
                        <Form.Item name="career_track" label="Lộ trình">
                            <Select
                                options={CAREER_TRACKS.map((t) => ({
                                    value: t,
                                    label: CAREER_TRACK_LABELS[t],
                                }))}
                            />
                        </Form.Item>
                        <Form.Item name="is_mandatory" label="Bắt buộc" valuePropName="checked">
                            <Switch />
                        </Form.Item>
                        <Form.Item name="description" label="Mô tả">
                            <Input.TextArea rows={3} />
                        </Form.Item>
                    </Form>
                </Modal>

                <Drawer
                    title={prereqCourse ? `Tiên quyết · ${prereqCourse.course_code}` : 'Tiên quyết'}
                    open={prereqOpen}
                    onClose={() => setPrereqOpen(false)}
                    width={480}
                >
                    {prereqLoading ? (
                        <Alert type="info" message="Đang tải..." />
                    ) : (
                        <>
                            <Form form={prereqForm} layout="vertical">
                                <Form.Item
                                    name="prerequisite_course_id"
                                    label="Môn tiên quyết"
                                    rules={[{ required: true, message: 'Chọn môn' }]}
                                >
                                    <Select
                                        showSearch
                                        optionFilterProp="label"
                                        placeholder="Chọn môn"
                                        options={courses
                                            .filter((c) => c.id !== prereqCourse?.id)
                                            .map((c) => ({
                                                value: c.id,
                                                label: `${c.course_code} · ${c.course_name}`,
                                            }))}
                                    />
                                </Form.Item>
                                <Form.Item
                                    name="relation_type"
                                    label="Loại quan hệ"
                                    initialValue="PREREQUISITE"
                                    rules={[{ required: true }]}
                                >
                                    <Select
                                        options={RELATION_TYPES.map((t) => ({
                                            value: t,
                                            label: RELATION_TYPE_LABELS[t],
                                        }))}
                                    />
                                </Form.Item>
                                <Button type="primary" onClick={handleAddPrereq} className="mb-4">
                                    Thêm cạnh
                                </Button>
                            </Form>
                            <Table
                                size="small"
                                rowKey={(row) => `${row.prerequisite_course_id}-${row.relation_type}`}
                                pagination={false}
                                dataSource={prereqRows}
                                columns={[
                                    {
                                        title: 'Môn',
                                        render: (_, row) =>
                                            `${row.prerequisite_code || ''} ${row.prerequisite_name || ''}`.trim(),
                                    },
                                    {
                                        title: 'Loại',
                                        dataIndex: 'relation_type',
                                        render: (type: string) => (
                                            <Tag color={type === 'PREREQUISITE' ? 'red' : 'gold'}>
                                                {type}
                                            </Tag>
                                        ),
                                    },
                                    {
                                        title: '',
                                        width: 64,
                                        render: (_, row) => (
                                            <Button
                                                size="small"
                                                danger
                                                icon={<DeleteOutlined />}
                                                onClick={() => handleDeletePrereq(row)}
                                            />
                                        ),
                                    },
                                ]}
                            />
                        </>
                    )}
                </Drawer>
            </MainLayout>
        </AuthGuard>
    );
}
