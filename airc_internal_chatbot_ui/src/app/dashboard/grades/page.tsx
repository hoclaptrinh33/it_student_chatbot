'use client';

import React, { useCallback, useEffect, useMemo, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import {
    Avatar,
    Breadcrumb,
    Button,
    Card,
    Col,
    Form,
    Input,
    InputNumber,
    Modal,
    notification,
    Row,
    Select,
    Space,
    Spin,
    Switch,
    Table,
    Tabs,
    Tag,
    Tooltip,
    Typography,
    Upload,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
    FormOutlined,
    SearchOutlined,
    DownloadOutlined,
    EditOutlined,
    WarningOutlined,
    CheckCircleOutlined,
    BookOutlined,
    CheckOutlined,
    FileExcelOutlined,
} from '@ant-design/icons';
import { AxiosError } from 'axios';
import AuthGuard from '@/components/Auth/AuthGuard';
import academicService, {
    AcademicRecord,
    RECORD_STATUS_LABELS,
    Transcript,
    EligibleCourse,
} from '@/services/academicService';
import courseService, { Course } from '@/services/courseService';
import { authService, User } from '@/services/authService';
import useAuthStore from '@/stores/authStore';

const { Title, Text, Paragraph } = Typography;

const STATUS_COLOR: Record<string, string> = {
    PASSED: 'success',
    FAILED: 'error',
    IN_PROGRESS: 'processing',
};

function axiosDetail(err: unknown, fallback: string): string {
    const axiosErr = err as AxiosError<{ detail?: string | Record<string, unknown> }>;
    const detail = axiosErr.response?.data?.detail;
    return typeof detail === 'string' ? detail : fallback;
}

function GradesContent() {
    const { token, user } = useAuthStore();
    const searchParams = useSearchParams();
    const initialStudentId = searchParams.get('student_id') || undefined;

    const [activeTab, setActiveTab] = useState('transcript');
    const [students, setStudents] = useState<User[]>([]);
    const [courses, setCourses] = useState<Course[]>([]);
    const [selectedUserId, setSelectedUserId] = useState<string | undefined>(initialStudentId);
    const [transcript, setTranscript] = useState<Transcript | null>(null);
    const [eligibleCourses, setEligibleCourses] = useState<EligibleCourse[]>([]);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [importing, setImporting] = useState(false);

    // Edit modal
    const [editModalVisible, setEditModalVisible] = useState(false);
    const [editingRecord, setEditingRecord] = useState<AcademicRecord | null>(null);
    const [editForm] = Form.useForm();

    // Single entry form
    const [singleEntryForm] = Form.useForm();

    // CSV Import options & result
    const [strictImport, setStrictImport] = useState(false);
    const [createUsersImport, setCreateUsersImport] = useState(false);
    const [importResult, setImportResult] = useState<{ imported: number; total: number; errors: { row: number; reason: string }[] } | null>(null);

    // Load courses
    useEffect(() => {
        courseService.listCourses().then(setCourses).catch(() => setCourses([]));
    }, []);

    // Load students
    useEffect(() => {
        if (!token) return;
        authService
            .getAllUsers(token, 'student')
            .then(setStudents)
            .catch(() => setStudents([]));
    }, [token]);

    // Load transcript & eligible courses
    const loadStudentData = useCallback(async (userId: string) => {
        setLoading(true);
        try {
            const [transData, eligData] = await Promise.all([
                academicService.getStudentTranscript(userId).catch(() => null),
                academicService.getStudentEligibleCourses(userId).catch(() => null),
            ]);
            setTranscript(transData);
            setEligibleCourses(eligData?.courses || []);
        } catch (err) {
            setTranscript(null);
            setEligibleCourses([]);
            notification.error({ message: axiosDetail(err, 'Không tải được dữ liệu học vụ của sinh viên') });
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (selectedUserId) {
            loadStudentData(selectedUserId);
        } else {
            setTranscript(null);
            setEligibleCourses([]);
        }
    }, [selectedUserId, loadStudentData]);

    // Selected student object
    const selectedStudent = useMemo(() => {
        return students.find((s) => s.id === selectedUserId);
    }, [students, selectedUserId]);

    // Academic stats of selected student
    const studentStats = useMemo(() => {
        if (!transcript?.records) return null;
        const recs = transcript.records;
        const passedRecs = recs.filter((r) => r.status === 'PASSED');
        const failedRecs = recs.filter((r) => r.status === 'FAILED');
        const inProgRecs = recs.filter((r) => r.status === 'IN_PROGRESS');

        const graded = recs.filter((r) => r.grade != null);
        const gpa = graded.length
            ? (graded.reduce((sum, r) => sum + (r.grade || 0), 0) / graded.length).toFixed(2)
            : '—';

        const totalCreditsPassed = passedRecs.reduce((sum, r) => sum + (r.credits || 0), 0);
        const totalCreditsFailed = failedRecs.reduce((sum, r) => sum + (r.credits || 0), 0);

        const isWarning = failedRecs.length >= 2 || (graded.length > 0 && Number(gpa) < 5.0);

        return {
            gpa,
            passedCount: passedRecs.length,
            failedCount: failedRecs.length,
            inProgCount: inProgRecs.length,
            totalCreditsPassed,
            totalCreditsFailed,
            isWarning,
        };
    }, [transcript]);

    // Handle single grade entry
    const handleSingleSubmit = async () => {
        const values = await singleEntryForm.validateFields();
        setSaving(true);
        try {
            await academicService.upsertRecord({
                user_id: values.user_id,
                course_code: values.course_code,
                status: values.status,
                grade: values.grade ?? null,
                semester_taken: values.semester_taken || null,
                attempt_count: values.attempt_count || 1,
            });
            notification.success({ message: 'Đã lưu điểm thành công!' });
            singleEntryForm.resetFields();
            if (values.user_id === selectedUserId) {
                await loadStudentData(values.user_id);
            }
        } catch (err) {
            notification.error({ message: axiosDetail(err, 'Không thể lưu điểm') });
        } finally {
            setSaving(false);
        }
    };

    // Open Edit record modal
    const openEditRecord = (record: AcademicRecord) => {
        setEditingRecord(record);
        editForm.setFieldsValue({
            course_code: record.course_code,
            status: record.status,
            grade: record.grade,
            semester_taken: record.semester_taken,
            attempt_count: record.attempt_count || 1,
        });
        setEditModalVisible(true);
    };

    // Save edited record
    const handleSaveEdit = async () => {
        if (!selectedUserId || !editingRecord) return;
        const values = await editForm.validateFields();
        setSaving(true);
        try {
            await academicService.upsertRecord({
                user_id: selectedUserId,
                course_code: editingRecord.course_code || values.course_code,
                status: values.status,
                grade: values.grade ?? null,
                semester_taken: values.semester_taken || null,
                attempt_count: values.attempt_count || 1,
            });
            notification.success({ message: 'Cập nhật điểm thành công!' });
            setEditModalVisible(false);
            await loadStudentData(selectedUserId);
        } catch (err) {
            notification.error({ message: axiosDetail(err, 'Không thể cập nhật điểm') });
        } finally {
            setSaving(false);
        }
    };

    // Download Sample CSV
    const handleDownloadSampleCsv = () => {
        const header = 'student_code,course_code,status,grade,semester_taken\n';
        const sampleRows = [
            '20240101,INT1101,PASSED,8.5,2024.1',
            '20240102,INT1101,FAILED,3.0,2024.1',
            'SV001,INT1203,FAILED,3.5,2023.2',
            'SV001,INT2104,IN_PROGRESS,,2024.1',
        ].join('\n');
        const blob = new Blob([header + sampleRows], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'bang_diem_mau_cntt.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Handle CSV Import
    const handleImportCsv = async (file: File) => {
        setImporting(true);
        setImportResult(null);
        try {
            const result = await academicService.importRecords(file, {
                strict: strictImport,
                create_users: createUsersImport,
            });
            setImportResult(result);
            if (result.errors.length === 0) {
                notification.success({
                    message: `Import thành công toàn bộ ${result.imported}/${result.total} bản ghi!`,
                });
            } else {
                notification.warning({
                    message: `Đã nhập ${result.imported}/${result.total} dòng, có ${result.errors.length} dòng lỗi.`,
                });
            }
            if (selectedUserId) await loadStudentData(selectedUserId);
        } catch (err) {
            notification.error({ message: axiosDetail(err, 'Không thể nhập tệp CSV') });
        } finally {
            setImporting(false);
        }
        return false;
    };

    // Columns for Transcript Table
    const transcriptColumns: ColumnsType<AcademicRecord> = [
        {
            title: 'Mã học phần',
            dataIndex: 'course_code',
            key: 'course_code',
            width: 130,
            render: (code: string) => <Tag color="blue" className="font-semibold">{code}</Tag>,
        },
        {
            title: 'Tên học phần',
            dataIndex: 'course_name',
            key: 'course_name',
            render: (name: string, record) => (
                <div>
                    <Text strong>{name || record.course_code}</Text>
                    {record.credits && (
                        <span className="text-xs text-gray-400 block">{record.credits} tín chỉ</span>
                    )}
                </div>
            ),
        },
        {
            title: 'Điểm số',
            dataIndex: 'grade',
            key: 'grade',
            width: 100,
            align: 'center',
            render: (g?: number | null) => {
                if (g == null) return <span className="text-gray-400">—</span>;
                const color = g >= 8.0 ? '#10b981' : g >= 5.0 ? '#3b82f6' : '#ef4444';
                return (
                    <span className="font-extrabold text-base" style={{ color }}>
                        {g.toFixed(1)}
                    </span>
                );
            },
        },
        {
            title: 'Trạng thái',
            dataIndex: 'status',
            key: 'status',
            width: 130,
            align: 'center',
            render: (status: string) => (
                <Tag color={STATUS_COLOR[status] || 'default'} className="font-medium px-2 py-0.5">
                    {RECORD_STATUS_LABELS[status] || status}
                </Tag>
            ),
        },
        {
            title: 'Học kỳ',
            dataIndex: 'semester_taken',
            key: 'semester_taken',
            width: 100,
            align: 'center',
            render: (sem?: string | null) => sem || '—',
        },
        {
            title: 'Lần học',
            dataIndex: 'attempt_count',
            key: 'attempt_count',
            width: 90,
            align: 'center',
            render: (att?: number) => (att && att > 1 ? <Tag color="orange">Lần {att}</Tag> : '1'),
        },
        {
            title: 'Thao tác',
            key: 'action',
            width: 90,
            align: 'center',
            render: (_, record) => (
                <Tooltip title="Chỉnh sửa điểm môn này">
                    <Button
                        size="small"
                        icon={<EditOutlined />}
                        onClick={() => openEditRecord(record)}
                        className="text-blue-600 hover:text-blue-800"
                    />
                </Tooltip>
            ),
        },
    ];

    // Filter student options
    const filteredStudentOptions = useMemo(() => {
        return students.map((s) => ({
            value: s.id,
            label: `${s.student_code ? `[${s.student_code}] ` : ''}${s.full_name} (${s.email})`,
        }));
    }, [students]);

    return (
        <div className="space-y-6 pb-12">
            {/* Breadcrumb & Title */}
            <div>
                <Breadcrumb
                    items={[
                        { title: 'Bảng điều khiển', href: '/dashboard' },
                        { title: user?.role === 'teacher' ? 'Cố vấn & Giảng viên' : 'Quản trị' },
                        { title: 'Quản lý điểm số & Cố vấn sinh viên' },
                    ]}
                />
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-3">
                    <div>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md">
                                <FormOutlined style={{ fontSize: 20 }} />
                            </div>
                            <div>
                                <Title level={3} className="!mb-0">
                                    Quản lý Điểm số & Cố vấn Sinh viên
                                </Title>
                                <Text type="secondary" className="text-sm">
                                    Tra cứu bảng điểm, xem cảnh báo học tập, tư vấn môn đủ điều kiện, nhập điểm đơn lẻ và import CSV.
                                </Text>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <Button
                            icon={<DownloadOutlined />}
                            onClick={handleDownloadSampleCsv}
                            className="font-medium"
                        >
                            Tải CSV mẫu
                        </Button>
                    </div>
                </div>
            </div>

            {/* Main Tabs */}
            <Card className="border-0 shadow-sm rounded-2xl p-2">
                <Tabs
                    activeKey={activeTab}
                    onChange={setActiveTab}
                    size="large"
                    items={[
                        {
                            key: 'transcript',
                            label: (
                                <Space>
                                    <SearchOutlined />
                                    <span>Tra cứu Bảng điểm & Cố vấn</span>
                                </Space>
                            ),
                            children: (
                                <div className="space-y-6 pt-2">
                                    {/* Student Selector Bar */}
                                    <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-4 md:p-6">
                                        <Row gutter={[16, 16]} align="middle">
                                            <Col xs={24} md={16}>
                                                <Text strong className="block mb-2 text-gray-700">
                                                    Chọn sinh viên cần xem bảng điểm & cố vấn học tập:
                                                </Text>
                                                <Select
                                                    showSearch
                                                    allowClear
                                                    size="large"
                                                    placeholder="Nhập tên hoặc MSSV (VD: SV001, 20240101, Lê Hải Đăng...)"
                                                    className="w-full"
                                                    optionFilterProp="label"
                                                    value={selectedUserId}
                                                    onChange={setSelectedUserId}
                                                    options={filteredStudentOptions}
                                                />
                                            </Col>
                                            <Col xs={24} md={8} className="flex sm:justify-end items-end">
                                                <Button
                                                    type="dashed"
                                                    onClick={() => {
                                                        setActiveTab('single');
                                                        if (selectedUserId) {
                                                            singleEntryForm.setFieldValue('user_id', selectedUserId);
                                                        }
                                                    }}
                                                    icon={<EditOutlined />}
                                                    className="w-full sm:w-auto"
                                                >
                                                    Nhập điểm mới cho SV này
                                                </Button>
                                            </Col>
                                        </Row>
                                    </div>

                                    {/* Student Info Card & Stats */}
                                    {loading ? (
                                        <div className="text-center py-16">
                                            <Spin size="large" />
                                            <div className="mt-3 text-sm text-gray-400">Đang tải hồ sơ học vụ sinh viên...</div>
                                        </div>
                                    ) : selectedStudent && studentStats ? (
                                        <div className="space-y-6">
                                            {/* Student Banner */}
                                            <div className="bg-linear-to-r from-blue-50/50 via-indigo-50/30 to-white border border-blue-100 rounded-2xl p-5">
                                                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                                                    <div className="flex items-center gap-4">
                                                        <Avatar
                                                            size={56}
                                                            style={{ backgroundColor: '#0F4C81', fontSize: 20, fontWeight: 700 }}
                                                        >
                                                            {selectedStudent.full_name?.charAt(0) || 'S'}
                                                        </Avatar>
                                                        <div>
                                                            <div className="flex items-center gap-2">
                                                                <Title level={4} className="!mb-0">
                                                                    {selectedStudent.full_name}
                                                                </Title>
                                                                {studentStats.isWarning ? (
                                                                    <Tag color="error" icon={<WarningOutlined />} className="font-semibold">
                                                                        Cảnh báo học tập
                                                                    </Tag>
                                                                ) : (
                                                                    <Tag color="success" icon={<CheckCircleOutlined />} className="font-semibold">
                                                                        Tiến độ tốt
                                                                    </Tag>
                                                                )}
                                                            </div>
                                                            <div className="text-sm text-gray-500 mt-0.5">
                                                                MSSV: <Text strong>{selectedStudent.student_code || 'Chưa cập nhật'}</Text> · Email: <Text>{selectedStudent.email}</Text>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* KPI Numbers */}
                                                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                                                        <div className="bg-white px-3 py-2 rounded-xl border border-gray-100 shadow-2xs">
                                                            <div className="text-xs text-gray-400">Điểm TB (GPA)</div>
                                                            <div className="text-xl font-black text-blue-600">{studentStats.gpa}</div>
                                                        </div>
                                                        <div className="bg-white px-3 py-2 rounded-xl border border-gray-100 shadow-2xs">
                                                            <div className="text-xs text-gray-400">TC Tích lũy</div>
                                                            <div className="text-xl font-black text-emerald-600">{studentStats.totalCreditsPassed}</div>
                                                        </div>
                                                        <div className="bg-white px-3 py-2 rounded-xl border border-gray-100 shadow-2xs">
                                                            <div className="text-xs text-gray-400">Môn nợ / rớt</div>
                                                            <div className="text-xl font-black text-red-500">{studentStats.failedCount}</div>
                                                        </div>
                                                        <div className="bg-white px-3 py-2 rounded-xl border border-gray-100 shadow-2xs">
                                                            <div className="text-xs text-gray-400">Đang học</div>
                                                            <div className="text-xl font-black text-indigo-500">{studentStats.inProgCount}</div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Transcript Records Table */}
                                            <Card
                                                title={
                                                    <div className="flex items-center justify-between">
                                                        <Space>
                                                            <BookOutlined className="text-blue-600" />
                                                            <span className="font-bold">Bảng điểm các học phần đã học</span>
                                                        </Space>
                                                        <Tag color="blue">{transcript?.records?.length || 0} học phần</Tag>
                                                    </div>
                                                }
                                                className="border border-gray-200/80 rounded-2xl shadow-none"
                                            >
                                                <Table
                                                    columns={transcriptColumns}
                                                    dataSource={transcript?.records || []}
                                                    rowKey="id"
                                                    pagination={false}
                                                    locale={{ emptyText: 'Sinh viên chưa có điểm học phần nào.' }}
                                                />
                                            </Card>

                                            {/* Eligible Courses for Advising */}
                                            <Card
                                                title={
                                                    <Space>
                                                        <CheckOutlined className="text-emerald-600" />
                                                        <span className="font-bold">Học phần đủ điều kiện đăng ký kỳ tới (Cố vấn lộ trình)</span>
                                                    </Space>
                                                }
                                                className="border border-emerald-100 bg-emerald-50/20 rounded-2xl shadow-none"
                                            >
                                                {eligibleCourses.length === 0 ? (
                                                    <Text type="secondary" className="text-sm">
                                                        Chưa có gợi ý học phần hoặc sinh viên đã hoàn thành tất cả môn đủ điều kiện.
                                                    </Text>
                                                ) : (
                                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                                        {eligibleCourses.map((c) => (
                                                            <div
                                                                key={c.course_id}
                                                                className="bg-white p-3.5 rounded-xl border border-emerald-200/60 shadow-2xs flex flex-col justify-between"
                                                            >
                                                                <div>
                                                                    <div className="flex items-center justify-between gap-2 mb-1">
                                                                        <Tag color="cyan" className="font-bold">
                                                                            {c.course_code}
                                                                        </Tag>
                                                                        {c.is_mandatory && (
                                                                            <Tag color="gold" className="text-xs">Bắt buộc</Tag>
                                                                        )}
                                                                    </div>
                                                                    <div className="font-bold text-gray-800 text-sm">
                                                                        {c.course_name}
                                                                    </div>
                                                                    <div className="text-xs text-gray-500 mt-1">
                                                                        {c.credits ? `${c.credits} tín chỉ` : ''} · Kỳ đề xuất: {c.semester || '—'}
                                                                    </div>
                                                                </div>

                                                                {c.recommended_previous?.length > 0 && (
                                                                    <div className="mt-2 text-2xs text-gray-400 border-t border-gray-100 pt-1.5">
                                                                        Môn học trước khuyên dùng: {c.recommended_previous.join(', ')}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}
                                            </Card>
                                        </div>
                                    ) : (
                                        <div className="text-center py-16 text-gray-400 border border-dashed rounded-2xl">
                                            <SearchOutlined style={{ fontSize: 36, color: '#cbd5e1' }} />
                                            <div className="mt-2 font-medium">Vui lòng chọn một sinh viên ở trên để xem bảng điểm và cố vấn.</div>
                                        </div>
                                    )}
                                </div>
                            ),
                        },
                        {
                            key: 'single',
                            label: (
                                <Space>
                                    <EditOutlined />
                                    <span>Nhập điểm đơn lẻ</span>
                                </Space>
                            ),
                            children: (
                                <div className="max-w-2xl mx-auto py-6">
                                    <Card
                                        title={<span className="font-bold">Nhập hoặc Cập nhật điểm cho một sinh viên</span>}
                                        className="border border-gray-200/80 rounded-2xl"
                                    >
                                        <Form
                                            form={singleEntryForm}
                                            layout="vertical"
                                            onFinish={handleSingleSubmit}
                                            initialValues={{
                                                status: 'PASSED',
                                                attempt_count: 1,
                                            }}
                                        >
                                            <Form.Item
                                                name="user_id"
                                                label="Chọn sinh viên"
                                                rules={[{ required: true, message: 'Vui lòng chọn sinh viên' }]}
                                            >
                                                <Select
                                                    showSearch
                                                    placeholder="Tìm kiếm theo MSSV hoặc họ tên"
                                                    optionFilterProp="label"
                                                    options={filteredStudentOptions}
                                                    size="large"
                                                />
                                            </Form.Item>

                                            <Form.Item
                                                name="course_code"
                                                label="Chọn học phần"
                                                rules={[{ required: true, message: 'Vui lòng chọn môn học' }]}
                                            >
                                                <Select
                                                    showSearch
                                                    placeholder="Chọn môn học (VD: INT1101 - Nhập môn lập trình)"
                                                    optionFilterProp="label"
                                                    size="large"
                                                    options={courses.map((c) => ({
                                                        value: c.course_code,
                                                        label: `${c.course_code} · ${c.course_name} (${c.credits || 3} TC)`,
                                                    }))}
                                                />
                                            </Form.Item>

                                            <Row gutter={16}>
                                                <Col span={12}>
                                                    <Form.Item
                                                        name="status"
                                                        label="Trạng thái"
                                                        rules={[{ required: true }]}
                                                    >
                                                        <Select size="large">
                                                            <Select.Option value="PASSED">Đạt (PASSED)</Select.Option>
                                                            <Select.Option value="FAILED">Không đạt (FAILED)</Select.Option>
                                                            <Select.Option value="IN_PROGRESS">Đang học (IN_PROGRESS)</Select.Option>
                                                        </Select>
                                                    </Form.Item>
                                                </Col>
                                                <Col span={12}>
                                                    <Form.Item
                                                        name="grade"
                                                        label="Điểm số (Thang 10)"
                                                        rules={[
                                                            {
                                                                type: 'number',
                                                                min: 0,
                                                                max: 10,
                                                                message: 'Điểm từ 0 đến 10',
                                                            },
                                                        ]}
                                                    >
                                                        <InputNumber
                                                            step={0.1}
                                                            precision={1}
                                                            className="w-full"
                                                            size="large"
                                                            placeholder="VD: 8.5"
                                                        />
                                                    </Form.Item>
                                                </Col>
                                            </Row>

                                            <Row gutter={16}>
                                                <Col span={12}>
                                                    <Form.Item
                                                        name="semester_taken"
                                                        label="Học kỳ"
                                                    >
                                                        <Input size="large" placeholder="VD: 2024.1 hoặc 2024.2" />
                                                    </Form.Item>
                                                </Col>
                                                <Col span={12}>
                                                    <Form.Item
                                                        name="attempt_count"
                                                        label="Lần học"
                                                    >
                                                        <InputNumber min={1} max={5} className="w-full" size="large" />
                                                    </Form.Item>
                                                </Col>
                                            </Row>

                                            <div className="flex justify-end gap-3 mt-4">
                                                <Button size="large" onClick={() => singleEntryForm.resetFields()}>
                                                    Làm mới
                                                </Button>
                                                <Button
                                                    type="primary"
                                                    htmlType="submit"
                                                    size="large"
                                                    loading={saving}
                                                    className="!bg-[#0F4C81] font-semibold"
                                                >
                                                    Lưu điểm học phần
                                                </Button>
                                            </div>
                                        </Form>
                                    </Card>
                                </div>
                            ),
                        },
                        {
                            key: 'import',
                            label: (
                                <Space>
                                    <FileExcelOutlined />
                                    <span>Import CSV hàng loạt</span>
                                </Space>
                            ),
                            children: (
                                <div className="max-w-3xl mx-auto py-6 space-y-6">
                                    <Card
                                        title={<span className="font-bold">Tải lên bảng điểm hàng loạt từ tệp CSV</span>}
                                        extra={
                                            <Button
                                                type="primary"
                                                icon={<DownloadOutlined />}
                                                onClick={handleDownloadSampleCsv}
                                                ghost
                                            >
                                                Tải file CSV mẫu
                                            </Button>
                                        }
                                        className="border border-gray-200/80 rounded-2xl"
                                    >
                                        <div className="mb-4">
                                            <Paragraph type="secondary" className="text-sm">
                                                Định dạng tệp yêu cầu có dòng tiêu đề chuẩn:
                                                <br />
                                                <Text code className="text-blue-700 font-semibold mt-1 inline-block">
                                                    student_code,course_code,status,grade,semester_taken
                                                </Text>
                                            </Paragraph>
                                        </div>

                                        <Row gutter={16} className="mb-4">
                                            <Col span={12}>
                                                <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-xl border border-gray-200">
                                                    <Switch checked={strictImport} onChange={setStrictImport} />
                                                    <div>
                                                        <div className="font-semibold text-xs text-gray-800">Strict Mode (Nghiêm ngặt)</div>
                                                        <div className="text-2xs text-gray-400">Dừng import nếu có dòng lỗi</div>
                                                    </div>
                                                </div>
                                            </Col>
                                            <Col span={12}>
                                                <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-xl border border-gray-200">
                                                    <Switch checked={createUsersImport} onChange={setCreateUsersImport} />
                                                    <div>
                                                        <div className="font-semibold text-xs text-gray-800">Tạo SV mới nếu chưa có</div>
                                                        <div className="text-2xs text-gray-400">Tự động khởi tạo user sinh viên</div>
                                                    </div>
                                                </div>
                                            </Col>
                                        </Row>

                                        <Upload.Dragger
                                            accept=".csv,text/csv"
                                            beforeUpload={handleImportCsv}
                                            showUploadList={false}
                                            disabled={importing}
                                            className="p-8 rounded-2xl border-2 border-dashed border-blue-300 hover:border-blue-500 bg-blue-50/20"
                                        >
                                            <p className="ant-upload-drag-icon">
                                                {importing ? <Spin size="large" /> : <FileExcelOutlined style={{ color: '#0F4C81', fontSize: 48 }} />}
                                            </p>
                                            <p className="ant-upload-text font-bold text-gray-800 text-base">
                                                Kéo thả tệp CSV vào đây hoặc bấm để chọn tệp
                                            </p>
                                            <p className="ant-upload-hint text-xs text-gray-500">
                                                Hỗ trợ tệp định dạng .csv chuẩn UTF-8
                                            </p>
                                        </Upload.Dragger>

                                        {importResult && (
                                            <div className="mt-6 p-4 rounded-xl border border-gray-200 bg-white">
                                                <div className="flex items-center justify-between mb-3">
                                                    <div className="font-bold text-base">Kết quả Import:</div>
                                                    <Tag color={importResult.errors.length === 0 ? 'success' : 'warning'}>
                                                        Thành công {importResult.imported}/{importResult.total} dòng
                                                    </Tag>
                                                </div>

                                                {importResult.errors.length > 0 && (
                                                    <div className="space-y-2 mt-3">
                                                        <Text type="danger" strong className="text-xs">
                                                            Chi tiết {importResult.errors.length} dòng lỗi:
                                                        </Text>
                                                        <div className="max-h-48 overflow-y-auto divide-y divide-red-100 bg-red-50/50 p-2 rounded-lg text-xs">
                                                            {importResult.errors.map((e, idx) => (
                                                                <div key={idx} className="py-1 text-red-700">
                                                                    Dòng <span className="font-bold">{e.row}</span>: {e.reason}
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </Card>
                                </div>
                            ),
                        },
                    ]}
                />
            </Card>

            {/* Quick Edit Modal */}
            <Modal
                title={`Cập nhật điểm môn ${editingRecord?.course_code || ''}`}
                open={editModalVisible}
                onCancel={() => setEditModalVisible(false)}
                onOk={handleSaveEdit}
                confirmLoading={saving}
                okText="Lưu thay đổi"
                cancelText="Hủy"
            >
                <Form form={editForm} layout="vertical" className="pt-2">
                    <Form.Item name="grade" label="Điểm số (Thang 10)">
                        <InputNumber min={0} max={10} step={0.1} precision={1} className="w-full" size="large" />
                    </Form.Item>
                    <Form.Item name="status" label="Trạng thái" rules={[{ required: true }]}>
                        <Select size="large">
                            <Select.Option value="PASSED">Đạt (PASSED)</Select.Option>
                            <Select.Option value="FAILED">Không đạt (FAILED)</Select.Option>
                            <Select.Option value="IN_PROGRESS">Đang học (IN_PROGRESS)</Select.Option>
                        </Select>
                    </Form.Item>
                    <Form.Item name="semester_taken" label="Học kỳ">
                        <Input size="large" placeholder="VD: 2024.1" />
                    </Form.Item>
                    <Form.Item name="attempt_count" label="Lần học">
                        <InputNumber min={1} max={5} className="w-full" size="large" />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
}

export default function TeacherGradesPage() {
    return (
        <AuthGuard requiredRole={['admin', 'teacher']}>
            <Suspense fallback={<div className="p-8 text-center"><Spin /></div>}>
                <GradesContent />
            </Suspense>
        </AuthGuard>
    );
}
