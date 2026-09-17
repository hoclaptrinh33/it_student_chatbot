'use client';

import React, { useState, useEffect, useRef, useMemo } from 'react';
import dayjs from 'dayjs';

import {
    Input,
    Button,
    Spin,
    message as antMessage,
    Tooltip,
    Drawer,
    Modal,
    Dropdown,
    MenuProps,
} from 'antd';
import {
    SendOutlined,
    PlusOutlined,
    MessageOutlined,
    DeleteOutlined,
    WarningOutlined,
    AudioOutlined,
    MenuOutlined,
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    EditOutlined,
    EllipsisOutlined,
    SearchOutlined,
    CheckCircleOutlined,
    CompassOutlined,
    LineChartOutlined,
    ReadOutlined,
    RightOutlined,
    ThunderboltOutlined,
} from '@ant-design/icons';
import useAuthStore from '@/stores/authStore';
import useChatStore from '@/stores/chatStore';
import { chatbotService } from '@/services/chatbotService';
import { Chatbot } from '@/types/chatbot';
import { ChatSession } from '@/services/chatService';
import LiveVoiceModal from '@/components/VoiceBot/LiveVoiceModal';
import ChatTranscript from '@/components/Chat/ChatTranscript';
import { useChatBranches } from '@/hooks/useChatBranches';

const { TextArea } = Input;

interface StarterPrompt {
    icon: React.ReactNode;
    title: string;
    description: string;
    prompt: string;
    cardStyle: string;
}

const STARTER_PROMPTS: StarterPrompt[] = [
    {
        icon: <CheckCircleOutlined className="text-xl text-emerald-700" />,
        title: 'Học phần đủ điều kiện đăng ký',
        description: 'Tra cứu danh sách môn học đủ điều kiện tiên quyết trong học kỳ tiếp theo.',
        prompt: 'Học kỳ tới em đủ điều kiện đăng ký những môn nào?',
        cardStyle: 'border-slate-200 bg-white hover:border-emerald-500 hover:shadow-sm',
    },
    {
        icon: <LineChartOutlined className="text-xl text-blue-700" />,
        title: 'Tư vấn cải thiện điểm học phần',
        description: 'Rà soát các môn điểm F hoặc D cần ưu tiên học lại để nâng điểm tích lũy.',
        prompt: 'Tóm tắt kết quả học tập của em: GPA hiện tại, tổng tín chỉ tích lũy và những môn nào bị điểm F hoặc D cần học lại?',
        cardStyle: 'border-slate-200 bg-white hover:border-blue-500 hover:shadow-sm',
    },
    {
        icon: <CompassOutlined className="text-xl text-indigo-700" />,
        title: 'Định hướng lộ trình chuyên ngành',
        description: 'Tham vấn các học phần theo định hướng Công nghệ Web hoặc Trí tuệ Nhân tạo.',
        prompt: 'Tư vấn cho em lộ trình các môn học chuyên ngành Công nghệ Web & Di động và Trí tuệ Nhân tạo.',
        cardStyle: 'border-slate-200 bg-white hover:border-indigo-500 hover:shadow-sm',
    },
    {
        icon: <ReadOutlined className="text-xl text-slate-700" />,
        title: 'Đề cương và tài liệu học phần',
        description: 'Tra cứu nhanh đề cương chi tiết và tài liệu học tập của các môn học trong khoa.',
        prompt: 'Tìm cho em đề cương chi tiết và tài liệu môn Cấu trúc dữ liệu và Giải thuật.',
        cardStyle: 'border-slate-200 bg-white hover:border-slate-500 hover:shadow-sm',
    },
];

