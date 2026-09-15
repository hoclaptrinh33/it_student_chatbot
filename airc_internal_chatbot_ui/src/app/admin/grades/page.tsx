'use client';

import React, { useCallback, useEffect, useState } from 'react';
import {
    Alert,
    Breadcrumb,
    Button,
    Card,
    Form,
    Input,
    InputNumber,
    Select,
    Table,
    Tag,
    Typography,
    Upload,
    notification,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { InboxOutlined, EditOutlined } from '@ant-design/icons';
import { AxiosError } from 'axios';
import AuthGuard from '@/components/Auth/AuthGuard';
import MainLayout from '@/components/Layout/MainLayout';
import academicService, {
    AcademicRecord,
    RECORD_STATUSES,
    RECORD_STATUS_LABELS,
    Transcript,
} from '@/services/academicService';
import courseService, { Course } from '@/services/courseService';
import { authService, User } from '@/services/authService';
import useAuthStore from '@/stores/authStore';

const { Title, Text, Paragraph } = Typography;

const STATUS_COLOR: Record<string, string> = {
    PASSED: 'green',
    FAILED: 'red',
    IN_PROGRESS: 'blue',
};

function axiosDetail(err: unknown, fallback: string): string {
    const axiosErr = err as AxiosError<{ detail?: string | Record<string, unknown> }>;
    const detail = axiosErr.response?.data?.detail;
    return typeof detail === 'string' ? detail : fallback;
}

export default function AdminGradesPage() {
    const { token, user } = useAuthStore();
    const [students, setStudents] = useState<User[]>([]);
    const [courses, setCourses] = useState<Course[]>([]);
    const [selectedUserId, setSelectedUserId] = useState<string | undefined>();
    const [manualUserId, setManualUserId] = useState('');
    const [transcript, setTranscript] = useState<Transcript | null>(null);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [importing, setImporting] = useState(false);
    const [form] = Form.useForm();

    const activeUserId = selectedUserId || manualUserId.trim() || undefined;

    useEffect(() => {
        courseService.listCourses().then(setCourses).catch(() => setCourses([]));
    }, []);

    useEffect(() => {
        if (!token) return;
        authService
            .getAllUsers(token, 'student')
            .then(setStudents)
            .catch(() => setStudents([]));
    }, [token]);

    const loadTranscript = useCallback(async (userId: string) => {
        setLoading(true);
        try {
            const data = await academicService.getStudentTranscript(userId);
            setTranscript(data);
        } catch (err) {
            setTranscript(null);
            notification.error({ message: axiosDetail(err, 'Không tải được bảng điểm sinh viên') });
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (activeUserId) {
            loadTranscript(activeUserId);
        } else {
            setTranscript(null);
        }
    }, [activeUserId, loadTranscript]);

    const handleUpsert = async () => {
        if (!activeUserId) {
            notification.warning({ message: 'Chọn hoặc nhập mã sinh viên trước' });
            return;
        }
        const values = await form.validateFields();
        setSaving(true);
        try {
            await academicService.upsertRecord({
                user_id: activeUserId,
                course_code: values.course_code,
                status: values.status,
                grade: values.grade ?? null,
                semester_taken: values.semester_taken || null,
                attempt_count: values.attempt_count || null,
            });
            notification.success({ message: 'Đã lưu điểm' });
            form.resetFields();
            await loadTranscript(activeUserId);
        } catch (err) {
            notification.error({ message: axiosDetail(err, 'Không lưu được điểm') });
        } finally {
            setSaving(false);
        }
    };

    const fillFromRecord = (record: AcademicRecord) => {
        form.setFieldsValue({
            course_code: record.course_code,
            status: record.status,
            grade: record.grade,
            semester_taken: record.semester_taken,
            attempt_count: record.attempt_count,
        });
    };

    const handleImport = async (file: File) => {
        setImporting(true);
        try {
            const result = await academicService.importRecords(file);
            notification.success({
                message: `Đã nhập ${result.imported}/${result.total} dòng`,
                description: result.errors.length
                    ? `${result.errors.length} dòng lỗi (không abort).`
                    : undefined,
            });
            if (result.errors.length) {
                notification.warning({
                    message: 'Một số dòng CSV lỗi',
                    description: result.errors
                        .slice(0, 5)
                        .map((e) => `Dòng ${e.row}: ${e.reason}`)
                        .join('\n'),
                });
            }
            if (activeUserId) await loadTranscript(activeUserId);
        } catch (err) {
            notification.error({ message: axiosDetail(err, 'Không nhập được CSV') });
        } finally {
            setImporting(false);
        }
        return false;
    };

    const columns: ColumnsType<AcademicRecord> = [
        { title: 'Mã', dataIndex: 'course_code', key: 'course_code' },
        { title: 'Tên môn', dataIndex: 'course_name', key: 'course_name' },
        {
            title: 'Điểm',
            dataIndex: 'grade',
            key: 'grade',
            render: (g?: number | null) => (g == null ? '—' : g.toFixed(2)),
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
        { title: 'HK', dataIndex: 'semester_taken', key: 'semester_taken' },
        {
            title: '',
            key: 'edit',
            width: 72,
            render: (_, record) => (
                <Button size="small" icon={<EditOutlined />} onClick={() => fillFromRecord(record)} />
            ),
        },
    ];

    return (
        <AuthGuard requiredRole={['admin', 'teacher']}>
            <MainLayout>
                <div className="mb-6">
                    <Breadcrumb
                        items={[
                            { title: 'Dashboard', href: '/dashboard' },
                            { title: user?.role === 'teacher' ? 'Giảng viên' : 'Admin' },
                            { title: 'Bảng điểm' },
                        ]}
                    />
                    <div className="flex items-center gap-3 mt-4">
                        <Title level={3} className="!mb-0">Nhập điểm sinh viên</Title>
                    </div>
                    <Text type="secondary">Nhập điểm một sinh viên hoặc import CSV. Sinh viên không thấy trang này.</Text>
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                    <Card title="Chọn sinh viên" bordered={false} className="shadow-sm">
                        {students.length > 0 ? (
                            <Select
                                showSearch
                                allowClear
                                className="w-full"
                                placeholder="Chọn sinh viên"
                                optionFilterProp="label"
                                value={selectedUserId}
                                onChange={(value) => {
                                    setSelectedUserId(value);
                                    setManualUserId('');
                                }}
                                options={students.map((s) => ({
                                    value: s.id,
                                    label: `${s.full_name} · ${s.student_code || s.email}`,
                                }))}
                            />
                        ) : (
                            <Alert
                                type="info"
                                showIcon
                                className="mb-3"
                                message="Không liệt kê được danh sách sinh viên"
                                description="Nhập UUID người dùng bên dưới, hoặc dùng CSV với cột student_code."
                            />
                        )}
                        <Input
                            className="mt-3"
                            placeholder="Hoặc dán user_id (UUID)"
                            value={manualUserId}
                            onChange={(e) => {
                                setManualUserId(e.target.value);
                                setSelectedUserId(undefined);
                            }}
                        />
                    </Card>

                    <Card title="Import CSV" bordered={false} className="shadow-sm">
                        <Paragraph type="secondary" className="!mb-2">
                            Cột: <Text code>student_code,course_code,status,grade,semester_taken</Text>
                        </Paragraph>
                        <Upload.Dragger
                            accept=".csv,text/csv"
                            maxCount={1}
                            showUploadList={false}
                            beforeUpload={(file) => {
                                handleImport(file);
                                return false;
                            }}
                            disabled={importing}
                        >
                            <p className="ant-upload-drag-icon">
                                <InboxOutlined />
                            </p>
                            <p className="ant-upload-text">
                                {importing ? 'Đang nhập...' : 'Kéo thả hoặc chọn file CSV'}
                            </p>
                            <p className="ant-upload-hint">Dòng lỗi không abort trừ khi API bật strict.</p>
                        </Upload.Dragger>
                    </Card>
                </div>

                <Card title="Nhập / cập nhật một môn" bordered={false} className="shadow-sm mt-4">
                    <Form form={form} layout="vertical">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
                            <Form.Item
                                name="course_code"
                                label="Môn học"
                                rules={[{ required: true, message: 'Chọn môn' }]}
                            >
                                <Select
                                    showSearch
                                    optionFilterProp="label"
                                    placeholder="Mã môn"
                                    options={courses.map((c) => ({
                                        value: c.course_code,
                                        label: `${c.course_code} · ${c.course_name}`,
                                    }))}
                                />
                            </Form.Item>
                            <Form.Item
                                name="status"
                                label="Trạng thái"
                                rules={[{ required: true, message: 'Chọn trạng thái' }]}
                            >
                                <Select
                                    options={RECORD_STATUSES.map((s) => ({
                                        value: s,
                                        label: RECORD_STATUS_LABELS[s],
                                    }))}
                                />
                            </Form.Item>
                            <Form.Item name="grade" label="Điểm (0–10)">
                                <InputNumber min={0} max={10} step={0.1} className="w-full" />
                            </Form.Item>
                            <Form.Item name="semester_taken" label="Học kỳ">
                                <Input placeholder="2025-1" />
                            </Form.Item>
                            <Form.Item name="attempt_count" label="Lần học">
                                <InputNumber min={1} className="w-full" />
                            </Form.Item>
                        </div>
                        <Button type="primary" loading={saving} onClick={handleUpsert}>
                            Lưu điểm
                        </Button>
                    </Form>
                </Card>

                <Card
                    title={
                        transcript
                            ? `Bảng điểm · ${transcript.full_name || ''} ${transcript.student_code || ''}`
                            : 'Bảng điểm sinh viên'
                    }
                    bordered={false}
                    className="shadow-sm mt-4"
                >
                    {!activeUserId ? (
                        <EmptyHint />
                    ) : (
                        <Table
                            rowKey="id"
                            loading={loading}
                            columns={columns}
                            dataSource={transcript?.records || []}
                            pagination={false}
                            locale={{ emptyText: 'chưa có bảng điểm' }}
                        />
                    )}
                </Card>
            </MainLayout>
        </AuthGuard>
    );
}

function EmptyHint() {
    return <Text type="secondary">Chọn một sinh viên để xem và sửa bảng điểm.</Text>;
}
