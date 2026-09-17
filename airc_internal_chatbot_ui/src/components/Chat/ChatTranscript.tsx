'use client';

import React, { useEffect, useState } from 'react';
import { Avatar, Button, Tooltip } from 'antd';
import { DownloadOutlined, RobotOutlined } from '@ant-design/icons';
import ChatMessageItem from '@/components/Chat/ChatMessageItem';

import { ChatMessage } from '@/core/entities/Chat';
import chatService from '@/services/chatService';
import useChatStore from '@/stores/chatStore';

interface ChatTranscriptProps {
    getBranchesAt: (idx: number) => string[];
    emptyHint?: React.ReactNode;
}

function toMarkdown(messages: ChatMessage[]): string {
    const lines = ['# Phiên trò chuyện Cố vấn Khoa CNTT', ''];
    for (const msg of messages) {
        const who = msg.role === 'user' ? 'Người dùng' : 'Trợ lý';
        lines.push(`## ${who}`, '', msg.content || '', '');
        const sources = msg.sources || [];
        if (sources.length) {
            lines.push('### Nguồn');
            for (const group of sources) {
                for (const result of group.results || []) {
                    lines.push(`- ${result.file_name || 'Tài liệu'} (${group.dataset_name || ''})`);
                    if (result.text) lines.push(`  > ${result.text.replace(/\s+/g, ' ').slice(0, 240)}`);
                }
            }
            lines.push('');
        }
    }
    return lines.join('\n');
}

export default function ChatTranscript({ getBranchesAt, emptyHint }: ChatTranscriptProps) {
    const {
        messages, loading, currentSessionId,
        createBranch, regenerateMessage, selectSession, sendMessage,
    } = useChatStore();
    const [suggestions, setSuggestions] = useState<string[]>([]);

    useEffect(() => {
        if (messages.length > 0) return;
        let cancelled = false;
        chatService.getSuggestions().then((items) => {
            if (!cancelled) setSuggestions(items);
        }).catch(() => {
            if (!cancelled) setSuggestions([]);
        });
        return () => {
            cancelled = true;
        };
    }, [messages.length]);

    const exportMarkdown = () => {
        const blob = new Blob([toMarkdown(messages)], { type: 'text/markdown;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `cntt-advisor-${currentSessionId || 'session'}.md`;
        link.click();
        URL.revokeObjectURL(url);
    };

    if (messages.length === 0) {
        return (
            <div className="min-h-full flex flex-col justify-start items-center text-slate-400 py-2 px-1">
                {emptyHint}
                {!emptyHint && suggestions.length > 0 && (
                    <div className="flex flex-wrap justify-center gap-2 max-w-xl">
                        {suggestions.map((item) => (
                            <Button key={item} size="small" onClick={() => sendMessage(item)}>
                                {item}
                            </Button>
                        ))}
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex justify-end">
                <Tooltip title="Xuất Markdown">
                    <Button size="small" icon={<DownloadOutlined />} onClick={exportMarkdown}>
                        Xuất phiên
                    </Button>
                </Tooltip>
            </div>
            {messages.map((msg, idx) => {
                const branches = getBranchesAt(idx);
                const currentBranchIndex = branches.indexOf(currentSessionId || '');
                return (
                    <ChatMessageItem
                        key={msg.id || idx}
                        message={msg}
                        index={idx}
                        isLast={idx === messages.length - 1}
                        loading={loading}
                        onEditAndSubmit={createBranch}
                        onRegenerate={regenerateMessage}
                        branches={branches}
                        currentBranchIndex={currentBranchIndex}
                        onBranchChange={selectSession}
                    />
                );
            })}
            {loading && messages[messages.length - 1]?.role !== 'assistant' && (
                <div className="flex justify-start py-2">
                    <div className="max-w-[85%] flex gap-3 items-start">
                        <Avatar
                            icon={<RobotOutlined />}
                            className="shadow-sm shrink-0 mt-1"
                            style={{ background: 'linear-gradient(135deg, #0F4C81 0%, #0D9488 100%)' }}
                            size={36}
                        />
                        <div className="bg-white border border-slate-200/80 p-4 rounded-2xl rounded-tl-xs shadow-xs">
                            <div className="flex items-center gap-2 mb-2 pb-1 border-b border-slate-100">
                                <span className="text-xs font-semibold text-[#0F4C81]">
                                    Cố vấn Học tập Khoa CNTT
                                </span>
                                <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 ring-2 ring-emerald-100"></span>
                            </div>
                            <div className="flex items-center gap-3 py-1 px-1">
                                <div className="relative w-6 h-6 flex items-center justify-center shrink-0">
                                    <span className="absolute inset-0 rounded-full bg-[#0F4C81]/10 animate-ping"></span>
                                    <span className="absolute inset-0 rounded-full border-2 border-slate-100 border-t-[#0F4C81] border-r-[#0D9488] animate-spin"></span>
                                    <span className="absolute w-3.5 h-3.5 rounded-full border-2 border-transparent border-b-[#38bdf8] border-l-[#0D9488] animate-[spin_1.2s_linear_infinite_reverse]"></span>
                                    <span className="w-1.5 h-1.5 rounded-full bg-[#0F4C81] animate-pulse"></span>
                                </div>
                                <div className="flex items-center gap-1 text-[#0F4C81]/70">
                                    <span className="w-1.5 h-1.5 rounded-full bg-[#0F4C81] animate-bounce [animation-delay:-0.3s]"></span>
                                    <span className="w-1.5 h-1.5 rounded-full bg-[#0D9488] animate-bounce [animation-delay:-0.15s]"></span>
                                    <span className="w-1.5 h-1.5 rounded-full bg-[#38bdf8] animate-bounce"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

        </div>
    );
}
