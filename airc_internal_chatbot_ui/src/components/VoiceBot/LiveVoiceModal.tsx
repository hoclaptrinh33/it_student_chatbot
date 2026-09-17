'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Button, Tooltip } from 'antd';
import {
    AudioOutlined,
    AudioMutedOutlined,
    PauseOutlined,
    CaretRightOutlined,
    CloseOutlined,
    EyeOutlined,
    EyeInvisibleOutlined,
    WarningOutlined,
    ThunderboltOutlined,
    SoundOutlined,
} from '@ant-design/icons';

import { useLiveVoiceBot } from '@/hooks/useLiveVoiceBot';
import AudioVisualizer from './AudioVisualizer';

interface LiveVoiceModalProps {
    onClose: () => void;
}

export default function LiveVoiceModal({ onClose }: LiveVoiceModalProps) {
    const [showSubtitles, setShowSubtitles] = useState(true);
    const rootRef = useRef<HTMLDivElement>(null);

    const {
        modeState,
        transcript,
        aiSubtitle,
        isMuted,
        stopLiveMode,
        toggleMute,
        togglePause,
        micAudioLevel,
        microphoneDenied,
        lastError,
        ttsEngine,
        setTtsEngine,
    } = useLiveVoiceBot();

    const isMicrophoneDenied = modeState === 'MICROPHONE_DENIED' || microphoneDenied;

    const handleClose = () => {
        stopLiveMode();
        onClose();
    };

    useEffect(() => {
        rootRef.current?.focus();
    }, []);

    useEffect(() => {
        const onKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                event.preventDefault();
                stopLiveMode();
                onClose();
            }
        };
        window.addEventListener('keydown', onKeyDown);
        return () => window.removeEventListener('keydown', onKeyDown);
    }, [stopLiveMode, onClose]);

    const getStatusText = () => {
        switch (modeState) {
            case 'IDLE':
                return 'Đang sẵn sàng kết nối giọng nói...';
            case 'UNSUPPORTED_BROWSER':
                return 'Trình duyệt không hỗ trợ Web Speech API';
            case 'MICROPHONE_DENIED':
                return 'Chưa được cấp quyền sử dụng microphone';
            case 'LISTENING':
                return isMuted ? 'Microphone đã tắt (Tạm dừng nghe)' : 'Đang lắng nghe câu hỏi của bạn...';
            case 'PROCESSING':
                return 'Cố vấn đang tra cứu và chuẩn bị phản hồi...';
            case 'SPEAKING':
                return 'Cố vấn đang giải đáp cho bạn...';
            case 'PAUSED':
                return 'Đang tạm dừng phát âm thanh';
            default:
                return '';
        }
    };

    return (
        <div
            ref={rootRef}
            tabIndex={-1}
            className="fixed inset-0 z-50 flex flex-col justify-between bg-slate-950/95 text-white backdrop-blur-2xl transition-all duration-300 p-6 sm:p-10 outline-none select-none"
        >
            {/* Top Header Bar */}
            <div className="flex items-center justify-between w-full max-w-4xl mx-auto">
                <div className="flex items-center gap-3">
                    <span className="relative flex h-3 w-3">
                        {modeState === 'LISTENING' && !isMuted && (
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                        )}
                        <span
                            className={`relative inline-flex rounded-full h-3 w-3 ${
                                modeState === 'SPEAKING'
                                    ? 'bg-cyan-400 ring-4 ring-cyan-500/20'
                                    : modeState === 'PROCESSING'
                                    ? 'bg-amber-400 ring-4 ring-amber-500/20'
                                    : modeState === 'LISTENING' && !isMuted
                                    ? 'bg-emerald-400 ring-4 ring-emerald-500/20'
                                    : 'bg-slate-500'
                            }`}
                        ></span>
                    </span>
                    <div className="flex flex-col">
                        <span className="text-base sm:text-lg font-semibold tracking-wide text-slate-100">
                            Cố vấn Giọng nói Trực tiếp
                        </span>
                        <span className="text-xs text-slate-400 font-medium">
                            Khoa Công nghệ Thông tin
                        </span>
                    </div>
                </div>

                <div className="flex items-center gap-2.5">
                    <Tooltip
                        title={
                            ttsEngine === 'browser'
                                ? 'Đang dùng giọng Trình duyệt (Tức thì, không độ trễ). Bấm để chuyển sang Edge-TTS.'
                                : 'Đang dùng giọng Edge-TTS (Tự nhiên chất lượng cao). Bấm để chuyển sang giọng Trình duyệt.'
                        }
                    >
                        <Button
                            type="text"
                            onClick={() => setTtsEngine(ttsEngine === 'browser' ? 'edge' : 'browser')}
                            className={`px-3.5 py-1 h-8 rounded-full text-xs font-medium flex items-center gap-2 border transition-all ${
                                ttsEngine === 'browser'
                                    ? 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30 hover:bg-cyan-500/25'
                                    : 'bg-white/10 text-slate-200 border-white/20 hover:bg-white/20'
                            }`}
                        >
                            {ttsEngine === 'browser' ? (
                                <>
                                    <ThunderboltOutlined className="text-cyan-400" />
                                    <span>Trình duyệt (Tức thì)</span>
                                </>
                            ) : (
                                <>
                                    <SoundOutlined className="text-teal-400" />
                                    <span>Edge-TTS (Tự nhiên)</span>
                                </>
                            )}
                        </Button>
                    </Tooltip>

                    <Tooltip title={showSubtitles ? 'Ẩn phụ đề' : 'Hiện phụ đề'}>
                        <Button
                            type="text"
                            shape="circle"
                            size="large"
                            icon={showSubtitles ? <EyeOutlined /> : <EyeInvisibleOutlined />}
                            onClick={() => setShowSubtitles((prev) => !prev)}
                            className="text-slate-300 hover:text-white hover:bg-white/10 border border-slate-800"
                        />
                    </Tooltip>
                    <Tooltip title="Thoát Live Voice">
                        <Button
                            type="text"
                            shape="circle"
                            size="large"
                            icon={<CloseOutlined />}
                            onClick={handleClose}
                            className="text-slate-300 hover:text-white hover:bg-white/10 border border-slate-800"
                        />
                    </Tooltip>
                </div>
            </div>

            {/* Central Visualizer Area */}
            <div className="flex-1 flex flex-col items-center justify-center text-center my-6">
                {modeState === 'UNSUPPORTED_BROWSER' ? (
                    <div className="max-w-md bg-amber-950/40 border border-amber-700/50 p-8 rounded-3xl text-center shadow-2xl backdrop-blur-xl">
                        <WarningOutlined className="text-5xl text-amber-400 mb-4" />
                        <h3 className="text-xl font-bold text-slate-100 mb-2">
                            Trình duyệt chưa hỗ trợ
                        </h3>
                        <p className="text-slate-300 text-sm leading-relaxed mb-4">
                            Tính năng Nhận dạng giọng nói (Web Speech API) yêu cầu trình duyệt tương thích.
                            Vui lòng sử dụng <strong>Google Chrome</strong> hoặc <strong>Microsoft Edge</strong> để trải nghiệm tính năng này.
                        </p>
                        <Button type="primary" onClick={handleClose} className="bg-[#0F4C81]">
                            Đóng
                        </Button>
                    </div>
                ) : isMicrophoneDenied ? (
                    <div className="max-w-md bg-amber-950/40 border border-amber-700/50 p-8 rounded-3xl text-center shadow-2xl backdrop-blur-xl">
                        <WarningOutlined className="text-5xl text-amber-400 mb-4" />
                        <h3 className="text-xl font-bold text-slate-100 mb-2">
                            Chưa cấp quyền microphone
                        </h3>
                        <p className="text-slate-300 text-sm leading-relaxed mb-4">
                            Hệ thống cần quyền truy cập microphone để lắng nghe câu hỏi. Hãy bấm biểu tượng ổ khóa cạnh thanh địa chỉ <strong>{typeof window !== 'undefined' ? window.location.host : 'trình duyệt'}</strong>, đặt Microphone thành <strong>Cho phép</strong>, rồi tải lại trang.
                        </p>
                        <Button type="primary" onClick={handleClose} className="bg-[#0F4C81]">
                            Đóng
                        </Button>
                    </div>
                ) : (
                    <>
                        <div className="mb-6">
                            <AudioVisualizer
                                modeState={modeState}
                                micAudioLevel={micAudioLevel}
                                size={300}
                            />
                        </div>

                        <div className="text-lg sm:text-xl font-medium text-slate-200 tracking-wide transition-all">
                            {getStatusText()}
                        </div>
                        {lastError && (
                            <div className="mt-3 max-w-md text-sm text-amber-300">
                                {lastError}
                            </div>
                        )}
                        {modeState === 'LISTENING' && (
                            <div className={`mt-2 text-xs font-semibold tracking-wider uppercase transition-all ${
                                micAudioLevel >= 8 ? 'text-emerald-400' : 'text-slate-500'
                            }`}>
                                {micAudioLevel >= 8
                                    ? `Đang nhận diện giọng nói · ${Math.round(micAudioLevel)}%`
                                    : 'Microphone đang sẵn sàng'}
                            </div>
                        )}
                    </>
                )}

                {/* Subtitle Display */}
                {showSubtitles && modeState !== 'UNSUPPORTED_BROWSER' && !isMicrophoneDenied && (
                    <div className="mt-8 max-w-2xl w-full min-h-[90px] bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 sm:p-6 backdrop-blur-xl shadow-2xl transition-all">
                        {modeState === 'SPEAKING' || modeState === 'PAUSED' ? (
                            <div>
                                <div className="text-xs uppercase tracking-wider text-cyan-400 font-semibold mb-1.5 flex items-center justify-center gap-1.5">
                                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                                    Cố vấn Khoa CNTT
                                </div>
                                <div className="text-base sm:text-lg text-slate-100 font-normal leading-relaxed">
                                    &ldquo;{aiSubtitle || '...'}&rdquo;
                                </div>
                            </div>
                        ) : (
                            <div>
                                <div className="text-xs uppercase tracking-wider text-emerald-400 font-semibold mb-1.5 flex items-center justify-center gap-1.5">
                                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                                    Sinh viên
                                </div>
                                <div className="text-base sm:text-lg text-slate-200">
                                    {transcript ? (
                                        <span>&ldquo;{transcript}&rdquo;</span>
                                    ) : (
                                        <span className="text-slate-500 italic">Hãy nói câu hỏi hoặc thắc mắc của bạn...</span>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Bottom Control Bar */}
            <div className="flex items-center justify-center gap-5 w-full max-w-md mx-auto">
                <Tooltip title={isMuted ? 'Bật Microphone' : 'Tắt Microphone'}>
                    <Button
                        type="default"
                        shape="circle"
                        size="large"
                        icon={isMuted ? <AudioMutedOutlined /> : <AudioOutlined />}
                        onClick={toggleMute}
                        disabled={modeState === 'UNSUPPORTED_BROWSER' || isMicrophoneDenied}
                        className={`h-14 w-14 text-xl flex items-center justify-center transition-all shadow-lg ${
                            isMuted
                                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 hover:bg-amber-500/30'
                                : 'bg-slate-800/90 text-slate-100 border-slate-700/80 hover:bg-slate-700 hover:border-slate-600'
                        }`}
                    />
                </Tooltip>

                {(modeState === 'SPEAKING' || modeState === 'PAUSED') && (
                    <Tooltip title={modeState === 'PAUSED' ? 'Tiếp tục phát' : 'Tạm dừng phát'}>
                        <Button
                            type="default"
                            shape="circle"
                            size="large"
                            icon={modeState === 'PAUSED' ? <CaretRightOutlined /> : <PauseOutlined />}
                            onClick={togglePause}
                            className="h-14 w-14 text-xl flex items-center justify-center bg-slate-800/90 text-slate-100 border-slate-700/80 hover:bg-slate-700 shadow-lg transition-all"
                        />
                    </Tooltip>
                )}

                <Tooltip title="Kết thúc phiên thoại">
                    <Button
                        type="primary"
                        shape="circle"
                        size="large"
                        icon={<CloseOutlined />}
                        onClick={handleClose}
                        className="h-14 w-14 text-xl flex items-center justify-center shadow-lg bg-rose-500/90 hover:bg-rose-600 text-white border-none transition-all shadow-rose-950/50"
                    />
                </Tooltip>
            </div>
        </div>
    );
}
