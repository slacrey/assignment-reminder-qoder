import api from './client';

export interface Assignment {
  id: number;
  parent_id: number;
  child_id: number;
  title: string;
  description: string;
  remind_at: string;
  status: 'pending' | 'sent';
  created_at: string;
  child_name?: string;
}

export interface AssignmentCreateRequest {
  child_id: number;
  title: string;
  description?: string;
  remind_at: string;
}

export interface AssignmentUpdateRequest {
  child_id?: number;
  title?: string;
  description?: string;
  remind_at?: string;
  status?: 'pending' | 'sent';
}

export const assignmentApi = {
  list: () => api.get<Assignment[]>('/assignments'),
  create: (data: AssignmentCreateRequest) => api.post<Assignment>('/assignments', data),
  update: (id: number, data: AssignmentUpdateRequest) => api.put<Assignment>(`/assignments/${id}`, data),
  delete: (id: number) => api.delete(`/assignments/${id}`),
};
