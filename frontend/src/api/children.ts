import api from './client';

export interface Child {
  id: number;
  parent_id: number;
  name: string;
  qq_number: string;
  email: string;
  created_at: string;
}

export interface ChildCreateRequest {
  name: string;
  qq_number?: string;
  email: string;
}

export interface ChildUpdateRequest {
  name?: string;
  qq_number?: string;
  email?: string;
}

export const childApi = {
  list: () => api.get<Child[]>('/children'),
  create: (data: ChildCreateRequest) => api.post<Child>('/children', data),
  update: (id: number, data: ChildUpdateRequest) => api.put<Child>(`/children/${id}`, data),
  delete: (id: number) => api.delete(`/children/${id}`),
};
