'use client';

import React, { useState } from 'react';
import { Avatar, Button, Input, Space, Tooltip, message } from 'antd';
import { 
    UserOutlined, 
    RobotOutlined, 
    EditOutlined, 
    CopyOutlined, 
    ReloadOutlined, 
    CheckOutlined,
    CloseOutlined,
    SendOutlined,
    WarningOutlined,
    LikeOutlined,
    DislikeOutlined,
    SoundOutlined,
} from '@ant-design/icons';
import { ChatMessage } from '@/core/entities/Chat';
import ChatMessageContent from './ChatMessageContent';
import SourceCitations from './SourceCitations';
import dayjs from 'dayjs';
import chatService from '@/services/chatService';

interface ChatMessageItemProps {
    message: ChatMessage;
    index: number;
    isLast: boolean;
    loading: boolean;
    onEditAndSubmit: (newContent: string, index: number) => Promise<void>;
    onRegenerate: (index: number) => Promise<void>;
    branches?: string[];
    currentBranchIndex?: number;
    onBranchChange?: (sessionId: string) => void;
}

export default function ChatMessageItem({
    message: msg,
    index,
    isLast,
    loading,
    onEditAndSubmit,
    onRegenerate,
    branches = [],
    currentBranchIndex = -1,
    onBranchChange
}: ChatMessageItemProps) {
    const [isEditing, setIsEditing] = useState(false);
    const [editValue, setEditValue] = useState(msg.content);
    const [copied, setCopied] = useState(false);
    const [submitLoading, setSubmitLoading] = useState(false);
    const [feedback, setFeedback] = useState<'up' | 'down' | null>(msg.feedback ?? null);
    const [feedbackLoading, setFeedbackLoading] = useState(false);

    const isUser = msg.role === 'user';
    const isError = !isUser && (
        msg.content.startsWith('Lỗi Server AI') || 
        msg.content.startsWith('Không thể kết nối') || 
        msg.content.startsWith('Thời gian yêu cầu') ||
        msg.content.startsWith('Xin lỗi, hệ thống gặp lỗi')
    );

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(msg.content);
            setCopied(true);
            message.success('Đã sao chép nội dung tin nhắn!');
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
            message.error('Không thể sao chép tin nhắn');
        }
    };

    const handleEditSubmit = async () => {
        if (!editValue.trim()) {
            message.warning('Nội dung tin nhắn không được để trống');
            return;
        }
        if (editValue === msg.content) {
            setIsEditing(false);
            return;
        }

        setSubmitLoading(true);
        try {
            await onEditAndSubmit(editValue, index);
            setIsEditing(false);
        } catch (err) {
            console.error(err);
        } finally {
            setSubmitLoading(false);
        }
    };

    const handleRegenerate = async () => {
        try {
            await onRegenerate(index);
        } catch (err) {
            console.error(err);
        }
    };

    const [commentOpen, setCommentOpen] = useState(false);
    const [comment, setComment] = useState('');

    const handleFeedback = async (rating: 'up' | 'down', extraComment?: string) => {
        if (!msg.id || feedbackLoading) return;
        if (rating === 'down' && extraComment === undefined && feedback !== 'down') {
            setCommentOpen(true);
            return;
        }
        const next = feedback === rating && extraComment === undefined ? null : rating;
        setFeedbackLoading(true);
        try {
            if (next) {
                await chatService.submitFeedback({
                    message_id: msg.id,
                    session_id: msg.session_id,
                    rating: next,
                    comment: extraComment,
                });
                setFeedback(next);
                setCommentOpen(false);
                message.success(next === 'up' ? 'Đã ghi nhận hữu ích' : 'Đã ghi nhận góp ý');
            } else {
                setFeedback(null);
            }
        } catch (err) {
            console.error(err);
            message.error('Không lưu được đánh giá');
        } finally {
            setFeedbackLoading(false);
        }
    };

    const [isSpeaking, setIsSpeaking] = useState(false);

    const handleToggleSpeak = () => {
        if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
            message.info('Trình duyệt không hỗ trợ đọc văn bản');
            return;
        }

        if (isSpeaking) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
            return;
        }

        window.speechSynthesis.cancel();
        // Remove markdown formatting characters for clean speech
        const cleanText = msg.content
            .replace(/```[\s\S]*?```/g, 'đoạn mã')
            .replace(/`([^`]+)`/g, '$1')
            .replace(/[*#_~]/g, '')
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'vi-VN';
        utterance.rate = 1.0;

        const voices = window.speechSynthesis.getVoices();
        const viVoice = voices.find(v => v.lang.toLowerCase().replace('_', '-').startsWith('vi'));
        if (viVoice) utterance.voice = viVoice;

        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);

        setIsSpeaking(true);
        window.speechSynthesis.speak(utterance);
    };

    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} w-full group py-2.5 transition-all`}>
            <div className={`flex max-w-[90%] md:max-w-[85%] gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start`}>
                {/* Avatar */}
                {isUser ? (
                    <Avatar
                        icon={<UserOutlined />}
                        className="shadow-sm shrink-0 mt-1"
                        style={{
                            background: 'linear-gradient(135deg, #0F4C81 0%, #1E3A8A 100%)',
                        }}
                        size={36}
                    />
                ) : (
                    <Avatar
                        icon={<RobotOutlined />}
                        className="shadow-sm shrink-0 mt-1"
                        style={{
                            background: 'linear-gradient(135deg, #0F4C81 0%, #0D9488 100%)',
                        }}
                        size={36}
                    />
                )}

                {/* Bong bóng chat chính */}
                <div className="flex flex-col gap-1.5 max-w-full">
                    {/* Bong bóng nội dung */}
                    <div
                        className={`p-4 rounded-2xl shadow-xs transition-all duration-150 ${
                            isUser
                                ? 'bg-gradient-to-br from-[#0F4C81] to-[#165a96] text-white rounded-tr-xs shadow-md shadow-blue-900/10'
                                : isError
                                ? 'bg-rose-50/90 border border-rose-200 rounded-tl-xs text-rose-900'
                                : 'bg-white border border-slate-200/80 rounded-tl-xs text-slate-800 hover:border-slate-300'
                        }`}
                        style={{ minWidth: isEditing ? '320px' : 'auto' }}
                    >
                        {/* Advisor Header Badge */}
                        {!isUser && !isEditing && (
                            <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
                                <div className="flex items-center gap-1.5">
                                    <span className="text-xs font-semibold text-[#0F4C81]">
                                        Cố vấn Học tập Khoa CNTT
                                    </span>
                                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 ring-2 ring-emerald-100"></span>
                                </div>
                                <span className="text-[11px] text-slate-400">
                                    {dayjs(msg.timestamp).format('HH:mm')}
                                </span>
                            </div>
                        )}

                        {isEditing ? (
                            <div className="flex flex-col gap-2">
                                <Input.TextArea
                                    value={editValue}
                                    onChange={(e) => setEditValue(e.target.value)}
                                    autoSize={{ minRows: 2, maxRows: 6 }}
                                    className="border-slate-300 focus:border-[#0F4C81] focus:shadow-none rounded-lg"
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            handleEditSubmit();
                                        }
                                    }}
                                />
                                <div className="flex justify-end gap-2 mt-1">
                                    <Button 
                                        size="small" 
                                        icon={<CloseOutlined />} 
                                        onClick={() => {
                                            setIsEditing(false);
                                            setEditValue(msg.content);
                                        }}
                                        disabled={submitLoading}
                                        className="rounded-md"
                                    >
                                        Hủy
                                    </Button>
                                    <Button 
                                        type="primary" 
                                        size="small" 
                                        icon={<SendOutlined />} 
                                        onClick={handleEditSubmit}
                                        loading={submitLoading}
                                        className="rounded-md bg-[#0F4C81]"
                                    >
                                        Gửi & Tạo nhánh
                                    </Button>
                                </div>
                            </div>
                        ) : (
                            <div className={`prose max-w-none break-words ${isUser ? 'text-white' : isError ? 'text-rose-800' : 'text-slate-800'} flex gap-2 items-start text-[14.5px] leading-relaxed`}>
                                {isError && <WarningOutlined className="text-rose-500 mt-1 shrink-0" />}
                                <div className="flex-1">
                                    {!isUser && (!msg.content || msg.content.trim() === '') ? (
                                        <div className="flex items-center gap-3 py-2 px-1">
                                            <div className="relative w-6 h-6 flex items-center justify-center shrink-0">
                                                {/* Vòng hào quang mờ */}
                                                <span className="absolute inset-0 rounded-full bg-[#0F4C81]/10 animate-ping"></span>
                                                {/* Vòng xoay ngoài xuôi chiều */}
                                                <span className="absolute inset-0 rounded-full border-2 border-slate-100 border-t-[#0F4C81] border-r-[#0D9488] animate-spin"></span>
                                                {/* Vòng xoay trong ngược chiều */}
                                                <span className="absolute w-3.5 h-3.5 rounded-full border-2 border-transparent border-b-[#38bdf8] border-l-[#0D9488] animate-[spin_1.2s_linear_infinite_reverse]"></span>
                                                {/* Chấm tâm breathing */}
                                                <span className="w-1.5 h-1.5 rounded-full bg-[#0F4C81] animate-pulse"></span>
                                            </div>
                                            <div className="flex items-center gap-1 text-[#0F4C81]/70">
                                                <span className="w-1.5 h-1.5 rounded-full bg-[#0F4C81] animate-bounce [animation-delay:-0.3s]"></span>
                                                <span className="w-1.5 h-1.5 rounded-full bg-[#0D9488] animate-bounce [animation-delay:-0.15s]"></span>
                                                <span className="w-1.5 h-1.5 rounded-full bg-[#38bdf8] animate-bounce"></span>
                                            </div>
                                        </div>
                                    ) : (
                                        <ChatMessageContent
                                            content={msg.content}
                                            isUser={isUser}
                                            sources={msg.sources}
                                        />
                                    )}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Meta info & Toolbar bên dưới bong bóng của AI */}
                    {!isUser && !isEditing && msg.content && (
                        <>
                            <SourceCitations sources={msg.sources} />
                            <div className="flex items-center justify-between px-1 mt-0.5 select-none">
                                <Space size={4} className="opacity-90 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity duration-150">
                                    <Tooltip title={isSpeaking ? 'Dừng đọc' : 'Nghe câu trả lời'}>
                                        <Button
                                            type="text"
                                            size="small"
                                            icon={<SoundOutlined className={isSpeaking ? 'text-[#0D9488] animate-pulse' : 'text-slate-400 hover:text-slate-700'} />}
                                            onClick={handleToggleSpeak}
                                            className="flex items-center justify-center p-1 h-7 w-7 rounded-md hover:bg-slate-100"
                                        />
                                    </Tooltip>
                                    <Tooltip title="Hữu ích">
                                        <Button
                                            type="text"
                                            size="small"
                                            icon={<LikeOutlined className={feedback === 'up' ? 'text-emerald-600' : 'text-slate-400 hover:text-slate-700'} />}
                                            onClick={() => handleFeedback('up')}
                                            loading={feedbackLoading}
                                            disabled={!msg.id}
                                            className="flex items-center justify-center p-1 h-7 w-7 rounded-md hover:bg-slate-100"
                                        />
                                    </Tooltip>
                                    <Tooltip title="Chưa chính xác">
                                        <Button
                                            type="text"
                                            size="small"
                                            icon={<DislikeOutlined className={feedback === 'down' ? 'text-rose-500' : 'text-slate-400 hover:text-slate-700'} />}
                                            onClick={() => handleFeedback('down')}
                                            loading={feedbackLoading}
                                            disabled={!msg.id}
                                            className="flex items-center justify-center p-1 h-7 w-7 rounded-md hover:bg-slate-100"
                                        />
                                    </Tooltip>
                                    <Tooltip title="Sao chép câu trả lời">
                                        <Button
                                            type="text"
                                            size="small"
                                            icon={copied ? <CheckOutlined className="text-emerald-500" /> : <CopyOutlined className="text-slate-400 hover:text-slate-700" />}
                                            onClick={handleCopy}
                                            className="flex items-center justify-center p-1 h-7 w-7 rounded-md hover:bg-slate-100"
                                        />
                                    </Tooltip>
                                    {isLast && (
                                        <Tooltip title="Tạo lại câu trả lời">
                                            <Button
                                                type="text"
                                                size="small"
                                                icon={<ReloadOutlined className="text-slate-400 hover:text-[#0F4C81]" />}
                                                onClick={handleRegenerate}
                                                disabled={loading}
                                                className="flex items-center justify-center p-1 h-7 w-7 rounded-md hover:bg-slate-100"
                                            />
                                        </Tooltip>
                                    )}
                                </Space>
                            </div>
                            {commentOpen && (
                                <div className="mt-2 flex flex-col gap-2 bg-slate-50 border border-slate-200 rounded-xl p-3 shadow-xs">
                                    <Input.TextArea
                                        value={comment}
                                        onChange={(e) => setComment(e.target.value)}
                                        placeholder="Em thấy câu trả lời này chưa đúng ở điểm nào? (không bắt buộc)"
                                        autoSize={{ minRows: 2, maxRows: 4 }}
                                        className="rounded-lg"
                                    />
                                    <div className="flex justify-end gap-2">
                                        <Button size="small" onClick={() => setCommentOpen(false)} className="rounded-md">Hủy</Button>
                                        <Button
                                            size="small"
                                            type="primary"
                                            onClick={() => handleFeedback('down', comment.trim())}
                                            loading={feedbackLoading}
                                            className="rounded-md bg-[#0F4C81]"
                                        >
                                            Gửi góp ý
                                        </Button>
                                    </div>
                                </div>
                            )}
                        </>
                    )}

                    {/* Meta info & Toolbar của User */}
                    {isUser && !isEditing && (
                        <div className="flex items-center justify-end gap-2 px-1 select-none">
                            {/* Bộ chọn nhánh (phiên bản tin nhắn cũ/mới) */}
                            {branches && branches.length > 1 && currentBranchIndex !== -1 && (
                                <span className="flex items-center gap-1 bg-slate-100 px-2.5 py-0.5 rounded-full border border-slate-200 text-[11px] text-slate-600 font-medium mr-1 select-none">
                                    <Button
                                        type="text"
                                        size="small"
                                        disabled={currentBranchIndex === 0}
                                        onClick={() => onBranchChange && onBranchChange(branches[currentBranchIndex - 1])}
                                        className="h-4 w-4 p-0 flex items-center justify-center border-none shadow-none text-slate-500 hover:text-[#0F4C81] disabled:text-slate-300 font-bold"
                                        style={{ fontSize: '10px', lineHeight: 1 }}
                                    >
                                        &lt;
                                    </Button>
                                    <span className="px-1">{currentBranchIndex + 1}/{branches.length}</span>
                                    <Button
                                        type="text"
                                        size="small"
                                        disabled={currentBranchIndex === branches.length - 1}
                                        onClick={() => onBranchChange && onBranchChange(branches[currentBranchIndex + 1])}
                                        className="h-4 w-4 p-0 flex items-center justify-center border-none shadow-none text-slate-500 hover:text-[#0F4C81] disabled:text-slate-300 font-bold"
                                        style={{ fontSize: '10px', lineHeight: 1 }}
                                    >
                                        &gt;
                                    </Button>
                                </span>
                            )}

                            {/* Toolbar User */}
                            <Space size={2} className="opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                                <Tooltip title="Chỉnh sửa tin nhắn">
                                    <Button
                                        type="text"
                                        size="small"
                                        icon={<EditOutlined className="text-slate-400 hover:text-[#0F4C81]" />}
                                        onClick={() => {
                                            setEditValue(msg.content);
                                            setIsEditing(true);
                                        }}
                                        className="flex items-center justify-center p-1 h-6 w-6 rounded-md hover:bg-slate-100"
                                    />
                                </Tooltip>
                                <Tooltip title="Sao chép">
                                    <Button
                                        type="text"
                                        size="small"
                                        icon={copied ? <CheckOutlined className="text-emerald-500" /> : <CopyOutlined className="text-slate-400 hover:text-slate-700" />}
                                        onClick={handleCopy}
                                        className="flex items-center justify-center p-1 h-6 w-6 rounded-md hover:bg-slate-100"
                                    />
                                </Tooltip>
                            </Space>

                            {/* Thời gian gửi */}
                            <span className="text-[11px] text-slate-400">
                                {dayjs(msg.timestamp).format('HH:mm')}
                            </span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
