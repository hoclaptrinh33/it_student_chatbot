import type { ThemeConfig } from 'antd';

// Khoa CNTT: navy primary + teal accent (not AIRC red)
const theme: ThemeConfig = {
    token: {
        colorPrimary: '#0F4C81',
        colorInfo: '#0D9488',
        colorSuccess: '#388E3C',
        colorWarning: '#F57C00',
        colorError: '#D32F2F',
        colorLink: '#0D9488',

        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        fontSize: 14,

        borderRadius: 8,
        wireframe: false,
    },
    components: {
        Button: {
            primaryShadow: '0 2px 0 rgba(15, 76, 129, 0.1)',
            colorPrimaryHover: '#0D9488',
        },
        Layout: {
            headerBg: '#ffffff',
            bodyBg: '#f5f5f5',
            siderBg: '#ffffff',
        },
        Menu: {
            itemSelectedColor: '#0F4C81',
            itemSelectedBg: '#E8F1F8',
            itemHoverBg: '#F0FDFA',
        },
        Input: {
            activeBorderColor: '#0F4C81',
            hoverBorderColor: '#0D9488',
        }
    }
};

export default theme;
