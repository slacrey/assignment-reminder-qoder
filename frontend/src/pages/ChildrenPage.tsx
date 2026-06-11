import { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, message, Popconfirm, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { childApi, type Child, type ChildCreateRequest, type ChildUpdateRequest } from '../api/children';

export default function ChildrenPage() {
  const [children, setChildren] = useState<Child[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingChild, setEditingChild] = useState<Child | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadChildren();
  }, []);

  const loadChildren = async () => {
    try {
      const res = await childApi.list();
      setChildren(res.data);
    } catch {
      message.error('加载孩子列表失败');
    }
  };

  const openCreate = () => {
    setEditingChild(null);
    form.resetFields();
    setModalOpen(true);
  };

  const openEdit = (child: Child) => {
    setEditingChild(child);
    form.setFieldsValue(child);
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingChild) {
        await childApi.update(editingChild.id, values as ChildUpdateRequest);
        message.success('更新成功');
      } else {
        await childApi.create(values as ChildCreateRequest);
        message.success('添加成功');
      }
      setModalOpen(false);
      loadChildren();
    } catch (err: any) {
      if (err.response) {
        message.error(err.response?.data?.detail || '操作失败');
      }
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await childApi.delete(id);
      message.success('删除成功');
      loadChildren();
    } catch {
      message.error('删除失败');
    }
  };

  const columns = [
    { title: '姓名', dataIndex: 'name', key: 'name' },
    { title: 'QQ号', dataIndex: 'qq_number', key: 'qq_number', render: (v: string) => v || <Tag>未绑定</Tag> },
    { title: '邮箱', dataIndex: 'email', key: 'email' },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Child) => (
        <>
          <Button type="link" icon={<EditOutlined />} onClick={() => openEdit(record)}>
            编辑
          </Button>
          <Popconfirm title="确定删除？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>孩子管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          添加孩子
        </Button>
      </div>

      <Table columns={columns} dataSource={children} rowKey="id" />

      <Modal
        title={editingChild ? '编辑孩子' : '添加孩子'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="姓名" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input placeholder="孩子姓名" />
          </Form.Item>
          <Form.Item name="email" label="邮箱" rules={[{ required: true, message: '请输入邮箱' }, { type: 'email', message: '邮箱格式不正确' }]}>
            <Input placeholder="用于接收提醒邮件" />
          </Form.Item>
          <Form.Item name="qq_number" label="QQ号">
            <Input placeholder="选填，后续扩展QQ通知" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
