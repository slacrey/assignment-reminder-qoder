import { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, DatePicker, Select, message, Popconfirm, Tag } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
dayjs.extend(utc);
import { assignmentApi, type Assignment, type AssignmentCreateRequest } from '../api/assignments';
import { childApi, type Child } from '../api/children';

const { TextArea } = Input;

export default function AssignmentsPage() {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [children, setChildren] = useState<Child[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [assignRes, childRes] = await Promise.all([
        assignmentApi.list(),
        childApi.list(),
      ]);
      setAssignments(assignRes.data);
      setChildren(childRes.data);
    } catch {
      message.error('加载数据失败');
    }
  };

  const openCreate = () => {
    form.resetFields();
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const data: AssignmentCreateRequest = {
        ...values,
        remind_at: values.remind_at.utc().format('YYYY-MM-DDTHH:mm:ss'),
      };
      await assignmentApi.create(data);
      message.success('创建作业成功');
      setModalOpen(false);
      loadData();
    } catch (err: any) {
      if (err.response) {
        message.error(err.response?.data?.detail || '创建失败');
      }
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await assignmentApi.delete(id);
      message.success('删除成功');
      loadData();
    } catch {
      message.error('删除失败');
    }
  };

  const columns = [
    { title: '作业标题', dataIndex: 'title', key: 'title' },
    { title: '孩子', dataIndex: 'child_name', key: 'child_name', render: (v: string) => <Tag color="blue">{v}</Tag> },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
    {
      title: '提醒时间',
      dataIndex: 'remind_at',
      key: 'remind_at',
      render: (v: string) => dayjs.utc(v).local().format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (v: string) => (
        <Tag color={v === 'pending' ? 'orange' : 'green'}>{v === 'pending' ? '待提醒' : '已发送'}</Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Assignment) => (
        <Popconfirm title="确定删除？" onConfirm={() => handleDelete(record.id)}>
          <Button type="link" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>作业管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          创建作业
        </Button>
      </div>

      <Table columns={columns} dataSource={assignments} rowKey="id" />

      <Modal
        title="创建作业"
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        okText="确定"
        cancelText="取消"
        width={500}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="child_id" label="选择孩子" rules={[{ required: true, message: '请选择孩子' }]}>
            <Select placeholder="请选择孩子">
              {children.map((c) => (
                <Select.Option key={c.id} value={c.id}>
                  {c.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="title" label="作业标题" rules={[{ required: true, message: '请输入作业标题' }]}>
            <Input placeholder="例如：数学练习册第5页" />
          </Form.Item>
          <Form.Item name="description" label="作业描述">
            <TextArea rows={3} placeholder="作业详细说明（可选）" />
          </Form.Item>
          <Form.Item name="remind_at" label="提醒时间" rules={[{ required: true, message: '请选择提醒时间' }]}>
            <DatePicker
              showTime
              format="YYYY-MM-DD HH:mm"
              placeholder="选择提醒时间"
              style={{ width: '100%' }}
              disabledDate={(current) => current && current < dayjs().startOf('day')}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