export default function StudentChat() {
    const { user } = useAuthStore();
    const {
        messages,
        loading,
        sendMessage,
        loadSessions,
        sessions,
        createSession,
        selectSession,
        currentSessionId,
        deleteSession,
        renameSession,
        selectChatbot,
        chatbotId,
    } = useChatStore();
    const { getBranchesAt } = useChatBranches();

    const [inputValue, setInputValue] = useState('');
    const [isLiveVoiceOpen, setIsLiveVoiceOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [isMobile, setIsMobile] = useState(false);

    useEffect(() => {
        const updateMedia = () => {
            setIsMobile(window.innerWidth < 768);
        };
        updateMedia();
        window.addEventListener('resize', updateMedia);
        return () => window.removeEventListener('resize', updateMedia);
    }, []);

    // Rename session state
    const [isRenameModalOpen, setIsRenameModalOpen] = useState(false);
    const [renamingSessionId, setRenamingSessionId] = useState<string | null>(null);
    const [newSessionTitle, setNewSessionTitle] = useState('');

    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Selected chatbot tracking
    const [selectedChatbot, setSelectedChatbot] = useState<Chatbot | null>(null);
    const [noChatbotAvailable, setNoChatbotAvailable] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    const lastUserIdRef = useRef<string | null>(null);

    useEffect(() => {
        if (!user?.id) {
            setIsLoading(false);
            return;
        }

        const userChanged = lastUserIdRef.current !== null && user.id !== lastUserIdRef.current;
        if (!userChanged && selectedChatbot !== null) {
            setIsLoading(false);
            return;
        }

        const initializeChat = async () => {
            setIsLoading(true);
            try {
                const chatbots = await chatbotService.getChatbots();
                if (chatbots.length > 0) {
                    const chatbot = chatbots[0];
                    selectChatbot(chatbot.id, chatbot.dataset_ids);
                    setSelectedChatbot(chatbot);
                    setNoChatbotAvailable(false);
                } else {
                    setNoChatbotAvailable(true);
                    setSelectedChatbot(null);
                }

                await loadSessions();
                lastUserIdRef.current = user.id;
            } catch (err) {
                console.error('Failed to initialize chat', err);
                setNoChatbotAvailable(true);
                setSelectedChatbot(null);
            } finally {
                setIsLoading(false);
            }
        };

        initializeChat();
    }, [user?.id, selectChatbot, loadSessions, selectedChatbot]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    const handleSend = async (customText?: string) => {
        const textToSend = (customText ?? inputValue).trim();
        if (!textToSend) return;

        if (!selectedChatbot) {
            antMessage.error('Chưa có chatbot được cấu hình. Vui lòng liên hệ Quản trị viên.');
            return;
        }

        if (chatbotId !== selectedChatbot.id) {
            selectChatbot(selectedChatbot.id, selectedChatbot.dataset_ids);
            await new Promise(resolve => setTimeout(resolve, 0));
        }

        if (!customText) {
            setInputValue('');
        }
        await sendMessage(textToSend);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleCreateNewChat = async () => {
        await createSession('Cuộc trò chuyện mới');
        setMobileDrawerOpen(false);
    };

    const handleSelectSession = async (sessionId: string) => {
        await selectSession(sessionId);
        setMobileDrawerOpen(false);
    };

    const handleDeleteSession = (sessionId: string, sessionName: string) => {
        Modal.confirm({
            title: 'Xóa cuộc trò chuyện này?',
            content: `Bạn có chắc muốn xóa "${sessionName}"? Đoạn hội thoại này sẽ không thể khôi phục.`,
            okText: 'Xóa',
            okType: 'danger',
            cancelText: 'Hủy',
            onOk: async () => {
                await deleteSession(sessionId);
                antMessage.success('Đã xóa cuộc trò chuyện');
            },
        });
    };

    const openRenameModal = (session: ChatSession) => {
        setRenamingSessionId(session.id);
        setNewSessionTitle(session.name);
        setIsRenameModalOpen(true);
    };

    const handleSaveRename = async () => {
        if (!renamingSessionId || !newSessionTitle.trim()) return;
        await renameSession(renamingSessionId, newSessionTitle.trim());
        setIsRenameModalOpen(false);
        setRenamingSessionId(null);
        antMessage.success('Đã đổi tên cuộc trò chuyện');
    };

    // Filter & group sessions
    const groupedSessions = useMemo(() => {
        const filtered = sessions.filter(s =>
            !s.parent_id && s.name.toLowerCase().includes(searchTerm.toLowerCase())
        );

        const today: ChatSession[] = [];
        const yesterday: ChatSession[] = [];
        const last7Days: ChatSession[] = [];
        const older: ChatSession[] = [];

        const now = dayjs();
        const startOfToday = now.startOf('day');
        const startOfYesterday = startOfToday.subtract(1, 'day');
        const startOfLast7Days = startOfToday.subtract(7, 'day');

        for (const s of filtered) {
            const date = dayjs(s.created_at || s.updated_at);
            if (date.isAfter(startOfToday)) {
                today.push(s);
            } else if (date.isAfter(startOfYesterday)) {
                yesterday.push(s);
            } else if (date.isAfter(startOfLast7Days)) {
                last7Days.push(s);
            } else {
                older.push(s);
            }
        }

        return [
            { label: 'Hôm nay', items: today },
            { label: 'Hôm qua', items: yesterday },
            { label: '7 ngày trước', items: last7Days },
            { label: 'Cũ hơn', items: older },
        ].filter(g => g.items.length > 0);
    }, [sessions, searchTerm]);

    const activeSession = sessions.find(s => s.id === currentSessionId);
    const activeSessionTitle = activeSession?.name || 'Cuộc trò chuyện mới';

    const renderSidebarContent = () => (
        <div className="flex flex-col h-full bg-slate-50/50 text-slate-700 border-r border-slate-200">
            {/* Sidebar Header */}
            <div className="p-3.5 border-b border-slate-200/80 bg-white flex items-center justify-between">
                <span className="font-bold text-slate-800 text-sm tracking-tight">Hội thoại đã lưu</span>
                <div className="flex items-center gap-1">
                    <Tooltip title="Tạo cuộc trò chuyện mới">
                        <Button
                            type="text"
                            size="small"
                            icon={<PlusOutlined />}
                            onClick={handleCreateNewChat}
                            className="h-8 w-8 rounded-lg flex items-center justify-center text-slate-600 hover:text-[#0F4C81] hover:bg-slate-100"
                        />
                    </Tooltip>
                    {!isMobile && (
                        <Tooltip title="Thu gọn thanh lịch sử">
                            <Button
                                type="text"
                                size="small"
                                icon={<MenuFoldOutlined />}
                                onClick={() => setSidebarCollapsed(true)}
                                className="h-8 w-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-800 hover:bg-slate-100"
                            />
                        </Tooltip>
                    )}
                </div>
            </div>

            {/* New Chat Button */}
            <div className="p-3">
                <Button
                    type="primary"
                    block
                    icon={<PlusOutlined />}
                    onClick={handleCreateNewChat}
                    className="h-9 rounded-lg font-semibold shadow-xs flex items-center justify-center gap-2 border-none bg-[#0F4C81] hover:bg-[#165a96] transition-colors"
                >
                    Cuộc trò chuyện mới
                </Button>
            </div>

            {/* Search Input */}
            <div className="px-3 pb-2">
                <Input
                    placeholder="Tìm cuộc trò chuyện..."
                    prefix={<SearchOutlined className="text-slate-400 text-xs" />}
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                    allowClear
                    className="rounded-lg bg-white border-slate-200 text-xs py-1.5 focus:border-[#0F4C81] transition-all"
                />
            </div>

            {/* Sessions List */}
            <div className="flex-1 overflow-y-auto px-2 space-y-3 py-1">
                {groupedSessions.length === 0 ? (
                    <div className="py-12 text-center text-slate-400 px-4">
                        <MessageOutlined className="text-2xl mb-2 text-slate-300" />
                        <p className="text-xs">{searchTerm ? 'Không tìm thấy cuộc trò chuyện' : 'Chưa có cuộc trò chuyện nào'}</p>
                    </div>
                ) : (
                    groupedSessions.map(group => (
                        <div key={group.label} className="space-y-0.5">
                            <div className="px-2 py-1 text-[10.5px] font-semibold text-slate-400 uppercase tracking-wider">
                                {group.label}
                            </div>
                            {group.items.map(session => {
                                const isActive = currentSessionId === session.id;
                                const menuItems: MenuProps['items'] = [
                                    {
                                        key: 'rename',
                                        label: 'Đổi tên',
                                        icon: <EditOutlined />,
                                        onClick: () => openRenameModal(session),
                                    },
                                    {
                                        type: 'divider',
                                    },
                                    {
                                        key: 'delete',
                                        label: 'Xóa đoạn chat',
                                        icon: <DeleteOutlined />,
                                        danger: true,
                                        onClick: () => handleDeleteSession(session.id, session.name),
                                    },
                                ];

                                return (
                                    <div
                                        key={session.id}
                                        onClick={() => handleSelectSession(session.id)}
                                        className={`group relative flex items-center justify-between px-2.5 py-2 rounded-lg cursor-pointer text-xs font-medium transition-all ${
                                            isActive
                                                ? 'bg-white text-[#0F4C81] font-semibold shadow-xs border border-slate-200'
                                                : 'text-slate-600 hover:bg-white hover:text-slate-900 border border-transparent'
                                        }`}
                                    >
                                        <div className="flex items-center gap-2 min-w-0 flex-1 mr-1">
                                            <MessageOutlined
                                                className={`text-xs shrink-0 ${
                                                    isActive ? 'text-[#0F4C81]' : 'text-slate-400 group-hover:text-slate-600'
                                                }`}
                                            />
                                            <span className="truncate">{session.name}</span>
                                        </div>

                                        <div className="shrink-0 flex items-center" onClick={e => e.stopPropagation()}>
                                            <Dropdown menu={{ items: menuItems }} trigger={['click']} placement="bottomRight">
                                                <Button
                                                    type="text"
                                                    size="small"
                                                    icon={<EllipsisOutlined />}
                                                    className={`h-5 w-5 p-0 rounded flex items-center justify-center text-slate-400 hover:text-slate-700 hover:bg-slate-100 ${
                                                        isActive ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
                                                    }`}
                                                />
                                            </Dropdown>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    ))
                )}
            </div>
        </div>
    );

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center bg-slate-50">
                <div className="text-center p-8 bg-white rounded-xl shadow-xs border border-slate-200">
                    <Spin size="large" />
                    <p className="mt-4 text-slate-600 font-medium text-xs">Đang kết nối hệ thống Cố vấn Học tập...</p>
                </div>
            </div>
        );
    }

    if (noChatbotAvailable || !selectedChatbot) {
        return (
            <div className="flex h-full items-center justify-center bg-slate-50 p-4">
                <div className="text-center max-w-md p-8 bg-white rounded-xl shadow-xs border border-slate-200">
                    <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-amber-50 flex items-center justify-center">
                        <WarningOutlined className="text-2xl text-amber-500" />
                    </div>
                    <h2 className="text-base font-bold text-slate-800 mb-2">Chưa có Trợ lý Cố vấn khả dụng</h2>
                    <p className="text-slate-500 text-xs mb-5 leading-relaxed">
                        Hệ thống chưa tìm thấy cấu hình Trợ lý Cố vấn học tập phù hợp với tài khoản sinh viên của bạn.
                    </p>
                    <Button
                        type="primary"
                        onClick={() => {
                            setSelectedChatbot(null);
                            setNoChatbotAvailable(false);
                            lastUserIdRef.current = null;
                        }}
                        className="rounded-lg h-9 px-5 font-medium bg-[#0F4C81]"
                    >
                        Tải lại trang
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="flex h-full w-full overflow-hidden bg-white font-sans">
            {/* Desktop Sidebar */}
            <div
                className={`bg-slate-50/50 transition-all duration-200 flex-col hidden md:flex shrink-0 ${
                    sidebarCollapsed ? 'w-0 overflow-hidden border-r-0' : 'w-72'
                }`}
            >
                {!sidebarCollapsed && renderSidebarContent()}
            </div>

            {/* Mobile Sidebar Drawer */}
            <Drawer
                placement="left"
                open={mobileDrawerOpen}
                onClose={() => setMobileDrawerOpen(false)}
                styles={{ body: { padding: 0 } }}
                width={280}
                className="md:hidden"
            >
                {renderSidebarContent()}
            </Drawer>

            {/* Main Chat Workspace */}
            <div className="flex-1 flex flex-col h-full bg-white relative overflow-hidden">
                {/* Top Header Bar */}
                <header className="h-12 border-b border-slate-200 bg-white flex items-center justify-between px-4 z-10">
                    <div className="flex items-center gap-2 min-w-0">
                        {/* Mobile: Chỉ hiển thị nút Hamburger mở Drawer */}
                        {isMobile && (
                            <Button
                                type="text"
                                icon={<MenuOutlined />}
                                onClick={() => setMobileDrawerOpen(true)}
                                className="flex items-center justify-center h-8 w-8 rounded-lg text-slate-600 hover:bg-slate-100"
                                title="Mở danh sách cuộc trò chuyện"
                            />
                        )}

                        {/* Desktop: Chỉ hiển thị nút Mở thanh lịch sử KHI thanh lịch sử ĐANG THU GỌN */}
                        {!isMobile && sidebarCollapsed && (
                            <Tooltip title="Mở thanh lịch sử">
                                <Button
                                    type="text"
                                    icon={<MenuUnfoldOutlined />}
                                    onClick={() => setSidebarCollapsed(false)}
                                    className="flex items-center justify-center h-8 w-8 rounded-lg text-slate-600 hover:text-[#0F4C81] hover:bg-slate-100"
                                />
                            </Tooltip>
                        )}

                        {/* Session Title */}
                        <div className="flex items-center gap-1.5 min-w-0">
                            <span className="font-semibold text-slate-800 text-sm truncate max-w-[220px] sm:max-w-[360px]">
                                {activeSessionTitle}
                            </span>
                            {activeSession && (
                                <Tooltip title="Đổi tên cuộc trò chuyện">
                                    <Button
                                        type="text"
                                        size="small"
                                        icon={<EditOutlined className="text-slate-400 hover:text-[#0F4C81] text-xs" />}
                                        onClick={() => openRenameModal(activeSession)}
                                        className="h-6 w-6 p-0 rounded flex items-center justify-center"
                                    />
                                </Tooltip>
                            )}
                        </div>
                    </div>

                    {/* Right side: Advisor Status & Live Voice launcher */}
                    <div className="flex items-center gap-2 shrink-0">
                        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-50 border border-slate-200 text-xs text-slate-600 font-medium">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            <span>Cố vấn Khoa CNTT</span>
                        </div>

                        {/* Live Voice Button */}
                        <Tooltip title="Trò chuyện giọng nói trực tiếp">
                            <Button
                                onClick={() => setIsLiveVoiceOpen(true)}
                                icon={<AudioOutlined className="text-[#0F4C81]" />}
                                className="h-8 px-3 rounded-lg border border-slate-200 bg-white hover:border-[#0F4C81] text-xs font-medium text-slate-700 flex items-center gap-1.5 shadow-xs"
                            >
                                <span className="relative flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-teal-500"></span>
                                </span>
                                <span className="hidden sm:inline">Live Voice</span>
                            </Button>
                        </Tooltip>
                    </div>
                </header>

                {/* Messages Body */}
                <div className="flex-1 overflow-y-auto p-4 sm:p-6 bg-slate-50/40">
                    <div className="max-w-3xl mx-auto h-full">
                        <ChatTranscript
                            getBranchesAt={getBranchesAt}
                            emptyHint={
                                <div className="pt-2 pb-6 flex flex-col items-center w-full">
                                    {/* Hero Banner */}
                                    <div className="text-center max-w-xl mb-6">
                                        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50/80 border border-blue-200 text-[#0F4C81] text-xs font-semibold mb-3">
                                            <ThunderboltOutlined />
                                            <span>Trợ lý Cố vấn Học tập Khoa CNTT</span>
                                        </div>

                                        <h1 className="text-xl sm:text-2xl font-bold text-slate-800 tracking-tight mb-2">
                                            Xin chào {user?.full_name || 'sinh viên'}
                                        </h1>
                                        <p className="text-slate-500 text-xs sm:text-sm leading-relaxed">
                                            Hệ thống hỗ trợ tra cứu môn học đủ điều kiện đăng ký, tiến độ học tập, lộ trình chuyên ngành và tài liệu học phần.
                                        </p>
                                    </div>

                                    {/* Starter Cards Grid */}
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
                                        {STARTER_PROMPTS.map((card, idx) => (
                                            <div
                                                key={idx}
                                                onClick={() => handleSend(card.prompt)}
                                                className={`group p-4 rounded-xl border transition-all duration-150 cursor-pointer flex flex-col justify-between ${card.cardStyle}`}
                                            >
                                                <div>
                                                    <div className="flex items-center justify-between mb-2">
                                                        <div className="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center border border-slate-100">
                                                            {card.icon}
                                                        </div>
                                                        <RightOutlined className="text-[10px] text-slate-300 group-hover:text-slate-600 transition-colors" />
                                                    </div>
                                                    <div className="font-semibold text-slate-800 text-xs mb-1 group-hover:text-[#0F4C81] transition-colors">
                                                        {card.title}
                                                    </div>
                                                    <div className="text-[11.5px] text-slate-500 leading-relaxed">
                                                        {card.description}
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            }
                        />
                        <div ref={messagesEndRef} />
                    </div>
                </div>

                {/* Bottom Input Area */}
                <div className="p-3 sm:p-4 bg-white border-t border-slate-200">
                    <div className="max-w-3xl mx-auto space-y-1.5">
                        {/* Clean Input Container */}
                        <div className="flex gap-2 items-end bg-white border border-slate-300 rounded-xl p-2 shadow-xs focus-within:border-[#0F4C81] focus-within:ring-1 focus-within:ring-[#0F4C81] transition-all">
                            <TextArea
                                value={inputValue}
                                onChange={e => setInputValue(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Nhập câu hỏi về môn đủ điều kiện, điểm số, lộ trình chuyên ngành, tài liệu môn học..."
                                autoSize={{ minRows: 1, maxRows: 6 }}
                                className="border-none shadow-none bg-transparent text-[14.5px] px-2 py-1.5 focus:ring-0 focus:border-transparent text-slate-800 placeholder:text-slate-400"
                                style={{ resize: 'none' }}
                                disabled={loading || !selectedChatbot}
                                bordered={false}
                                variant="borderless"
                            />

                            {/* Voice Button */}
                            <Tooltip title="Mở Live Voice">
                                <Button
                                    type="text"
                                    shape="circle"
                                    size="middle"
                                    icon={<AudioOutlined className="text-[#0F4C81] text-base" />}
                                    onClick={() => setIsLiveVoiceOpen(true)}
                                    disabled={loading || !selectedChatbot}
                                    className="mb-0.5 rounded-full hover:bg-slate-100 flex items-center justify-center h-8 w-8"
                                />
                            </Tooltip>

                            {/* Send Button */}
                            <Button
                                type="primary"
                                shape="circle"
                                size="middle"
                                icon={<SendOutlined />}
                                onClick={() => handleSend()}
                                disabled={!inputValue.trim() || loading || !selectedChatbot}
                                loading={loading}
                                className={`mb-0.5 mr-0.5 rounded-full flex items-center justify-center transition-all ${
                                    inputValue.trim() && !loading && selectedChatbot
                                        ? 'border-none text-white bg-[#0F4C81] hover:bg-[#165a96]'
                                        : 'bg-slate-100 text-slate-400 border-none'
                                }`}
                            />
                        </div>

                        {/* Helper Disclaimer */}
                        <div className="flex items-center justify-between text-[11px] text-slate-400 px-1">
                            <span>Nhấn <kbd className="px-1 py-0.5 bg-slate-100 border border-slate-200 rounded text-[10px] text-slate-500 font-mono">Enter</kbd> để gửi • <kbd className="px-1 py-0.5 bg-slate-100 border border-slate-200 rounded text-[10px] text-slate-500 font-mono">Shift+Enter</kbd> để xuống dòng</span>
                            <span className="hidden sm:inline">Khoa Công nghệ Thông tin</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Rename Session Modal */}
            <Modal
                title="Đổi tên cuộc trò chuyện"
                open={isRenameModalOpen}
                onOk={handleSaveRename}
                onCancel={() => setIsRenameModalOpen(false)}
                okText="Lưu"
                cancelText="Hủy"
                okButtonProps={{ style: { background: '#0F4C81' } }}
            >
                <div className="py-3">
                    <Input
                        value={newSessionTitle}
                        onChange={e => setNewSessionTitle(e.target.value)}
                        onPressEnter={handleSaveRename}
                        placeholder="Nhập tên cuộc trò chuyện..."
                        className="rounded-lg py-1.5"
                        autoFocus
                    />
                </div>
            </Modal>

            {/* Live Voice Modal */}
            {isLiveVoiceOpen && (
                <LiveVoiceModal onClose={() => setIsLiveVoiceOpen(false)} />
            )}
        </div>
    );
}
