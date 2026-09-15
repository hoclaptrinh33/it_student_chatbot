import React from 'react';
import { Layout } from 'antd';
import StudentNav from './StudentNav';

const { Content } = Layout;

interface StudentLayoutProps {
    children: React.ReactNode;
}

const StudentLayout: React.FC<StudentLayoutProps> = ({ children }) => {
    return (
        <Layout className="h-screen bg-gray-50" style={{ display: 'flex', flexDirection: 'column' }}>
            <StudentNav />
            <Content className="p-0" style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
                {children}
            </Content>
        </Layout>
    );
};

export default StudentLayout;
