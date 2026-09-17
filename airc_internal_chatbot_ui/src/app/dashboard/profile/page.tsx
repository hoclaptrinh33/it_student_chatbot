'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { Card, Avatar, Tag, Button, Typography, Spin, Tabs, Alert, Descriptions, Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
    UserOutlined,
    MailOutlined,
    IdcardOutlined,
    BankOutlined,
    CheckCircleOutlined,
    ClockCircleOutlined,
    CloseCircleOutlined,
    FileTextOutlined,
    SafetyCertificateOutlined,
    BookOutlined,
} from '@ant-design/icons';
import { useRouter } from 'next/navigation';
import AuthGuard from '@/components/Auth/AuthGuard';
import useAuthStore from '@/stores/authStore';
import academicService, { AcademicRecord } from '@/services/academicService';

const { Title, Text } = Typography;

export default function StudentProfilePage() {
    const router = useRouter();
    const { user } = useAuthStore();
    const [loading, setLoading] = useState(true);
    const [records, setRecords] = useState<AcademicRecord[]>([]);

    useEffect(() => {
        const fetchAcademicData = async () => {
            try {
                const data = await academicService.getMyTranscript();
                setRecords(data.records || []);
            } catch (err) {
                console.warn('Could not load transcript for profile:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchAcademicData();
    }, []);

    // Compute academic summary
    const academicStats = useMemo(() => {
        let passedCredits = 0;
        let inProgressCredits = 0;
        let failedCredits = 0;
        let totalWeightedGrade = 0;
        let gradedCredits = 0;

        for (const r of records) {
            const cr = r.credits || 0;
            if (r.status === 'PASSED') {
                passedCredits += cr;
                if (typeof r.grade === 'number') {
                    totalWeightedGrade += r.grade * cr;
                    gradedCredits += cr;
                }
            } else if (r.status === 'IN_PROGRESS') {
                inProgressCredits += cr;
            } else if (r.status === 'FAILED') {
                failedCredits += cr;
            }
        }

        const calculatedGpa = gradedCredits > 0 ? (totalWeightedGrade / gradedCredits).toFixed(2) : '—';

        return {
            passedCredits,
            inProgressCredits,
            failedCredits,
            totalCreditsAttempted: passedCredits + failedCredits,
            gpa: calculatedGpa,
            totalCourses: records.length,
        };
    }, [records]);

    const recentColumns: ColumnsType<AcademicRecord> = [
        {
            title: 'Mã học phần',
            dataIndex: 'course_code',
            key: 'course_code',
            render: (code: string) => <Text strong>{code || '—'}</Text>,
        },
        {
            title: 'Tên môn học',
            dataIndex: 'course_name',
            key: 'course_name',
            render: (name: string) => name || '—',
        },
        {
            title: 'Tín chỉ',
            dataIndex: 'credits',
            key: 'credits',
            width: 80,
            align: 'center',
        },
        {
            title: 'Điểm',
            dataIndex: 'grade',
            key: 'grade',
            width: 80,
            align: 'center',
            render: (grade?: number | null) => (typeof grade === 'number' ? <Text strong>{grade}</Text> : '—'),
        },
        {
            title: 'Trạng thái',
            dataIndex: 'status',
            key: 'status',
            width: 120,
            render: (status: string) => {
                if (status === 'PASSED') return <Tag color="green">Đã đạt</Tag>;
                if (status === 'FAILED') return <Tag color="red">Chưa đạt</Tag>;
                return <Tag color="blue">Đang học</Tag>;
            },
        },
    ];

    return (
        <AuthGuard>
            <div className="max-w-5xl mx-auto p-4 sm:p-6 space-y-6">
                {/* Header Profile Card */}
                <Card className="rounded-2xl border-slate-200/80 shadow-xs overflow-hidden">
                    <div className="flex flex-col sm:flex-row items-center sm:items-start gap-5">
                        <Avatar
                            size={84}
                            icon={<UserOutlined />}
                            src={user?.avatar_url}
                            className="shadow-sm shrink-0"
                            style={{ background: 'linear-gradient(135deg, #0F4C81 0%, #0D9488 100%)' }}
                        />
                        <div className="flex-1 text-center sm:text-left space-y-1">
                            <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                                <Title level={3} className="!mb-0 text-slate-800">
                                    {user?.full_name || 'Hồ sơ Sinh viên'}
                                </Title>
                                <Tag color="blue" className="w-fit mx-auto sm:mx-0 font-medium">
                                    Sinh viên chính quy
                                </Tag>
                            </div>

                            <div className="flex flex-wrap items-center justify-center sm:justify-start gap-x-4 gap-y-1 text-xs text-slate-500 pt-1">
                                <span className="flex items-center gap-1">
                                    <IdcardOutlined className="text-slate-400" />
                                    <span>MSSV: <strong>{user?.student_code || user?.email?.split('@')[0] || '—'}</strong></span>
                                </span>
                                <span className="flex items-center gap-1">
                                    <BankOutlined className="text-slate-400" />
                                    <span>{user?.department || 'Khoa Công nghệ Thông tin'}</span>
                                </span>
                                <span className="flex items-center gap-1">
                                    <MailOutlined className="text-slate-400" />
                                    <span>{user?.email}</span>
                                </span>
                            </div>
                        </div>

                        <div className="shrink-0 flex sm:flex-col gap-2">
                            <Button
                                type="primary"
                                icon={<FileTextOutlined />}
                                onClick={() => router.push('/dashboard/transcript')}
                                className="bg-[#0F4C81] hover:bg-[#165a96] rounded-lg text-xs h-8"
                            >
                                Bảng điểm chi tiết
                            </Button>
                            <Button
                                icon={<BookOutlined />}
                                onClick={() => router.push('/dashboard/eligible-courses')}
                                className="rounded-lg text-xs h-8"
                            >
                                Môn đủ điều kiện
                            </Button>
                        </div>
                    </div>
                </Card>

                {/* Academic KPI Stats */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
                    <Card className="rounded-xl border-slate-200/80 shadow-xs p-1">
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-slate-500 font-medium">Tín chỉ tích lũy</span>
                            <CheckCircleOutlined className="text-emerald-500 text-base" />
                        </div>
                        <div className="text-2xl font-bold text-slate-800 mt-2">
                            {loading ? <Spin size="small" /> : academicStats.passedCredits}
                        </div>
                        <div className="text-[11px] text-emerald-600 font-medium mt-1">Đã hoàn thành</div>
                    </Card>

                    <Card className="rounded-xl border-slate-200/80 shadow-xs p-1">
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-slate-500 font-medium">Tín chỉ đang học</span>
                            <ClockCircleOutlined className="text-blue-500 text-base" />
                        </div>
                        <div className="text-2xl font-bold text-slate-800 mt-2">
                            {loading ? <Spin size="small" /> : academicStats.inProgressCredits}
                        </div>
                        <div className="text-[11px] text-blue-600 font-medium mt-1">Học kỳ hiện tại</div>
                    </Card>

                    <Card className="rounded-xl border-slate-200/80 shadow-xs p-1">
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-slate-500 font-medium">Tín chỉ chưa đạt</span>
                            <CloseCircleOutlined className="text-rose-500 text-base" />
                        </div>
                        <div className="text-2xl font-bold text-slate-800 mt-2">
                            {loading ? <Spin size="small" /> : academicStats.failedCredits}
                        </div>
                        <div className="text-[11px] text-rose-600 font-medium mt-1">Cần đăng ký học lại</div>
                    </Card>

                    <Card className="rounded-xl border-slate-200/80 shadow-xs p-1">
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-slate-500 font-medium">Điểm TB tích lũy (GPA)</span>
                            <SafetyCertificateOutlined className="text-[#0F4C81] text-base" />
                        </div>
                        <div className="text-2xl font-bold text-slate-800 mt-2">
                            {loading ? <Spin size="small" /> : academicStats.gpa}
                        </div>
                        <div className="text-[11px] text-slate-500 font-medium mt-1">Hệ 10 quy đổi</div>
                    </Card>
                </div>

                {/* Tabs Information */}
                <Card className="rounded-2xl border-slate-200/80 shadow-xs">
                    <Tabs
                        defaultActiveKey="info"
                        items={[
                            {
                                key: 'info',
                                label: 'Thông tin Học vụ',
                                children: (
                                    <div className="py-2">
                                        <Descriptions
                                            bordered
                                            column={{ xxl: 2, xl: 2, lg: 2, md: 2, sm: 1, xs: 1 }}
                                            size="middle"
                                        >
                                            <Descriptions.Item label="Mã sinh viên">
                                                <Text strong>{user?.student_code || user?.email?.split('@')[0] || '—'}</Text>
                                            </Descriptions.Item>
                                            <Descriptions.Item label="Họ và tên">
                                                <Text strong>{user?.full_name || '—'}</Text>
                                            </Descriptions.Item>
                                            <Descriptions.Item label="Khoa quản lý">
                                                {user?.department || 'Khoa Công nghệ Thông tin'}
                                            </Descriptions.Item>
                                            <Descriptions.Item label="Hệ đào tạo">
                                                Đại học chính quy
                                            </Descriptions.Item>
                                            <Descriptions.Item label="Email sinh viên">
                                                {user?.email}
                                            </Descriptions.Item>
                                            <Descriptions.Item label="Trạng thái đào tạo">
                                                <Tag color="success">Đang theo học</Tag>
                                            </Descriptions.Item>
                                            <Descriptions.Item label="Cố vấn học tập">
                                                Ban Cố vấn Học tập Khoa CNTT
                                            </Descriptions.Item>
                                            <Descriptions.Item label="Tài khoản hệ thống">
                                                <Tag color="cyan">Đã kích hoạt</Tag>
                                            </Descriptions.Item>
                                        </Descriptions>
                                    </div>
                                ),
                            },
                            {
                                key: 'courses',
                                label: 'Học phần gần đây',
                                children: (
                                    <div className="space-y-3 py-2">
                                        <div className="flex items-center justify-between">
                                            <Text type="secondary" className="text-xs">
                                                Danh sách học phần đã ghi nhận trong hồ sơ học vụ ({records.length} môn)
                                            </Text>
                                            <Button
                                                type="link"
                                                size="small"
                                                onClick={() => router.push('/dashboard/transcript')}
                                                className="text-[#0F4C81] p-0"
                                            >
                                                Xem đầy đủ bảng điểm →
                                            </Button>
                                        </div>
                                        <Table
                                            dataSource={records.slice(0, 8)}
                                            columns={recentColumns}
                                            rowKey="id"
                                            pagination={false}
                                            size="small"
                                            loading={loading}
                                        />
                                    </div>
                                ),
                            },
                            {
                                key: 'security',
                                label: 'Tài khoản & Bảo mật',
                                children: (
                                    <div className="py-2 max-w-xl space-y-4">
                                        <Alert
                                            message="Thông tin bảo mật tài khoản"
                                            description="Tài khoản sinh viên được đồng bộ trực tiếp từ hệ thống quản lý đào tạo của trường. Mọi yêu cầu thay đổi thông tin cá nhân hoặc cấp lại mật khẩu vui lòng liên hệ Văn phòng Khoa Công nghệ Thông tin."
                                            type="info"
                                            showIcon
                                            className="rounded-xl"
                                        />

                                        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2 text-xs text-slate-600">
                                            <div><strong>Hỗ trợ kỹ thuật Khoa CNTT:</strong> fit@eau.edu.vn</div>
                                            <div><strong>Thời gian tiếp nhận:</strong> Thứ Hai – Thứ Sáu (8:00 – 17:00)</div>
                                        </div>
                                    </div>
                                ),
                            },
                        ]}
                    />
                </Card>
            </div>
        </AuthGuard>
    );
}
