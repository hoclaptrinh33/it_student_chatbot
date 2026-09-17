'use client';

import React from 'react';
import { Layout, Menu, Button, Tooltip } from 'antd';
import {
    DashboardOutlined,
    TeamOutlined,
    DatabaseOutlined,
    MessageOutlined,
    SafetyCertificateOutlined,
    RobotOutlined,
    SettingOutlined,
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    BookOutlined,
    FormOutlined,
    FolderOpenOutlined,
} from '@ant-design/icons';
import { usePathname, useRouter } from 'next/navigation';
import FitLogo from '../Common/FitLogo';
import useAuthStore from '@/stores/authStore';

const { Sider } = Layout;

interface SidebarProps {
    collapsed: boolean;
    onCollapse: (value: boolean) => void;
}

/**
 * Component Sidebar menu
 * Tu dong hien thi menu dua theo role cua user (DYNAMIC tu authStore)
 */
const MainSidebar: React.FC<SidebarProps> = ({ collapsed, onCollapse }) => {
    const router = useRouter();
    const pathname = usePathname();

    // Safe theme usage for SSR
    // const { token } = theme.useToken(); // Unused

    // Lay role tu AuthStore (DYNAMIC)
    const { user } = useAuthStore();
    const userRole = user?.role?.toLowerCase() || 'student';

    // Menu items configuration
    const getMenuItems = (role: string) => {
        const items: Array<{ key: string; icon: React.ReactNode; label: string }> = [];

        // Dashboard chỉ cho admin và teacher
        if (role === 'admin' || role === 'teacher') {
            items.push({
                key: '/dashboard',
                icon: <DashboardOutlined />,
                label: 'Bảng điều khiển',
            });
        }

        // Admin: Toàn quyền
        if (role === 'admin') {
            items.push(
                {
                    key: '/admin/permissions',
                    icon: <SafetyCertificateOutlined />,
                    label: 'Quyền hạn',
                },
                {
                    key: '/admin/roles',
                    icon: <SafetyCertificateOutlined />,
                    label: 'Vai trò',
                },
                {
                    key: '/admin/users',
                    icon: <TeamOutlined />,
                    label: 'Người dùng',
                },
                {
                    key: '/admin/chatbots',
                    icon: <RobotOutlined />,
                    label: 'Chatbots',
                },
                {
                    key: '/admin/courses',
                    icon: <BookOutlined />,
                    label: 'Môn học',
                },
                {
                    key: '/admin/grades',
                    icon: <FormOutlined />,
                    label: 'Bảng điểm',
                },
                {
                    key: '/dashboard/datasets',
                    icon: <DatabaseOutlined />,
                    label: 'Bộ dữ liệu',
                },
                {
                    key: '/admin/settings',
                    icon: <SettingOutlined />,
                    label: 'Cài đặt hệ thống',
                }
            );
        }

        // Teacher: Nghiệp vụ giảng dạy, cố vấn, tài liệu, điểm số, bộ dữ liệu
        if (role === 'teacher') {
            items.push(
                {
                    key: '/dashboard/grades',
                    icon: <FormOutlined />,
                    label: 'Quản lý điểm & SV',
                },
                {
                    key: '/dashboard/materials',
                    icon: <FolderOpenOutlined />,
                    label: 'Tài liệu giảng dạy',
                },
                {
                    key: '/dashboard/courses',
                    icon: <BookOutlined />,
                    label: 'Tra cứu môn học',
                },
                {
                    key: '/dashboard/datasets',
                    icon: <DatabaseOutlined />,
                    label: 'Bộ dữ liệu AI',
                }
            );
        }

        // Chat cho tất cả roles
        items.push({
            key: '/dashboard/chat',
            icon: <MessageOutlined />,
            label: role === 'teacher' ? 'Trợ lý AI Giảng viên' : 'Trò chuyện AI',
        });

        return items;
    };

    const selectedKey = (() => {
        if (pathname.startsWith('/dashboard/datasets')) return '/dashboard/datasets';
        if (pathname.startsWith('/dashboard/courses')) return '/dashboard/courses';
        if (pathname.startsWith('/dashboard/grades') || pathname.startsWith('/admin/grades')) {
            return userRole === 'teacher' ? '/dashboard/grades' : '/admin/grades';
        }
        if (pathname.startsWith('/dashboard/materials')) return '/dashboard/materials';
        if (pathname.startsWith('/dashboard/chat')) return '/dashboard/chat';
        if (pathname.startsWith('/admin/users')) return '/admin/users';
        if (pathname.startsWith('/admin/roles')) return '/admin/roles';
        if (pathname.startsWith('/admin/permissions')) return '/admin/permissions';
        if (pathname.startsWith('/admin/chatbots')) return '/admin/chatbots';
        if (pathname.startsWith('/admin/settings')) return '/admin/settings';
        return pathname;
    })();

    return (
        <Sider
            trigger={null}
            collapsible
            collapsed={collapsed}
            theme="light"
            width={260}
            collapsedWidth={80}
            style={{
                boxShadow: '2px 0 8px rgba(0,0,0,0.05)',
                zIndex: 1001,
                display: 'flex',
                flexDirection: 'column'
            }}
        >
            <FitLogo collapsed={collapsed} />

            <Menu
                mode="inline"
                defaultSelectedKeys={['/dashboard']}
                selectedKeys={[selectedKey]}
                items={getMenuItems(userRole)}
                onClick={({ key }) => router.push(key)}
                style={{ borderRight: 0, padding: '0 8px', flex: 1 }}
            />

            {/* Collapse Toggle Button */}
            <div style={{
                padding: '12px 16px',
                borderTop: '1px solid #f0f0f0',
                display: 'flex',
                justifyContent: collapsed ? 'center' : 'flex-end'
            }}>
                <Tooltip title={collapsed ? 'Mở rộng menu' : 'Thu gọn menu'} placement="right">
                    <Button
                        type="text"
                        icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                        onClick={() => onCollapse(!collapsed)}
                        style={{
                            fontSize: '16px',
                            width: collapsed ? 40 : 'auto',
                            height: 40,
                            borderRadius: 8,
                            color: '#666'
                        }}
                    >
                        {!collapsed && 'Thu gọn'}
                    </Button>
                </Tooltip>
            </div>
        </Sider>
    );
};

export default MainSidebar;
