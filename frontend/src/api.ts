import axios from 'axios';
import type { DocumentInfo, DocumentStatusResponse, AnalysisResponse } from './types';

const api = axios.create({
  baseURL: '/api',
  timeout: 180000,
});

export const uploadDocument = async (file: File): Promise<DocumentInfo> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<DocumentInfo>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const ingestText = async (text: string, title?: string): Promise<DocumentInfo> => {
  const response = await api.post<DocumentInfo>('/documents/text', { text, title });
  return response.data;
};

export const ingestUrl = async (url: string, title?: string): Promise<DocumentInfo> => {
  const response = await api.post<DocumentInfo>('/documents/url', { url, title });
  return response.data;
};

export const getDocumentStatus = async (id: string): Promise<DocumentStatusResponse> => {
  const response = await api.get<DocumentStatusResponse>(`/documents/${id}/status`);
  return response.data;
};

export const analyzeDocument = async (
  id: string,
  options: {
    instructions?: string;
    topic_of_interest?: string;
    detail_level: string;
    confirm_healthcare_override?: boolean;
  }
): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>(`/documents/${id}/analyze`, options);
  return response.data;
};

export const getSummary = async (id: string): Promise<AnalysisResponse> => {
  const response = await api.get<AnalysisResponse>(`/documents/${id}/summary`);
  return response.data;
};
