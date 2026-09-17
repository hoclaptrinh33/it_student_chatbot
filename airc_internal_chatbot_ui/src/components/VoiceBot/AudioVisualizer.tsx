'use client';

import React, { useEffect, useRef } from 'react';
import { VoiceModeState } from '@/hooks/useLiveVoiceBot';

interface AudioVisualizerProps {
    modeState: VoiceModeState;
    micAudioLevel: number;
    size?: number;
}

export default function AudioVisualizer({
    modeState,
    micAudioLevel,
    size = 280,
}: AudioVisualizerProps) {
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const animFrameRef = useRef<number | null>(null);
    const phaseRef = useRef(0);
    const micAudioLevelRef = useRef(micAudioLevel);

    useEffect(() => {
        micAudioLevelRef.current = micAudioLevel;
    }, [micAudioLevel]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let active = true;

        const render = () => {
            if (!active) return;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const baseRadius = size * 0.26;

            phaseRef.current += 0.035;
            const phase = phaseRef.current;
            const currentMicLevel = micAudioLevelRef.current;
            const signalStrength = Math.min(1, currentMicLevel / 55);
            const hasVoiceSignal = currentMicLevel >= 8;

            // Tính toán độ phồng co giãn theo trạng thái
            let pulse = 0;
            if (modeState === 'LISTENING') {
                pulse = signalStrength * (size * 0.16) + Math.sin(phase * 1.5) * 3;
            } else if (modeState === 'PROCESSING') {
                pulse = Math.sin(phase * 3.5) * 7;
            } else if (modeState === 'SPEAKING') {
                pulse = Math.sin(phase * 4) * 10 + Math.cos(phase * 2) * 5;
            } else {
                pulse = Math.sin(phase * 1.2) * 2;
            }

            const currentRadius = Math.max(12, baseRadius + pulse);

            // 1. Lớp hào quang ngoài cùng (Ambient Aura Gradient)
            const gradientAura = ctx.createRadialGradient(
                centerX,
                centerY,
                currentRadius * 0.4,
                centerX,
                centerY,
                currentRadius * 2.0
            );

            if (modeState === 'PROCESSING') {
                // Sắc xanh Cyan - Navy điện tử khi đang xử lý
                gradientAura.addColorStop(0, 'rgba(56, 189, 248, 0.45)');
                gradientAura.addColorStop(0.5, 'rgba(15, 76, 129, 0.2)');
                gradientAura.addColorStop(1, 'rgba(15, 23, 42, 0)');
            } else if (modeState === 'SPEAKING') {
                // Sắc Cyan - Indigo năng động khi Cố vấn đang nói
                gradientAura.addColorStop(0, 'rgba(14, 165, 233, 0.6)');
                gradientAura.addColorStop(0.5, 'rgba(99, 102, 241, 0.25)');
                gradientAura.addColorStop(1, 'rgba(15, 23, 42, 0)');
            } else if (modeState === 'LISTENING' && hasVoiceSignal) {
                // Sắc Ngọc bích - Teal sống động khi nhận giọng nói
                gradientAura.addColorStop(0, `rgba(16, 185, 129, ${0.4 + signalStrength * 0.4})`);
                gradientAura.addColorStop(0.5, `rgba(13, 148, 136, ${0.15 + signalStrength * 0.25})`);
                gradientAura.addColorStop(1, 'rgba(15, 23, 42, 0)');
            } else if (modeState === 'LISTENING') {
                // Sắc Teal êm dịu khi đang chờ nghe
                gradientAura.addColorStop(0, 'rgba(13, 148, 136, 0.35)');
                gradientAura.addColorStop(0.6, 'rgba(15, 76, 129, 0.12)');
                gradientAura.addColorStop(1, 'rgba(15, 23, 42, 0)');
            } else if (modeState === 'UNSUPPORTED_BROWSER' || modeState === 'MICROPHONE_DENIED') {
                gradientAura.addColorStop(0, 'rgba(245, 158, 11, 0.3)');
                gradientAura.addColorStop(0.6, 'rgba(217, 119, 6, 0.1)');
                gradientAura.addColorStop(1, 'rgba(15, 23, 42, 0)');
            } else {
                gradientAura.addColorStop(0, 'rgba(71, 85, 105, 0.3)');
                gradientAura.addColorStop(0.6, 'rgba(15, 76, 129, 0.1)');
                gradientAura.addColorStop(1, 'rgba(15, 23, 42, 0)');
            }

            ctx.fillStyle = gradientAura;
            ctx.beginPath();
            ctx.arc(centerX, centerY, currentRadius * 2.0, 0, Math.PI * 2);
            ctx.fill();

            // 2. Vòng quỹ đạo công nghệ (Orbital High-tech Rings) xoay 3D
            if (modeState === 'PROCESSING' || modeState === 'SPEAKING') {
                ctx.save();
                ctx.translate(centerX, centerY);

                // Vòng Elip 1 nghiêng 30 độ
                ctx.rotate(phase * 0.4);
                ctx.beginPath();
                ctx.ellipse(0, 0, currentRadius * 1.45, currentRadius * 0.65, Math.PI / 6, 0, Math.PI * 2);
                ctx.strokeStyle = modeState === 'SPEAKING'
                    ? 'rgba(56, 189, 248, 0.4)'
                    : 'rgba(45, 212, 191, 0.45)';
                ctx.lineWidth = 1.5;
                ctx.stroke();

                // Hạt vệ tinh nhỏ xoay trên quỹ đạo 1
                const orbitAngle1 = phase * 2;
                const orbX1 = Math.cos(orbitAngle1) * (currentRadius * 1.45);
                const orbY1 = Math.sin(orbitAngle1) * (currentRadius * 0.65);
                ctx.beginPath();
                ctx.arc(orbX1, orbY1, 3, 0, Math.PI * 2);
                ctx.fillStyle = '#38bdf8';
                ctx.shadowColor = '#38bdf8';
                ctx.shadowBlur = 8;
                ctx.fill();
                ctx.shadowBlur = 0;

                // Vòng Elip 2 ngược chiều
                ctx.rotate(-phase * 0.7);
                ctx.beginPath();
                ctx.ellipse(0, 0, currentRadius * 1.3, currentRadius * 0.55, -Math.PI / 4, 0, Math.PI * 2);
                ctx.strokeStyle = 'rgba(125, 211, 252, 0.25)';
                ctx.lineWidth = 1.2;
                ctx.stroke();

                ctx.restore();
            }

            // 3. Quả cầu năng lượng chính (Organic Wave Core Orb)
            ctx.beginPath();
            const points = 72;
            for (let i = 0; i <= points; i++) {
                const angle = (i / points) * Math.PI * 2;
                let waveAmplitude = 3;
                if (modeState === 'LISTENING') {
                    waveAmplitude = 2 + signalStrength * 12;
                } else if (modeState === 'SPEAKING') {
                    waveAmplitude = 6 + Math.sin(phase * 5) * 3;
                } else if (modeState === 'PROCESSING') {
                    waveAmplitude = 4;
                }

                const wave =
                    Math.sin(angle * 4 + phase * 2.2) * waveAmplitude +
                    Math.cos(angle * 6 - phase * 1.8) * (waveAmplitude * 0.6);
                const r = currentRadius + wave;
                const x = centerX + Math.cos(angle) * r;
                const y = centerY + Math.sin(angle) * r;

                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.closePath();

            // Phối màu Gradient cho lõi
            const coreGradient = ctx.createLinearGradient(
                centerX - currentRadius,
                centerY - currentRadius,
                centerX + currentRadius,
                centerY + currentRadius
            );

            if (modeState === 'PROCESSING') {
                coreGradient.addColorStop(0, '#7dd3fc'); // sky-300
                coreGradient.addColorStop(0.5, '#0284c7'); // sky-600
                coreGradient.addColorStop(1, '#0F4C81'); // navy
            } else if (modeState === 'SPEAKING') {
                coreGradient.addColorStop(0, '#bae6fd'); // sky-200
                coreGradient.addColorStop(0.4, '#0284c7'); // sky-600
                coreGradient.addColorStop(1, '#4338ca'); // indigo-700
            } else if (modeState === 'LISTENING' && hasVoiceSignal) {
                coreGradient.addColorStop(0, '#a7f3d0'); // emerald-200
                coreGradient.addColorStop(0.5, '#0d9488'); // teal-600
                coreGradient.addColorStop(1, '#0F4C81'); // navy
            } else if (modeState === 'LISTENING') {
                coreGradient.addColorStop(0, '#99f6e4'); // teal-200
                coreGradient.addColorStop(0.6, '#0d9488'); // teal-600
                coreGradient.addColorStop(1, '#0F4C81'); // navy
            } else if (modeState === 'UNSUPPORTED_BROWSER' || modeState === 'MICROPHONE_DENIED') {
                coreGradient.addColorStop(0, '#fde68a');
                coreGradient.addColorStop(1, '#d97706');
            } else {
                coreGradient.addColorStop(0, '#94a3b8');
                coreGradient.addColorStop(1, '#334155');
            }

            ctx.fillStyle = coreGradient;

            // Đổ bóng phát sáng (Outer Glow)
            if (modeState === 'SPEAKING') {
                ctx.shadowColor = 'rgba(14, 165, 233, 0.7)';
                ctx.shadowBlur = 24;
            } else if (modeState === 'LISTENING' && hasVoiceSignal) {
                ctx.shadowColor = `rgba(16, 185, 129, ${0.4 + signalStrength * 0.4})`;
                ctx.shadowBlur = 20 + signalStrength * 16;
            } else if (modeState === 'PROCESSING') {
                ctx.shadowColor = 'rgba(56, 189, 248, 0.6)';
                ctx.shadowBlur = 22;
            } else {
                ctx.shadowColor = 'rgba(15, 76, 129, 0.4)';
                ctx.shadowBlur = 12;
            }

            ctx.fill();
            ctx.shadowBlur = 0;

            animFrameRef.current = requestAnimationFrame(render);
        };

        render();

        return () => {
            active = false;
            if (animFrameRef.current) {
                cancelAnimationFrame(animFrameRef.current);
            }
        };
    }, [modeState, size]);

    return (
        <canvas
            ref={canvasRef}
            width={size}
            height={size}
            className="mx-auto block drop-shadow-2xl"
        />
    );
}
