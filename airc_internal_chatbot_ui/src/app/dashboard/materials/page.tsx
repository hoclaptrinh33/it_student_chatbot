'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
    Card,
    Table,
    Tag,
    Typography,
    Alert,
    Empty,
    Spin,
    Select,
    Button,
    message,
    Modal,
    Form,
    Input,
    Radio,
    Popconfirm,
    Tooltip,
    Space,
    Breadcrumb,
    Row,
    Col,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
    DownloadOutlined,
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    FolderOpenOutlined,
    FileTextOutlined,
    LinkOutlined,
    SearchOutlined,
} from '@ant-design/icons';
import AuthGuard from '@/components/Auth/AuthGuard';
import academicService, {
    LearningMaterial,
    MATERIAL_TYPES,
    MATERIAL_TYPE_LABELS,
} from '@/services/academicService';
import courseService, { Course } from '@/services/courseService';
import fileService from '@/services/fileService';
import datasetService, { Dataset, DatasetFile } from '@/services/datasetService';
import useAuthStore from '@/stores/authStore';
import { AxiosError } from 'axios';

const { Title, Text } = Typography;

const TYPE_COLORS: Record<string, string> = {
    SYLLABUS: 'purple',
    SLIDE: 'cyan',
    TEXTBOOK: 'blue',
    EXAM: 'volcano',
};

