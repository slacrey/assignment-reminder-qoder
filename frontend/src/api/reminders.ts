import api from './client';

export interface ReminderLog {
  id: number;
  assignment_id: number;
  channel: string;
  status: 'success' | 'failed';
  sent_at: string;
  error_message?: string;
  assignment_title?: string;
  child_name?: string;
}

export const reminderApi = {
  list: () => api.get<ReminderLog[]>('/reminders'),
};
