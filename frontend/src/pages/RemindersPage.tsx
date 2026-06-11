import { useEffect, useState } from 'react';
import { Table, Tag } from 'antd';
import { reminderApi, type ReminderLog } from '../api/reminders';
import { message } from 'antd';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
dayjs.extend(utc);

export default function RemindersPage() {
  const [logs, setLogs] = useState<ReminderLog[]>([]);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const res = await reminderApi.list();
      setLogs(res.data);
    } catch {
      message.error('加载提醒记录失败');
    }
  };

  const columns = [
    { title: '作业', dataIndex: 'assignment_title', key: 'assignment_title' },
    { title: '孩子', dataIndex: 'child_name', key: 'child_name', render: (v: string) => <Tag color="blue">{v}</Tag> },
    { title: '渠道', dataIndex: 'channel', key: 'channel', render: (v: string) => <Tag>{v}</Tag> },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (v: string) => (
        <Tag color={v === 'success' ? 'green' : 'red'}>{v === 'success' ? '成功' : '失败'}</Tag>
      ),
    },
    {
      title: '发送时间',
      dataIndex: 'sent_at',
      key: 'sent_at',
      render: (v: string) => dayjs.utc(v).local().format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '错误信息',
      dataIndex: 'error_message',
      key: 'error_message',
      render: (v: string) => v || '-',
    },
  ];

  return (
    <div>
      <h2 style={{ marginBottom: 16 }}>提醒记录</h2>
      <Table columns={columns} dataSource={logs} rowKey="id" />
    </div>
  );
}
