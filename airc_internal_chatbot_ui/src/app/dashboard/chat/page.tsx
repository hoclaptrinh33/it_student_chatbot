'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
    Input, Button, Typography,
    Space, Select, Tooltip
} from 'antd';
import { SendOutlined, AudioOutlined } from '@ant-design/icons';
import Image from 'next/image';
import useChatStore from '@/stores/chatStore';
import useDatasetStore from '@/stores/datasetStore';
import StudentChat from '@/components/Student/StudentChat';
import ChatSidebar from './ChatSidebar';
import useAuthStore from '@/stores/authStore';
import LiveVoiceModal from '@/components/VoiceBot/LiveVoiceModal';
import AuthGuard from '@/components/Auth/AuthGuard';
import { chatbotService } from '@/services/chatbotService';
import { Chatbot } from '@/types/chatbot';
import ChatTranscript from '@/components/Chat/ChatTranscript';
import { useChatBranches } from '@/hooks/useChatBranches';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

export default function ChatPage() {
    const { user } = useAuthStore();
    const {
        messages, loading: chatLoading, chatbotId,
        sendMessage, loadSessions, selectChatbot,
    } = useChatStore();
    const { getBranchesAt } = useChatBranches();

    const { fetchDatasets } = useDatasetStore();

    const [input, setInput] = useState('');
    const [chatbots, setChatbots] = useState<Chatbot[]>([]);
    const [isLiveVoiceOpen, setIsLiveVoiceOpen] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const lastUserIdRef = useRef<string | null>(null);
    const isInitializedRef = useRef(false);

    // Initialize chat - load chatbots, datasets, sessions
    useEffect(() => {
        if (!user?.id) return;

        // Check if user changed or first init
        const userChanged = lastUserIdRef.current !== null && user.id !== lastUserIdRef.current;
        const shouldInitialize = !isInitializedRef.current || userChanged;

        if (!shouldInitialize) return;

        const initializeChat = async () => {
            try {
                // Fetch Chatbots - API trả về theo role/user
                const data = await chatbotService.getChatbots();
                setChatbots(data);
                console.log('[ChatPage] Available chatbots:', data.map(c => ({ id: c.id, name: c.name })));

                // Luôn chọn chatbot đầu tiên
                if (data.length > 0) {
                    selectChatbot(data[0].id, data[0].dataset_ids);
                    console.log('[ChatPage] Selected chatbot:', data[0].name);
                }

                // Fetch datasets and sessions
                await Promise.all([
                    fetchDatasets(),
                    loadSessions()
                ]);

                // Update refs after successful init
                lastUserIdRef.current = user.id;
                isInitializedRef.current = true;
            } catch (err) {
                console.error("Failed to initialize chat", err);
                lastUserIdRef.current = user.id;
                isInitializedRef.current = true;
            }
        };

        initializeChat();
    }, [user?.id, selectChatbot, fetchDatasets, loadSessions]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || chatLoading) return;

        const question = input;
        setInput('');
        await sendMessage(question);
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleChatbotChange = (value: string) => {
        const bot = chatbots.find(c => c.id === value);
        selectChatbot(value, bot?.dataset_ids || []);
    };

    // STUDENT VIEW: Use StudentChat component
    if (user?.role === 'student') {
        return (
            <AuthGuard>
                <StudentChat />
            </AuthGuard>
        );
    }

    const currentChatbot = chatbots.find(c => c.id === chatbotId);

    return (
        <AuthGuard>
            <div className="h-[calc(100vh-96px)] flex flex-col md:flex-row border border-gray-200 rounded-lg shadow-sm overflow-hidden bg-white">
                {/* Left Sidebar: Session & Dataset Manager */}
                <div className="w-full md:w-80 shrink-0 h-full border-b md:border-b-0 md:border-r border-gray-200">
                    <ChatSidebar className="h-full" />
                </div>

                {/* Main Chat Area */}
                <div className="flex-1 flex flex-col h-full bg-white">
                    <div className="p-4 border-b flex justify-between items-center bg-white rounded-t-lg">
                        <Space>
                            <Image
                                src="/logo_fit.png"
                                alt="Khoa CNTT"
                                width={48}
                                height={48}
                                className="object-contain"
                            />
                            <div>
                                {chatbots.length > 1 ? (
                                    <Space direction="vertical" size={0}>
                                        <Text type="secondary" className="text-xs">Trợ lý hiện tại</Text>
                                        <Select
                                            value={chatbotId}
                                            onChange={handleChatbotChange}
                                            style={{ width: 220, fontWeight: 600 }}
                                            bordered={false}
                                            className="-ml-3"
                                            dropdownMatchSelectWidth={false}
                                        >
                                            {chatbots.map(bot => (
                                                <Option key={bot.id} value={bot.id}>{bot.name}</Option>
                                            ))}
                                        </Select>
                                    </Space>
                                ) : (
                                    <Title level={5} className="mb-0">
                                        {currentChatbot?.name || "Cố vấn Học tập Khoa CNTT"}
                                    </Title>
                                )}
                            </div>
                        </Space>
                    </div>

                    {/* Messages List */}
                    <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
                        <ChatTranscript
                            getBranchesAt={getBranchesAt}
                            emptyHint={
                                <div className="flex flex-col items-center">
                                    <div className="w-24 h-24 mb-6">
                                        <Image src="/logo_fit.png" alt="Khoa CNTT" width={96} height={96} className="object-contain" />
                                    </div>
                                    <Title level={4} style={{ color: '#bfbfbf' }}>Trợ lý Cố vấn Học tập Khoa CNTT</Title>
                                    <Text type="secondary">Hỏi về môn đủ điều kiện, bảng điểm, lộ trình, hoặc tài liệu học tập.</Text>
                                </div>
                            }
                        />
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="p-4 bg-white border-t border-gray-100">
                        <div className="max-w-3xl mx-auto relative">
                            <div className="flex gap-2 items-end bg-white border border-gray-200 rounded-2xl p-2 shadow-sm focus-within:ring-2 focus-within:ring-teal-100 focus-within:border-[#0F4C81] transition-all">
                                <TextArea
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={handleKeyPress}
                                    placeholder="Hỏi về môn đủ ĐK, học lại, lộ trình Web/AI..."
                                    autoSize={{ minRows: 1, maxRows: 6 }}
                                    className="border-none shadow-none bg-transparent text-[16px] px-3 py-2 focus:ring-0 focus:border-transparent"
                                    style={{ resize: 'none' }}
                                    disabled={chatLoading}
                                    bordered={false}
                                    variant="borderless"
                                />
                                <Tooltip title={!chatbotId ? 'Hãy chọn chatbot trước khi bật Live Mode' : 'Bật Live Voice Mode'}>
                                    <Button
                                        type="default"
                                        shape="circle"
                                        size="large"
                                        icon={<AudioOutlined style={{ color: '#0F4C81' }} />}
                                        onClick={() => setIsLiveVoiceOpen(true)}
                                        disabled={chatLoading || !chatbotId}
                                        className="mb-0.5 border-gray-200 hover:border-[#0F4C81] flex items-center justify-center"
                                    />
                                </Tooltip>
                                <Button
                                    type="primary"
                                    shape="circle"
                                    size="large"
                                    icon={<SendOutlined />}
                                    onClick={handleSend}
                                    disabled={!input.trim() || chatLoading}
                                    loading={chatLoading}
                                    className={`mb-0.5 mr-0.5 shadow-md flex items-center justify-center ${
                                        input.trim() && !chatLoading
                                            ? 'border-none text-white'
                                            : 'bg-gray-100 text-gray-400 border-none'
                                    }`}
                                    style={input.trim() && !chatLoading ? { background: '#0F4C81' } : undefined}
                                />
                            </div>
                            <div className="mt-2 text-xs text-gray-400 text-center">
                                Cố vấn dựa trên bảng điểm trong hệ thống. Vui lòng kiểm tra lại thông tin quan trọng.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {isLiveVoiceOpen && (
                <LiveVoiceModal onClose={() => setIsLiveVoiceOpen(false)} />
            )}
        </AuthGuard>
    );
}
