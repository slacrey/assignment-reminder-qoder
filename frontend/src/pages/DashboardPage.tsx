import { useEffect, useState } from 'react';
import { Card, Statistic, Row, Col, Tag } from 'antd';
import { ClockCircleOutlined, CheckCircleOutlined, TeamOutlined } from '@ant-design/icons';
import { assignmentApi, type Assignment } from '../api/assignments';
import { childApi, type Child } from '../api/children';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
dayjs.extend(utc);

export default function DashboardPage() {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [children, setChildren] = useState<Child[]>([]);

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
      // ignore
    }
  };

  const pendingCount = assignments.filter((a) => a.status === 'pending').length;
  const sentCount = assignments.filter((a) => a.status === 'sent').length;
  const todayReminders = assignments.filter(
    (a) => a.status === 'pending' && dayjs.utc(a.remind_at).local().isSame(dayjs(), 'day')
  );

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>仪表盘</h2>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic title="孩子数量" value={children.length} prefix={<TeamOutlined />} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="待提醒作业" value={pendingCount} prefix={<ClockCircleOutlined />} valueStyle={{ color: '#faad14' }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="已发送提醒" value={sentCount} prefix={<CheckCircleOutlined />} valueStyle={{ color: '#52c41a' }} />
          </Card>
        </Col>
      </Row>

      <Card title="今日待提醒" style={{ marginBottom: 24 }}>
        {todayReminders.length === 0 ? (
          <p style={{ color: '#999' }}>今天没有待提醒的作业</p>
        ) : (
          todayReminders.map((a) => (
            <div key={a.id} style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
              <span style={{ fontWeight: 500 }}>{a.title}</span>
              <Tag color="blue" style={{ marginLeft: 8 }}>{a.child_name}</Tag>
              <Tag color="orange">{dayjs.utc(a.remind_at).local().format('HH:mm')}</Tag>
            </div>
          ))
        )}
      </Card>

      <Card title="最近作业">
        {assignments.slice(0, 5).map((a) => (
          <div key={a.id} style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
            <span style={{ fontWeight: 500 }}>{a.title}</span>
            <Tag color="blue" style={{ marginLeft: 8 }}>{a.child_name}</Tag>
            <Tag color={a.status === 'pending' ? 'orange' : 'green'}>
              {a.status === 'pending' ? '待提醒' : '已发送'}
            </Tag>
            <span style={{ float: 'right', color: '#999' }}>{dayjs.utc(a.remind_at).local().format('YYYY-MM-DD HH:mm')}</span>
          </div>
        ))}
      </Card>
    </div>
  );
}