function MaterialsPage() {
    const { user } = useAuthStore();
    const isTeacherOrAdmin = user?.role === 'teacher' || user?.role === 'admin';

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [materials, setMaterials] = useState<LearningMaterial[]>([]);
    const [courses, setCourses] = useState<Course[]>([]);
    const [datasets, setDatasets] = useState<Dataset[]>([]);
    const [courseId, setCourseId] = useState<string | undefined>();
    const [materialType, setMaterialType] = useState<string | undefined>();
    const [searchQuery, setSearchQuery] = useState('');
    const [openingId, setOpeningId] = useState<string | null>(null);

    // Modal state for Create / Edit
    const [modalVisible, setModalVisible] = useState(false);
    const [editingMaterial, setEditingMaterial] = useState<LearningMaterial | null>(null);
    const [attachMode, setAttachMode] = useState<'url' | 'dataset'>('url');
    const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);
    const [datasetFiles, setDatasetFiles] = useState<DatasetFile[]>([]);
    const [loadingFiles, setLoadingFiles] = useState(false);
    const [form] = Form.useForm();

    const courseMap = useMemo(() => {
        const map = new Map<string, Course>();
        courses.forEach((c) => map.set(c.id, c));
        return map;
    }, [courses]);

    // Load initial courses & datasets
    useEffect(() => {
        courseService.listCourses().then(setCourses).catch(() => setCourses([]));
        if (isTeacherOrAdmin) {
            datasetService.getDatasets().then(setDatasets).catch(() => setDatasets([]));
        }
    }, [isTeacherOrAdmin]);

    // Load dataset files when dataset selected in modal
    useEffect(() => {
        if (!selectedDatasetId) {
            setDatasetFiles([]);
            return;
        }
        setLoadingFiles(true);
        datasetService
            .getDatasetFiles(selectedDatasetId)
            .then(setDatasetFiles)
            .catch(() => setDatasetFiles([]))
            .finally(() => setLoadingFiles(false));
    }, [selectedDatasetId]);

    const loadMaterials = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const mats = await academicService.listMaterials({
                course_id: courseId,
                material_type: materialType,
            });
            setMaterials(mats || []);
        } catch (err: unknown) {
            const axiosErr = err as AxiosError<{ detail?: string }>;
            setError(axiosErr.response?.data?.detail || 'Không tải được tài liệu học tập.');
        } finally {
            setLoading(false);
        }
    }, [courseId, materialType]);

    useEffect(() => {
        loadMaterials();
    }, [loadMaterials]);

    const openFile = async (material: LearningMaterial) => {
        if (material.file_id) {
            setOpeningId(material.id);
            try {
                await fileService.openFileInBrowser(material.file_id, material.title);
            } catch (err) {
                console.error('Lỗi khi mở tài liệu:', err);
                message.error('Không thể mở tài liệu. Vui lòng kiểm tra quyền truy cập hoặc thử lại sau.');
            } finally {
                setOpeningId(null);
            }
            return;
        }

        if (material.file_url) {
            if (material.file_url.startsWith('http://') || material.file_url.startsWith('https://')) {
                window.open(material.file_url, '_blank', 'noopener,noreferrer');
                return;
            }
            message.info('Tài liệu mẫu đang được cập nhật, chưa có tệp đính kèm.');
            return;
        }

        message.warning('Chưa có tệp đính kèm cho tài liệu này.');
    };

    // Open create modal
    const openCreateModal = () => {
        setEditingMaterial(null);
        form.resetFields();
        form.setFieldsValue({
            material_type: 'SLIDE',
            course_id: courseId || (courses.length > 0 ? courses[0].id : undefined),
        });
        setAttachMode('url');
        setSelectedDatasetId(null);
        setModalVisible(true);
    };

    // Open edit modal
    const openEditModal = (record: LearningMaterial) => {
        setEditingMaterial(record);
        form.resetFields();
        form.setFieldsValue({
            title: record.title,
            course_id: record.course_id,
            material_type: record.material_type,
            file_url: record.file_url,
            file_id: record.file_id,
            dataset_id: record.dataset_id,
        });
        if (record.file_id || record.dataset_id) {
            setAttachMode('dataset');
            setSelectedDatasetId(record.dataset_id || null);
        } else {
            setAttachMode('url');
            setSelectedDatasetId(null);
        }
        setModalVisible(true);
    };

    // Save Material (Create or Update)
    const handleSave = async () => {
        try {
            const values = await form.validateFields();
            setSaving(true);

            if (editingMaterial) {
                await academicService.updateMaterial(editingMaterial.id, {
                    title: values.title,
                    course_id: values.course_id,
                    material_type: values.material_type,
                    file_url: attachMode === 'url' ? values.file_url : null,
                    file_id: attachMode === 'dataset' ? values.file_id : null,
                    dataset_id: attachMode === 'dataset' ? values.dataset_id : null,
                });
                message.success('Cập nhật tài liệu thành công!');
            } else {
                await academicService.bindMaterial({
                    title: values.title,
                    course_id: values.course_id,
                    material_type: values.material_type,
                    file_url: attachMode === 'url' ? values.file_url : null,
                    file_id: attachMode === 'dataset' ? values.file_id : null,
                    dataset_id: attachMode === 'dataset' ? values.dataset_id : null,
                });
                message.success('Thêm tài liệu học tập mới thành công!');
            }

            setModalVisible(false);
            form.resetFields();
            loadMaterials();
        } catch (err) {
            console.error('Lỗi lưu tài liệu:', err);
            message.error('Không thể lưu tài liệu. Vui lòng kiểm tra lại thông tin.');
        } finally {
            setSaving(false);
        }
    };

    // Delete Material
    const handleDelete = async (materialId: string) => {
        try {
            await academicService.deleteMaterial(materialId);
            message.success('Đã xóa tài liệu!');
            loadMaterials();
        } catch (err) {
            console.error('Lỗi xóa tài liệu:', err);
            message.error('Không thể xóa tài liệu.');
        }
    };

    // Filtered materials by search
    const filteredMaterials = useMemo(() => {
        if (!searchQuery.trim()) return materials;
        const q = searchQuery.toLowerCase().trim();
        return materials.filter((m) => {
            const course = courseMap.get(m.course_id);
            return (
                m.title?.toLowerCase().includes(q) ||
                course?.course_code?.toLowerCase().includes(q) ||
                course?.course_name?.toLowerCase().includes(q)
            );
        });
    }, [materials, searchQuery, courseMap]);

    const columns: ColumnsType<LearningMaterial> = [
        {
            title: 'Tên tài liệu',
            dataIndex: 'title',
            key: 'title',
            render: (title: string, record) => (
                <div className="flex items-start gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center shrink-0 mt-0.5">
                        <FileTextOutlined />
                    </div>
                    <div>
                        <Text strong className="text-gray-900 block">{title}</Text>
                        {record.file_url ? (
                            <span className="text-xs text-blue-500 hover:underline cursor-pointer flex items-center gap-1 mt-0.5" onClick={() => openFile(record)}>
                                <LinkOutlined /> Liên kết trực tuyến
                            </span>
                        ) : record.file_id ? (
                            <span className="text-xs text-teal-600 block mt-0.5">Tệp lưu trữ trên hệ thống</span>
                        ) : null}
                    </div>
                </div>
            ),
        },
        {
            title: 'Môn học',
            dataIndex: 'course_id',
            key: 'course_id',
            render: (id: string) => {
                const course = courseMap.get(id);
                return course ? (
                    <div>
                        <Tag color="blue" className="font-semibold">{course.course_code}</Tag>
                        <span className="text-sm text-gray-700">{course.course_name}</span>
                    </div>
                ) : (
                    <Text type="secondary">{id}</Text>
                );
            },
        },
        {
            title: 'Loại tài liệu',
            dataIndex: 'material_type',
            key: 'material_type',
            width: 140,
            align: 'center',
            render: (type: string) => (
                <Tag color={TYPE_COLORS[type] || 'default'} className="font-semibold px-2 py-0.5">
                    {MATERIAL_TYPE_LABELS[type] || type}
                </Tag>
            ),
        },
        {
            title: 'Thao tác',
            key: 'action',
            width: isTeacherOrAdmin ? 160 : 90,
            align: 'center',
            render: (_, record) => (
                <Space size={8}>
                    <Tooltip title="Mở / Xem tài liệu">
                        <Button
                            size="small"
                            icon={<DownloadOutlined />}
                            loading={openingId === record.id}
                            disabled={!record.file_id && !record.file_url}
                            onClick={() => openFile(record)}
                        />
                    </Tooltip>

                    {isTeacherOrAdmin && (
                        <>
                            <Tooltip title="Chỉnh sửa">
                                <Button
                                    size="small"
                                    icon={<EditOutlined />}
                                    onClick={() => openEditModal(record)}
                                />
                            </Tooltip>
                            <Popconfirm
                                title="Xóa tài liệu này?"
                                description="Bạn có chắc muốn xóa tài liệu khỏi môn học?"
                                onConfirm={() => handleDelete(record.id)}
                                okText="Xóa"
                                cancelText="Hủy"
                                okButtonProps={{ danger: true }}
                            >
                                <Tooltip title="Xóa">
                                    <Button size="small" danger icon={<DeleteOutlined />} />
                                </Tooltip>
                            </Popconfirm>
                        </>
                    )}
                </Space>
            ),
        },
    ];

    return (
        <AuthGuard>
            <div className="space-y-6 pb-12">
                {/* Header & Breadcrumb */}
                <div>
                    <Breadcrumb
                        items={[
                            { title: 'Bảng điều khiển', href: '/dashboard' },
                            { title: isTeacherOrAdmin ? 'Giảng dạy' : 'Sinh viên' },
                            { title: 'Tài liệu học tập' },
                        ]}
                    />
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-3">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-teal-600 text-white flex items-center justify-center shadow-md">
                                <FolderOpenOutlined style={{ fontSize: 20 }} />
                            </div>
                            <div>
                                <Title level={3} className="!mb-0">
                                    Tài liệu Học tập & Giảng dạy
                                </Title>
                                <Text type="secondary" className="text-sm">
                                    Tra cứu đề cương, slide bài giảng, giáo trình và ngân hàng đề thi theo từng môn học Khoa CNTT.
                                </Text>
                            </div>
                        </div>

                        {isTeacherOrAdmin && (
                            <Button
                                type="primary"
                                icon={<PlusOutlined />}
                                onClick={openCreateModal}
                                size="large"
                                className="!bg-[#0F4C81] font-semibold"
                            >
                                Thêm tài liệu mới
                            </Button>
                        )}
                    </div>
                </div>

                {/* Filters & Search */}
                <Card className="border-0 shadow-sm rounded-2xl p-2">
                    <Row gutter={[16, 16]} align="middle">
                        <Col xs={24} sm={10} md={8}>
                            <Input
                                prefix={<SearchOutlined className="text-gray-400" />}
                                placeholder="Tìm kiếm tài liệu hoặc môn học..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                allowClear
                                size="large"
                            />
                        </Col>
                        <Col xs={24} sm={7} md={8}>
                            <Select
                                allowClear
                                showSearch
                                placeholder="Lọc theo tất cả môn học"
                                className="w-full"
                                optionFilterProp="label"
                                value={courseId}
                                onChange={(value) => setCourseId(value)}
                                size="large"
                                options={courses.map((c) => ({
                                    value: c.id,
                                    label: `${c.course_code} · ${c.course_name}`,
                                }))}
                            />
                        </Col>
                        <Col xs={24} sm={7} md={8}>
                            <Select
                                allowClear
                                placeholder="Lọc theo loại tài liệu"
                                className="w-full"
                                value={materialType}
                                onChange={(value) => setMaterialType(value)}
                                size="large"
                                options={MATERIAL_TYPES.map((type) => ({
                                    value: type,
                                    label: MATERIAL_TYPE_LABELS[type],
                                }))}
                            />
                        </Col>
                    </Row>
                </Card>

                {/* Materials List Table */}
                <Card className="shadow-sm border-0 rounded-2xl" styles={{ body: { padding: 0 } }}>
                    {error && <Alert type="error" showIcon message={error} className="m-4" />}
                    {loading ? (
                        <div className="flex justify-center py-16">
                            <Spin size="large" />
                        </div>
                    ) : (
                        <Table
                            rowKey="id"
                            columns={columns}
                            dataSource={filteredMaterials}
                            pagination={{ pageSize: 10, showTotal: (total) => `Tổng số ${total} tài liệu` }}
                            locale={{
                                emptyText: <Empty description="Chưa có tài liệu phù hợp bộ lọc" />,
                            }}
                        />
                    )}
                </Card>

                {/* Create / Edit Modal for Teachers */}
                <Modal
                    title={editingMaterial ? 'Chỉnh sửa tài liệu học tập' : 'Đăng tải tài liệu học tập mới'}
                    open={modalVisible}
                    onCancel={() => setModalVisible(false)}
                    onOk={handleSave}
                    confirmLoading={saving}
                    okText="Lưu tài liệu"
                    cancelText="Hủy"
                    width={600}
                >
                    <Form form={form} layout="vertical" className="pt-2">
                        <Form.Item
                            name="course_id"
                            label="Môn học thuộc Khoa CNTT"
                            rules={[{ required: true, message: 'Vui lòng chọn môn học' }]}
                        >
                            <Select
                                showSearch
                                placeholder="Chọn môn học"
                                optionFilterProp="label"
                                size="large"
                                options={courses.map((c) => ({
                                    value: c.id,
                                    label: `${c.course_code} · ${c.course_name}`,
                                }))}
                            />
                        </Form.Item>

                        <Form.Item
                            name="title"
                            label="Tiêu đề tài liệu"
                            rules={[{ required: true, message: 'Vui lòng nhập tên tài liệu' }]}
                        >
                            <Input size="large" placeholder="VD: Slide Chương 3: Kế thừa và Đa hình trong OOP" />
                        </Form.Item>

                        <Form.Item
                            name="material_type"
                            label="Phân loại tài liệu"
                            rules={[{ required: true, message: 'Vui lòng chọn loại tài liệu' }]}
                        >
                            <Select size="large">
                                <Select.Option value="SYLLABUS">Đề cương chi tiết (SYLLABUS)</Select.Option>
                                <Select.Option value="SLIDE">Slide bài giảng (SLIDE)</Select.Option>
                                <Select.Option value="TEXTBOOK">Giáo trình / Sách tham khảo (TEXTBOOK)</Select.Option>
                                <Select.Option value="EXAM">Đề thi & Ngân hàng câu hỏi (EXAM)</Select.Option>
                            </Select>
                        </Form.Item>

                        <div className="mb-2 font-semibold text-gray-700 text-sm">Phương thức đính kèm tệp:</div>
                        <Radio.Group
                            value={attachMode}
                            onChange={(e) => setAttachMode(e.target.value)}
                            className="mb-4"
                        >
                            <Radio.Button value="url">Nhập liên kết (URL)</Radio.Button>
                            <Radio.Button value="dataset">Chọn từ Bộ dữ liệu AI</Radio.Button>
                        </Radio.Group>

                        {attachMode === 'url' ? (
                            <Form.Item
                                name="file_url"
                                label="Đường dẫn tài liệu trực tuyến (Google Drive, OneDrive, Web...)"
                                rules={[{ type: 'url', message: 'Vui lòng nhập đường dẫn URL hợp lệ' }]}
                            >
                                <Input size="large" placeholder="https://drive.google.com/..." />
                            </Form.Item>
                        ) : (
                            <div className="space-y-3 bg-gray-50 p-4 rounded-xl border border-gray-200">
                                <Form.Item
                                    name="dataset_id"
                                    label="Chọn Bộ dữ liệu nguồn"
                                    className="!mb-2"
                                >
                                    <Select
                                        placeholder="Chọn dataset"
                                        size="large"
                                        value={selectedDatasetId}
                                        onChange={(id) => {
                                            setSelectedDatasetId(id);
                                            form.setFieldValue('dataset_id', id);
                                            form.setFieldValue('file_id', undefined);
                                        }}
                                        options={datasets.map((d) => ({
                                            value: d.id,
                                            label: d.name,
                                        }))}
                                    />
                                </Form.Item>

                                <Form.Item
                                    name="file_id"
                                    label="Chọn tệp tài liệu trong bộ dữ liệu"
                                    className="!mb-0"
                                >
                                    <Select
                                        placeholder={loadingFiles ? 'Đang tải tệp...' : 'Chọn tệp'}
                                        size="large"
                                        loading={loadingFiles}
                                        disabled={!selectedDatasetId}
                                        options={datasetFiles.map((f) => ({
                                            value: f.id,
                                            label: `${f.file_name} (${(((f.file_size || 0)) / 1024).toFixed(0)} KB)`,
                                        }))}
                                    />
                                </Form.Item>
                            </div>
                        )}
                    </Form>
                </Modal>
            </div>
        </AuthGuard>
    );
}

export default MaterialsPage;
