'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import {
    Card,
    Row,
    Col,
    Typography,
    Space,
    Button,
    Tag,
    Spin,
    Avatar,
    Select,
} from 'antd';
import {
    BookOutlined,
    FolderOpenOutlined,
    DatabaseOutlined,
    TeamOutlined,
    FormOutlined,
    MessageOutlined,
    SearchOutlined,
    CheckCircleOutlined,
    WarningOutlined,
    RightOutlined,
    FileTextOutlined,
    ArrowRightOutlined,
    BulbOutlined,
} from '@ant-design/icons';
import useAuthStore from '@/stores/authStore';
import courseService, { Course } from '@/services/courseService';
import academicService, { LearningMaterial, Transcript, MATERIAL_TYPE_LABELS } from '@/services/academicService';
import datasetService, { Dataset } from '@/services/datasetService';
import { authService, User } from '@/services/authService';

const { Title, Text, Paragraph } = Typography;

export default function TeacherDashboard() {
    const router = useRouter();
    const { user, token } = useAuthStore();

    const [loading, setLoading] = useState(true);
    const [courses, setCourses] = useState<Course[]>([]);
    const [materials, setMaterials] = useState<LearningMaterial[]>([]);
    const [datasets, setDatasets] = useState<Dataset[]>([]);
    const [students, setStudents] = useState<User[]>([]);

    // Quick student search state
    const [selectedStudentId, setSelectedStudentId] = useState<string | null>(null);
    const [studentTranscript, setStudentTranscript] = useState<Transcript | null>(null);
    const [transcriptLoading, setTranscriptLoading] = useState(false);

    useEffect(() => {
        const loadDashboardData = async () => {
            setLoading(true);
            try {
                const [coursesData, materialsData, datasetsData] = await Promise.all([
                    courseService.listCourses().catch(() => [] as Course[]),
                    academicService.listMaterials().catch(() => [] as LearningMaterial[]),
                    datasetService.getDatasets().catch(() => [] as Dataset[]),
                ]);
                setCourses(coursesData);
                setMaterials(materialsData);
                setDatasets(datasetsData);

                if (token) {
                    const studentsData = await authService.getAllUsers(token, 'student').catch(() => [] as User[]);
                    setStudents(studentsData);
                }
            } catch (err) {
                console.error('Failed to load teacher dashboard data:', err);
            } finally {
                setLoading(false);
            }
        };

        loadDashboardData();
    }, [token]);

    // Load transcript when quick student is selected
    useEffect(() => {
        if (!selectedStudentId) {
            setStudentTranscript(null);
            return;
        }

        const fetchQuickTranscript = async () => {
            setTranscriptLoading(true);
            try {
                const data = await academicService.getStudentTranscript(selectedStudentId);
                setStudentTranscript(data);
            } catch (err) {
                console.error('Failed to load quick transcript:', err);
                setStudentTranscript(null);
            } finally {
                setTranscriptLoading(false);
            }
        };

        fetchQuickTranscript();
    }, [selectedStudentId]);

    // Map course ID to Course
    const courseMap = useMemo(() => {
        const map = new Map<string, Course>();
        courses.forEach((c) => map.set(c.id, c));
        return map;
    }, [courses]);

    // Selected student object
    const selectedStudent = useMemo(() => {
        return students.find((s) => s.id === selectedStudentId);
    }, [students, selectedStudentId]);

    // Summary stats for selected student
    const studentStats = useMemo(() => {
        if (!studentTranscript?.records) return null;
        const records = studentTranscript.records;
        const graded = records.filter((r) => r.grade != null);
        const avg = graded.length
            ? (graded.reduce((acc, r) => acc + (r.grade || 0), 0) / graded.length).toFixed(2)
            : '—';
        const passed = records.filter((r) => r.status === 'PASSED').length;
        const failed = records.filter((r) => r.status === 'FAILED').length;
        const inProgress = records.filter((r) => r.status === 'IN_PROGRESS').length;
        return { avg, passed, failed, inProgress, total: records.length };
    }, [studentTranscript]);

    const quickAIPrompts = [
        {
            title: 'Tư vấn lộ trình học',
            prompt: 'Tư vấn lộ trình đăng ký môn học tiếp theo cho sinh viên ngành Công nghệ Thông tin.',
        },
        {
            title: 'Tóm tắt chuẩn đầu ra',
            prompt: 'Tóm tắt các yêu cầu và chuẩn đầu ra của các môn học cơ sở ngành CNTT.',
        },
        {
            title: 'Ngân hàng câu hỏi ôn tập',
            prompt: 'Hãy tạo 5 câu hỏi trắc nghiệm kèm đáp án chi tiết về kiến trúc máy tính và pipeline.',
        },
    ];

    const handlePromptClick = (p: string) => {
        // Can route to chat with prompt stored or query param
        sessionStorage.setItem('pending_chat_prompt', p);
        router.push('/dashboard/chat');
    };

    return (
        <div className="space-y-6 pb-8">
            {/* Header Hero Banner */}
            <div
                className="rounded-2xl p-6 md:p-8 text-white relative overflow-hidden shadow-lg"
                style={{
                    background: 'linear-gradient(135deg, #0F4C81 0%, #1E3A8A 50%, #0D9488 100%)',
                }}
            >
                <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-2xl bg-white/10 backdrop-blur-md p-2 flex items-center justify-center border border-white/20 shadow-inner">
                            <Image
                                src="/logo_fit.png"
                                alt="Khoa CNTT"
                                width={56}
                                height={56}
                                className="object-contain"
                            />
                        </div>
                        <div>
                            <div className="flex items-center gap-2 flex-wrap mb-1">
                                <Title level={2} className="!text-white !mb-0 tracking-tight font-extrabold">
                                    Kính chào Thầy/Cô {user?.full_name || 'Giảng viên'}!
                                </Title>
                                <Tag color="cyan" className="font-semibold px-2 py-0.5 border-0">
                                    Giảng viên · Cố vấn học tập
                                </Tag>
                            </div>
                            <Text className="text-white/80 text-sm md:text-base">
                                Cổng thông tin đào tạo, quản lý học liệu và cố vấn học tập — Khoa Công nghệ Thông tin
                            </Text>
                        </div>
                    </div>

                    {/* Quick action buttons */}
                    <div className="flex items-center gap-2 flex-wrap">
                        <Button
                            type="primary"
                            icon={<FormOutlined />}
                            onClick={() => router.push('/dashboard/grades')}
                            className="!bg-white !text-[#0F4C81] !border-none font-semibold shadow hover:!bg-white/90"
                            size="large"
                        >
                            Quản lý Điểm & SV
                        </Button>
                        <Button
                            ghost
                            icon={<FolderOpenOutlined />}
                            onClick={() => router.push('/dashboard/materials')}
                            className="font-semibold text-white border-white/40 hover:!border-white hover:!text-white"
                            size="large"
                        >
                            Tài liệu môn học
                        </Button>
                        <Button
                            ghost
                            icon={<MessageOutlined />}
                            onClick={() => router.push('/dashboard/chat')}
                            className="font-semibold text-white border-white/40 hover:!border-white hover:!text-white"
                            size="large"
                        >
                            Trợ lý AI
                        </Button>
                    </div>
                </div>
            </div>

            {/* Key KPI Metrics Grid */}
            <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} lg={6}>
                    <Card
                        hoverable
                        className="border-0 shadow-sm rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-md cursor-pointer"
                        onClick={() => router.push('/dashboard/courses')}
                    >
                        <div className="flex items-center gap-4">
                            <div
                                className="w-12 h-12 rounded-xl flex items-center justify-center text-white"
                                style={{ background: 'linear-gradient(135deg, #0F4C81 0%, #2563EB 100%)' }}
                            >
                                <BookOutlined style={{ fontSize: 24 }} />
                            </div>
                            <div>
                                <Text type="secondary" className="text-xs uppercase tracking-wider font-semibold">
                                    Môn học Khoa CNTT
                                </Text>
                                <div className="text-2xl font-black text-gray-800">
                                    {loading ? <Spin size="small" /> : courses.length}
                                </div>
                                <Text className="text-xs text-blue-600 font-medium flex items-center gap-1 mt-0.5">
                                    Tra cứu sơ đồ tiên quyết <RightOutlined style={{ fontSize: 10 }} />
                                </Text>
                            </div>
                        </div>
                    </Card>
                </Col>

                <Col xs={24} sm={12} lg={6}>
                    <Card
                        hoverable
                        className="border-0 shadow-sm rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-md cursor-pointer"
                        onClick={() => router.push('/dashboard/materials')}
                    >
                        <div className="flex items-center gap-4">
                            <div
                                className="w-12 h-12 rounded-xl flex items-center justify-center text-white"
                                style={{ background: 'linear-gradient(135deg, #0D9488 0%, #10B981 100%)' }}
                            >
                                <FolderOpenOutlined style={{ fontSize: 24 }} />
                            </div>
                            <div>
                                <Text type="secondary" className="text-xs uppercase tracking-wider font-semibold">
                                    Tài liệu học tập
                                </Text>
                                <div className="text-2xl font-black text-gray-800">
                                    {loading ? <Spin size="small" /> : materials.length}
                                </div>
                                <Text className="text-xs text-teal-600 font-medium flex items-center gap-1 mt-0.5">
                                    Slide, đề cương & đề thi <RightOutlined style={{ fontSize: 10 }} />
                                </Text>
                            </div>
                        </div>
                    </Card>
                </Col>

                <Col xs={24} sm={12} lg={6}>
                    <Card
                        hoverable
                        className="border-0 shadow-sm rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-md cursor-pointer"
                        onClick={() => router.push('/dashboard/datasets')}
                    >
                        <div className="flex items-center gap-4">
                            <div
                                className="w-12 h-12 rounded-xl flex items-center justify-center text-white"
                                style={{ background: 'linear-gradient(135deg, #7C3AED 0%, #8B5CF6 100%)' }}
                            >
                                <DatabaseOutlined style={{ fontSize: 24 }} />
                            </div>
                            <div>
                                <Text type="secondary" className="text-xs uppercase tracking-wider font-semibold">
                                    Bộ dữ liệu AI
                                </Text>
                                <div className="text-2xl font-black text-gray-800">
                                    {loading ? <Spin size="small" /> : datasets.length}
                                </div>
                                <Text className="text-xs text-purple-600 font-medium flex items-center gap-1 mt-0.5">
                                    Kiến thức huấn luyện RAG <RightOutlined style={{ fontSize: 10 }} />
                                </Text>
                            </div>
                        </div>
                    </Card>
                </Col>

                <Col xs={24} sm={12} lg={6}>
                    <Card
                        hoverable
                        className="border-0 shadow-sm rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-md cursor-pointer"
                        onClick={() => router.push('/dashboard/grades')}
                    >
                        <div className="flex items-center gap-4">
                            <div
                                className="w-12 h-12 rounded-xl flex items-center justify-center text-white"
                                style={{ background: 'linear-gradient(135deg, #EA580C 0%, #F59E0B 100%)' }}
                            >
                                <TeamOutlined style={{ fontSize: 24 }} />
                            </div>
                            <div>
                                <Text type="secondary" className="text-xs uppercase tracking-wider font-semibold">
                                    Sinh viên theo dõi
                                </Text>
                                <div className="text-2xl font-black text-gray-800">
                                    {loading ? <Spin size="small" /> : students.length}
                                </div>
                                <Text className="text-xs text-orange-600 font-medium flex items-center gap-1 mt-0.5">
                                    Hồ sơ học vụ & điểm số <RightOutlined style={{ fontSize: 10 }} />
                                </Text>
                            </div>
                        </div>
                    </Card>
                </Col>
            </Row>

            {/* Split Content Area */}
            <Row gutter={[20, 20]}>
                {/* Left Column: Quick Student Lookup & Recent Materials */}
                <Col xs={24} lg={15}>
                    {/* Quick Student Advising Lookup */}
                    <Card
                        title={
                            <Space>
                                <SearchOutlined className="text-blue-600" />
                                <span className="font-bold">Tra cứu nhanh Tiến độ Học tập Sinh viên</span>
                            </Space>
                        }
                        extra={
                            <Button
                                type="link"
                                size="small"
                                onClick={() => router.push('/dashboard/grades')}
                                className="font-medium"
                            >
                                Mở trang Quản lý điểm đầy đủ <ArrowRightOutlined />
                            </Button>
                        }
                        className="border-0 shadow-sm rounded-2xl mb-6"
                    >
                        <div className="mb-4">
                            <Text type="secondary" className="text-xs block mb-1">
                                Chọn hoặc tìm sinh viên theo MSSV / Họ tên để xem nhanh kết quả học tập và cảnh báo:
                            </Text>
                            <Select
                                showSearch
                                allowClear
                                placeholder="Gõ tên hoặc mã sinh viên (VD: SV001, 20240102, Lê Hải Đăng...)"
                                className="w-full"
                                optionFilterProp="label"
                                value={selectedStudentId}
                                onChange={setSelectedStudentId}
                                size="large"
                                options={students.map((s) => ({
                                    value: s.id,
                                    label: `${s.student_code ? `[${s.student_code}] ` : ''}${s.full_name} (${s.email})`,
                                }))}
                            />
                        </div>

                        {transcriptLoading ? (
                            <div className="text-center py-8">
                                <Spin />
                                <div className="mt-2 text-xs text-gray-400">Đang tải bảng điểm sinh viên...</div>
                            </div>
                        ) : selectedStudent && studentStats ? (
                            <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 mt-3">
                                <div className="flex items-center justify-between flex-wrap gap-3 pb-3 border-b border-slate-200">
                                    <div className="flex items-center gap-3">
                                        <Avatar
                                            size={44}
                                            style={{ backgroundColor: '#0F4C81', fontWeight: 600 }}
                                        >
                                            {selectedStudent.full_name?.charAt(0) || 'S'}
                                        </Avatar>
                                        <div>
                                            <div className="font-bold text-gray-900 text-base">
                                                {selectedStudent.full_name}
                                            </div>
                                            <div className="text-xs text-gray-500">
                                                MSSV: <span className="font-semibold text-gray-700">{selectedStudent.student_code || '—'}</span> · {selectedStudent.email}
                                            </div>
                                        </div>
                                    </div>
                                    <div>
                                        {studentStats.failed > 1 ? (
                                            <Tag color="error" icon={<WarningOutlined />} className="font-semibold px-2 py-1">
                                                Cảnh báo học tập (Nợ {studentStats.failed} môn)
                                            </Tag>
                                        ) : (
                                            <Tag color="success" icon={<CheckCircleOutlined />} className="font-semibold px-2 py-1">
                                                Tiến độ học tập bình thường
                                            </Tag>
                                        )}
                                    </div>
                                </div>

                                {/* Mini Stats */}
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3 text-center">
                                    <div className="bg-white p-2 rounded-lg border border-slate-100 shadow-2xs">
                                        <div className="text-xs text-gray-400">Điểm TB (GPA)</div>
                                        <div className="text-lg font-black text-blue-600">{studentStats.avg}</div>
                                    </div>
                                    <div className="bg-white p-2 rounded-lg border border-slate-100 shadow-2xs">
                                        <div className="text-xs text-gray-400">Môn đã đạt</div>
                                        <div className="text-lg font-black text-emerald-600">{studentStats.passed}</div>
                                    </div>
                                    <div className="bg-white p-2 rounded-lg border border-slate-100 shadow-2xs">
                                        <div className="text-xs text-gray-400">Môn nợ / trượt</div>
                                        <div className="text-lg font-black text-red-500">{studentStats.failed}</div>
                                    </div>
                                    <div className="bg-white p-2 rounded-lg border border-slate-100 shadow-2xs">
                                        <div className="text-xs text-gray-400">Đang học</div>
                                        <div className="text-lg font-black text-indigo-500">{studentStats.inProgress}</div>
                                    </div>
                                </div>

                                <div className="mt-3 flex justify-end">
                                    <Button
                                        type="primary"
                                        size="small"
                                        onClick={() => router.push(`/dashboard/grades?student_id=${selectedStudent.id}`)}
                                        className="!bg-[#0F4C81]"
                                    >
                                        Xem chi tiết & Nhập điểm sinh viên này
                                    </Button>
                                </div>
                            </div>
                        ) : (
                            <div className="text-center py-6 text-gray-400 text-sm border border-dashed rounded-xl">
                                Chọn một sinh viên ở trên để tra cứu nhanh tiến độ học tập và tư vấn.
                            </div>
                        )}
                    </Card>

                    {/* Recent Materials */}
                    <Card
                        title={
                            <Space>
                                <FolderOpenOutlined className="text-teal-600" />
                                <span className="font-bold">Tài liệu học tập mới cập nhật</span>
                            </Space>
                        }
                        extra={
                            <Button
                                type="link"
                                size="small"
                                onClick={() => router.push('/dashboard/materials')}
                            >
                                Quản lý toàn bộ <ArrowRightOutlined />
                            </Button>
                        }
                        className="border-0 shadow-sm rounded-2xl"
                    >
                        {materials.length === 0 ? (
                            <div className="text-center py-6 text-gray-400 text-sm">
                                Chưa có tài liệu nào được tải lên.
                            </div>
                        ) : (
                            <div className="divide-y divide-gray-100">
                                {materials.slice(0, 5).map((mat) => {
                                    const course = courseMap.get(mat.course_id);
                                    return (
                                        <div
                                            key={mat.id}
                                            className="py-3 flex items-center justify-between gap-3 hover:bg-gray-50/80 px-2 rounded-lg transition-colors"
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className="w-9 h-9 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center shrink-0">
                                                    <FileTextOutlined />
                                                </div>
                                                <div>
                                                    <div className="font-semibold text-gray-800 text-sm">
                                                        {mat.title}
                                                    </div>
                                                    <div className="text-xs text-gray-500">
                                                        {course ? `${course.course_code} - ${course.course_name}` : 'Chưa gắn môn'}
                                                    </div>
                                                </div>
                                            </div>
                                            <div>
                                                <Tag color="cyan">
                                                    {MATERIAL_TYPE_LABELS[mat.material_type] || mat.material_type}
                                                </Tag>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </Card>
                </Col>

                {/* Right Column: Faculty AI Assistant & Quick Actions */}
                <Col xs={24} lg={9}>
                    {/* Faculty AI Assistant Widget */}
                    <Card
                        title={
                            <Space>
                                <BulbOutlined className="text-amber-500" />
                                <span className="font-bold">Gợi ý tác vụ Trợ lý AI</span>
                            </Space>
                        }
                        className="border-0 shadow-sm rounded-2xl mb-6 bg-linear-to-br from-amber-50/40 to-white"
                    >
                        <Paragraph type="secondary" className="text-xs !mb-3">
                            Chọn câu hỏi mẫu dưới đây để bắt đầu làm việc cùng Trợ lý AI Cố vấn Học tập:
                        </Paragraph>

                        <div className="space-y-2.5">
                            {quickAIPrompts.map((item, idx) => (
                                <div
                                    key={idx}
                                    onClick={() => handlePromptClick(item.prompt)}
                                    className="p-3 bg-white border border-amber-200/60 rounded-xl hover:border-amber-400 hover:shadow-xs transition-all cursor-pointer group"
                                >
                                    <div className="font-bold text-gray-800 text-sm flex items-center justify-between">
                                        <span>{item.title}</span>
                                        <RightOutlined className="text-xs text-gray-400 group-hover:text-amber-600 transition-colors" />
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1 line-clamp-2">
                                        {item.prompt}
                                    </div>
                                </div>
                            ))}
                        </div>

                        <Button
                            type="primary"
                            icon={<MessageOutlined />}
                            onClick={() => router.push('/dashboard/chat')}
                            className="w-full mt-4 font-semibold !bg-[#0F4C81]"
                        >
                            Mở khung Trò chuyện AI
                        </Button>
                    </Card>

                    {/* Quick Access to Teacher Tools */}
                    <Card
                        title={<span className="font-bold">Lối tắt nghiệp vụ Giảng viên</span>}
                        className="border-0 shadow-sm rounded-2xl"
                    >
                        <div className="space-y-3">
                            <div
                                onClick={() => router.push('/dashboard/grades')}
                                className="flex items-center justify-between p-3 rounded-xl border border-gray-100 hover:bg-blue-50/60 hover:border-blue-200 transition-all cursor-pointer"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">
                                        <FormOutlined />
                                    </div>
                                    <div>
                                        <div className="font-semibold text-gray-800 text-sm">Nhập điểm & Bảng điểm</div>
                                        <div className="text-xs text-gray-500">Nhập lẻ hoặc tải CSV hàng loạt</div>
                                    </div>
                                </div>
                                <RightOutlined className="text-gray-400 text-xs" />
                            </div>

                            <div
                                onClick={() => router.push('/dashboard/materials')}
                                className="flex items-center justify-between p-3 rounded-xl border border-gray-100 hover:bg-teal-50/60 hover:border-teal-200 transition-all cursor-pointer"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-teal-100 text-teal-700 flex items-center justify-center">
                                        <FolderOpenOutlined />
                                    </div>
                                    <div>
                                        <div className="font-semibold text-gray-800 text-sm">Đăng tải tài liệu môn</div>
                                        <div className="text-xs text-gray-500">Đề cương, slide, giáo trình, đề thi</div>
                                    </div>
                                </div>
                                <RightOutlined className="text-gray-400 text-xs" />
                            </div>

                            <div
                                onClick={() => router.push('/dashboard/courses')}
                                className="flex items-center justify-between p-3 rounded-xl border border-gray-100 hover:bg-indigo-50/60 hover:border-indigo-200 transition-all cursor-pointer"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center">
                                        <BookOutlined />
                                    </div>
                                    <div>
                                        <div className="font-semibold text-gray-800 text-sm">Tra cứu cây tiên quyết</div>
                                        <div className="text-xs text-gray-500">Xem điều kiện đăng ký môn học</div>
                                    </div>
                                </div>
                                <RightOutlined className="text-gray-400 text-xs" />
                            </div>

                            <div
                                onClick={() => router.push('/dashboard/datasets')}
                                className="flex items-center justify-between p-3 rounded-xl border border-gray-100 hover:bg-purple-50/60 hover:border-purple-200 transition-all cursor-pointer"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center">
                                        <DatabaseOutlined />
                                    </div>
                                    <div>
                                        <div className="font-semibold text-gray-800 text-sm">Bộ dữ liệu kiến thức AI</div>
                                        <div className="text-xs text-gray-500">Tạo dataset phục vụ sinh viên</div>
                                    </div>
                                </div>
                                <RightOutlined className="text-gray-400 text-xs" />
                            </div>
                        </div>
                    </Card>
                </Col>
            </Row>
        </div>
    );
}
