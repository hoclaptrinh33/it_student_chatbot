'use client';

import React, { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Button, Avatar, Dropdown, MenuProps } from 'antd';
import { UserOutlined, LogoutOutlined } from '@ant-design/icons';
import Image from 'next/image';
import useAuthStore from '@/stores/authStore';

const TABS = [
    { href: '/dashboard/chat', label: 'Chat' },
    { href: '/dashboard/eligible-courses', label: 'Môn đủ ĐK' },
    { href: '/dashboard/transcript', label: 'Bảng điểm' },
    { href: '/dashboard/materials', label: 'Tài liệu' },
];

const StudentNav: React.FC = () => {
    const router = useRouter();
    const pathname = usePathname();
    const { user, logout } = useAuthStore();
    const [logoFailed, setLogoFailed] = useState(false);

    const handleLogout = () => {
        logout();
        router.push('/auth/login');
    };

    const userMenu: MenuProps['items'] = [
        {
            key: 'profile',
            label: 'Hồ sơ',
            icon: <UserOutlined />,
            disabled: true,
        },
        { type: 'divider' },
        {
            key: 'logout',
            label: 'Đăng xuất',
            icon: <LogoutOutlined />,
            onClick: handleLogout,
            danger: true,
        },
    ];

    const isActive = (href: string) => pathname === href || pathname.startsWith(href + '/');

    return (
        <header className="sticky top-0 z-50 w-full border-b border-neutral-200/70 bg-white/80 backdrop-blur-md">
            <div className="mx-auto flex items-center justify-between px-4 py-3 md:px-6 max-w-7xl gap-3">
                <div
                    className="flex items-center gap-2 cursor-pointer shrink-0"
                    onClick={() => router.push('/dashboard/chat')}
                >
                    {logoFailed ? (
                        <span
                            className="flex items-center justify-center w-8 h-8 rounded-md text-white text-xs font-black"
                            style={{ background: 'linear-gradient(135deg, #0F4C81 0%, #0D9488 100%)' }}
                        >
                            CNTT
                        </span>
                    ) : (
                        <Image
                            src="/logo_fit.png"
                            alt="Khoa CNTT"
                            width={32}
                            height={32}
                            className="object-contain"
                            onError={() => setLogoFailed(true)}
                        />
                    )}
                    <span
                        className="text-lg font-bold bg-clip-text text-transparent"
                        style={{ backgroundImage: 'linear-gradient(90deg, #0F4C81, #0D9488)' }}
                    >
                        Khoa CNTT
                    </span>
                </div>

                <nav className="flex rounded-full bg-gray-100 px-1 py-1 gap-1 overflow-x-auto max-w-[55vw] sm:max-w-none">
                    {TABS.map((tab) => (
                        <Button
                            key={tab.href}
                            type="text"
                            shape="round"
                            className={`px-3 sm:px-5 h-9 font-medium whitespace-nowrap ${
                                isActive(tab.href)
                                    ? 'bg-[#0F4C81] text-white hover:!bg-[#0F4C81] hover:!text-white'
                                    : 'text-gray-600 hover:bg-white'
                            }`}
                            onClick={() => router.push(tab.href)}
                        >
                            {tab.label}
                        </Button>
                    ))}
                </nav>

                <div className="flex items-center gap-3 shrink-0">
                    <div className="hidden sm:block text-right">
                        <div className="text-sm font-medium text-gray-900">{user?.full_name || user?.email}</div>
                        <div className="text-xs text-gray-500 capitalize">{user?.role}</div>
                    </div>
                    <Dropdown menu={{ items: userMenu }} placement="bottomRight" arrow>
                        <Avatar
                            size="large"
                            icon={<UserOutlined />}
                            className="cursor-pointer"
                            style={{ background: 'linear-gradient(135deg, #0F4C81, #0D9488)' }}
                        />
                    </Dropdown>
                </div>
            </div>
        </header>
    );
};

export default StudentNav;
