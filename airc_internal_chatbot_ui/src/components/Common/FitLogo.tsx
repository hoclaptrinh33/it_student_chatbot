'use client';

import React, { useState } from 'react';
import Image from 'next/image';

interface FitLogoProps {
    collapsed?: boolean;
    className?: string;
}

const FitLogo: React.FC<FitLogoProps> = ({ collapsed = false, className = '' }) => {
    const [imgFailed, setImgFailed] = useState(false);

    const badge = imgFailed ? (
        <div
            className="flex items-center justify-center rounded-lg text-white font-black tracking-tight"
            style={{
                width: collapsed ? 32 : 40,
                height: collapsed ? 32 : 40,
                background: 'linear-gradient(135deg, #0F4C81 0%, #0D9488 100%)',
                fontSize: collapsed ? 10 : 11,
            }}
        >
            CNTT
        </div>
    ) : (
        <Image
            src="/logo_fit.png"
            alt="Khoa CNTT"
            width={collapsed ? 32 : 40}
            height={collapsed ? 32 : 40}
            className="object-contain rounded-md"
            priority
            onError={() => setImgFailed(true)}
        />
    );

    return (
        <div className={`flex items-center justify-center p-4 ${className}`} style={{ height: 64 }}>
            {!collapsed ? (
                <div className="flex items-center gap-2">
                    {badge}
                    <span className="text-lg font-black text-gray-800 tracking-tight">
                        Khoa <span style={{ color: '#0F4C81' }}>CNTT</span>
                    </span>
                </div>
            ) : (
                badge
            )}
        </div>
    );
};

export default FitLogo;
