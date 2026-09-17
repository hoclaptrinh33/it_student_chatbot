'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
    Card,
    Table,
    Tag,
    Typography,
    Input,
    Select,
    Button,
    Row,
    Col,
    Drawer,
    Spin,
    Breadcrumb,
    Empty,
    Divider,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
    BookOutlined,
    SearchOutlined,
    ApartmentOutlined,
    FolderOpenOutlined,
    CheckCircleOutlined,
    ExclamationCircleOutlined,
} from '@ant-design/icons';
import AuthGuard from '@/components/Auth/AuthGuard';
import courseService, {
    Course,
    CoursePrerequisites,
    CAREER_TRACKS,
    CAREER_TRACK_LABELS,
    CareerTrack,
} from '@/services/courseService';

const { Title, Text, Paragraph } = Typography;

const TRACK_COLORS: Record<string, string> = {
    SOFTWARE_ENGINEERING: 'blue',
    DATA_AI: 'purple',
    NETWORK_SECURITY: 'volcano',
    INFO_SYSTEMS: 'cyan',
};

export default function CoursesCatalogPage() {
    const router = useRouter();

    const [courses, setCourses] = useState<Course[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedTrack, setSelectedTrack] = useState<string | undefined>();
    const [selectedSemester, setSelectedSemester] = useState<number | undefined>();

    // Drawer state for prerequisites
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
    const [prereqs, setPrereqs] = useState<CoursePrerequisites | null>(null);
    const [prereqLoading, setPrereqLoading] = useState(false);

    const loadCourses = useCallback(async () => {
        setLoading(true);
        try {
            const data = await courseService.listCourses();
            setCourses(data || []);
        } catch (err) {
            console.error('Failed to load courses:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadCourses();
    }, [loadCourses]);

    // Open Prerequisite Drawer
    const openPrerequisites = async (course: Course) => {
        setSelectedCourse(course);
        setDrawerOpen(true);
        setPrereqLoading(true);
        try {
            const data = await courseService.getPrerequisites(course.id);
            setPrereqs(data);
        } catch (err) {
            console.error('Failed to load prerequisites:', err);
            setPrereqs(null);
        } finally {
            setPrereqLoading(false);
        }
    };

    // Filter courses
    const filteredCourses = useMemo(() => {
        return courses.filter((c) => {
            const matchesQuery =
                !searchQuery.trim() ||
                c.course_code.toLowerCase().includes(searchQuery.toLowerCase().trim()) ||
                c.course_name.toLowerCase().includes(searchQuery.toLowerCase().trim());
            const matchesTrack = !selectedTrack || c.career_track === selectedTrack;
            const matchesSem = !selectedSemester || c.semester === selectedSemester;
            return matchesQuery && matchesTrack && matchesSem;
        });
    }, [courses, searchQuery, selectedTrack, selectedSemester]);

    const columns: ColumnsType<Course> = [
        {
            title: 'Mã học phần',
            dataIndex: 'course_code',
            key: 'course_code',
            width: 140,
            render: (code: string) => (
                <Tag color="blue" className="font-bold text-sm px-2 py-0.5">
                    {code}
                </Tag>
            ),
        },
        {
            title: 'Tên học phần',
            dataIndex: 'course_name',
            key: 'course_name',
            render: (name: string, record) => (
                <div>
                    <Text strong className="text-gray-900 text-sm block">{name}</Text>
                    {record.description && (
                        <Paragraph ellipsis={{ rows: 1 }} className="!mb-0 text-xs text-gray-400">
                            {record.description}
                        </Paragraph>
                    )}
                </div>
            ),
        },
        {
            title: 'Số tín chỉ',
            dataIndex: 'credits',
            key: 'credits',
            width: 100,
            align: 'center',
            render: (cr: number) => <span className="font-semibold text-gray-700">{cr} TC</span>,
        },
        {
            title: 'Học kỳ đề xuất',
            dataIndex: 'semester',
            key: 'semester',
            width: 130,
            align: 'center',
            render: (sem?: number) => (sem ? `Học kỳ ${sem}` : '—'),
        },
        {
            title: 'Chuyên ngành định hướng',
            dataIndex: 'career_track',
            key: 'career_track',
            width: 220,
            render: (track?: string) => {
                if (!track) return <Tag color="default">Đại cương / Cơ sở</Tag>;
                return (
                    <Tag color={TRACK_COLORS[track] || 'default'} className="font-medium">
                        {CAREER_TRACK_LABELS[track as CareerTrack] || track}
                    </Tag>
                );
            },
        },
        {
            title: 'Loại môn',
            dataIndex: 'is_mandatory',
            key: 'is_mandatory',
            width: 120,
            align: 'center',
            render: (man?: boolean) =>
                man ? (
                    <Tag color="gold" className="font-medium">Bắt buộc</Tag>
                ) : (
                    <Tag color="green" className="font-medium">Tự chọn</Tag>
                ),
        },
        {
            title: 'Sơ đồ tiên quyết',
            key: 'prereq',
            width: 150,
            align: 'center',
            render: (_, record) => (
                <Button
                    size="small"
                    icon={<ApartmentOutlined />}
                    onClick={() => openPrerequisites(record)}
                    className="text-[#0F4C81] border-[#0F4C81]/30 hover:border-[#0F4C81]"
                >
                    Xem tiên quyết
                </Button>
            ),
        },
    ];

    return (
        <AuthGuard>
            <div className="space-y-6 pb-12">
                {/* Header & Breadcrumb */}
                <div>
                    <Breadcrumb
                        items={[
                            { title: 'Bảng điều khiển', href: '/dashboard' },
                            { title: 'Chương trình đào tạo' },
                            { title: 'Danh mục môn học & Cây tiên quyết' },
                        ]}
                    />
                    <div className="flex items-center gap-3 mt-3">
                        <div className="w-10 h-10 rounded-xl bg-[#0F4C81] text-white flex items-center justify-center shadow-md">
                            <BookOutlined style={{ fontSize: 20 }} />
                        </div>
                        <div>
                            <Title level={3} className="!mb-0">
                                Danh mục Môn học & Cây Tiên quyết Khoa CNTT
                            </Title>
                            <Text type="secondary" className="text-sm">
                                Tra cứu danh mục học phần, số tín chỉ, chuyên ngành định hướng và sơ đồ điều kiện tiên quyết phục vụ cố vấn đăng ký môn.
                            </Text>
                        </div>
                    </div>
                </div>

                {/* Filters */}
                <Card className="border-0 shadow-sm rounded-2xl p-2">
                    <Row gutter={[16, 16]} align="middle">
                        <Col xs={24} sm={10} md={9}>
                            <Input
                                prefix={<SearchOutlined className="text-gray-400" />}
                                placeholder="Tìm mã môn hoặc tên học phần (VD: INT1101, CSDL...)"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                allowClear
                                size="large"
                            />
                        </Col>
                        <Col xs={24} sm={8} md={8}>
                            <Select
                                allowClear
                                placeholder="Lọc theo Chuyên ngành định hướng"
                                className="w-full"
                                value={selectedTrack}
                                onChange={setSelectedTrack}
                                size="large"
                                options={CAREER_TRACKS.map((t) => ({
                                    value: t,
                                    label: CAREER_TRACK_LABELS[t],
                                }))}
                            />
                        </Col>
                        <Col xs={24} sm={6} md={7}>
                            <Select
                                allowClear
                                placeholder="Lọc theo Học kỳ"
                                className="w-full"
                                value={selectedSemester}
                                onChange={setSelectedSemester}
                                size="large"
                                options={[1, 2, 3, 4, 5, 6, 7, 8].map((sem) => ({
                                    value: sem,
                                    label: `Học kỳ ${sem}`,
                                }))}
                            />
                        </Col>
                    </Row>
                </Card>

                {/* Course List Table */}
                <Card className="shadow-sm border-0 rounded-2xl" styles={{ body: { padding: 0 } }}>
                    {loading ? (
                        <div className="flex justify-center py-16">
                            <Spin size="large" />
                        </div>
                    ) : (
                        <Table
                            rowKey="id"
                            columns={columns}
                            dataSource={filteredCourses}
                            pagination={{ pageSize: 12, showTotal: (total) => `Tổng số ${total} học phần` }}
                            locale={{ emptyText: <Empty description="Không tìm thấy môn học phù hợp" /> }}
                        />
                    )}
                </Card>

                {/* Prerequisite Drawer */}
                <Drawer
                    title={
                        <div>
                            <div className="text-xs text-gray-400 uppercase tracking-wider font-semibold">
                                Sơ đồ điều kiện tiên quyết
                            </div>
                            <div className="text-lg font-bold text-gray-800">
                                {selectedCourse?.course_code} · {selectedCourse?.course_name}
                            </div>
                        </div>
                    }
                    placement="right"
                    width={520}
                    open={drawerOpen}
                    onClose={() => setDrawerOpen(false)}
                >
                    {prereqLoading ? (
                        <div className="text-center py-16">
                            <Spin size="large" />
                            <div className="mt-2 text-xs text-gray-400">Đang phân tích sơ đồ tiên quyết...</div>
                        </div>
                    ) : selectedCourse ? (
                        <div className="space-y-6">
                            {/* Course Quick Summary */}
                            <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-4">
                                <div className="flex items-center justify-between gap-2 mb-2">
                                    <Tag color="blue" className="font-bold text-base px-2.5 py-0.5">
                                        {selectedCourse.course_code}
                                    </Tag>
                                    <Tag color={selectedCourse.is_mandatory ? 'gold' : 'green'}>
                                        {selectedCourse.is_mandatory ? 'Học phần bắt buộc' : 'Học phần tự chọn'}
                                    </Tag>
                                </div>
                                <div className="text-sm font-semibold text-gray-800 mb-1">
                                    {selectedCourse.course_name}
                                </div>
                                <div className="text-xs text-gray-500">
                                    Số tín chỉ: <span className="font-semibold text-gray-700">{selectedCourse.credits}</span> · Kỳ đề xuất: <span className="font-semibold text-gray-700">{selectedCourse.semester ? `HK ${selectedCourse.semester}` : 'Linh hoạt'}</span>
                                </div>
                                {selectedCourse.career_track && (
                                    <div className="mt-2">
                                        <Tag color={TRACK_COLORS[selectedCourse.career_track] || 'default'}>
                                            {CAREER_TRACK_LABELS[selectedCourse.career_track as CareerTrack] || selectedCourse.career_track}
                                        </Tag>
                                    </div>
                                )}
                            </div>

                            {/* Hard Prerequisites */}
                            <div>
                                <div className="flex items-center gap-2 mb-3">
                                    <CheckCircleOutlined className="text-red-500" />
                                    <span className="font-bold text-gray-800 text-sm">
                                        Môn học Tiên quyết Bắt buộc (Hard Prerequisites)
                                    </span>
                                </div>
                                {!prereqs?.hard || prereqs.hard.length === 0 ? (
                                    <div className="p-3 bg-gray-50 rounded-xl text-xs text-gray-400 border border-dashed">
                                        Học phần này không yêu cầu môn tiên quyết bắt buộc. Sinh viên có thể tự do đăng ký theo học kỳ.
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        {prereqs.hard.map((edge, idx) => (
                                            <div
                                                key={edge.id || idx}
                                                className="p-3 bg-red-50/60 border border-red-200/80 rounded-xl flex items-center justify-between"
                                            >
                                                <div>
                                                    <Tag color="red" className="font-bold">
                                                        {edge.prerequisite_code || edge.prerequisite_course_id}
                                                    </Tag>
                                                    <span className="font-semibold text-gray-800 text-sm">
                                                        {edge.prerequisite_name || 'Môn học tiên quyết'}
                                                    </span>
                                                </div>
                                                <Tag color="error" className="text-2xs">Bắt buộc đã đạt</Tag>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* Soft Prerequisites */}
                            <div>
                                <div className="flex items-center gap-2 mb-3">
                                    <ExclamationCircleOutlined className="text-amber-500" />
                                    <span className="font-bold text-gray-800 text-sm">
                                        Môn học Trước khuyên dùng (Soft Prerequisites)
                                    </span>
                                </div>
                                {!prereqs?.soft || prereqs.soft.length === 0 ? (
                                    <div className="p-3 bg-gray-50 rounded-xl text-xs text-gray-400 border border-dashed">
                                        Không có môn học trước bổ sung được yêu cầu.
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        {prereqs.soft.map((edge, idx) => (
                                            <div
                                                key={edge.id || idx}
                                                className="p-3 bg-amber-50/60 border border-amber-200/80 rounded-xl flex items-center justify-between"
                                            >
                                                <div>
                                                    <Tag color="orange" className="font-bold">
                                                        {edge.prerequisite_code || edge.prerequisite_course_id}
                                                    </Tag>
                                                    <span className="font-semibold text-gray-800 text-sm">
                                                        {edge.prerequisite_name || 'Môn học trước'}
                                                    </span>
                                                </div>
                                                <Tag color="warning" className="text-2xs">Khuyên học trước</Tag>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* Closure Prerequisites */}
                            {prereqs?.closure && prereqs.closure.length > 0 && (
                                <div>
                                    <div className="flex items-center gap-2 mb-3">
                                        <ApartmentOutlined className="text-purple-600" />
                                        <span className="font-bold text-gray-800 text-sm">
                                            Toàn bộ chuỗi tiên quyết bắc cầu (Transitive Chain)
                                        </span>
                                    </div>
                                    <div className="flex flex-wrap gap-2 p-3 bg-purple-50/40 rounded-xl border border-purple-100">
                                        {prereqs.closure.map((edge, idx) => (
                                            <Tag key={edge.id || idx} color="purple" className="font-medium">
                                                {edge.prerequisite_code || edge.prerequisite_course_id}
                                                {edge.prerequisite_name ? ` · ${edge.prerequisite_name}` : ''}
                                            </Tag>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <Divider />

                            {/* Quick Action to view materials */}
                            <Button
                                type="primary"
                                icon={<FolderOpenOutlined />}
                                onClick={() => {
                                    setDrawerOpen(false);
                                    router.push('/dashboard/materials');
                                }}
                                className="w-full !bg-[#0F4C81] font-semibold"
                                size="large"
                            >
                                Mở kho tài liệu học phần này
                            </Button>
                        </div>
                    ) : null}
                </Drawer>
            </div>
        </AuthGuard>
    );
}
