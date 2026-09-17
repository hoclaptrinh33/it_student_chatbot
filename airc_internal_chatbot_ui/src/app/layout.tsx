import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ConfigProvider } from 'antd';
import AntdRegistry from '@/lib/AntdRegistry';
import theme from '@/theme/themeConfig';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Cố vấn Học tập Khoa CNTT",
  description: "Chatbot cố vấn học tập và tài liệu Khoa Công nghệ Thông tin",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
                navigator.serviceWorker.getRegistrations().then(function(registrations) {
                  for (var r of registrations) {
                    r.unregister();
                  }
                });
              }
            `,
          }}
        />
        <AntdRegistry>
          <ConfigProvider theme={theme}>
            {children}
          </ConfigProvider>
        </AntdRegistry>
      </body>
    </html>
  );
}
