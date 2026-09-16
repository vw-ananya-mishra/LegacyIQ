// API Service client
// src/utils/api.ts

import axios from 'axios';
import { Workbook, Application, CodeModule, DashboardSummary, DependencyGraphData, Risk, ParityTest, Recommendation } from '../types';

const API_BASE = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export const workbookAPI = {
  upload: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/workbook/upload', formData);
    return response.data as Workbook;
  },

  getMetadata: async (workbookId: string) => {
    const response = await apiClient.get(`/workbook/${workbookId}/metadata`);
    return response.data as Workbook;
  },

  getApplications: async (workbookId: string) => {
    const response = await apiClient.get(`/workbook/${workbookId}/applications`);
    return response.data.applications as Application[];
  },

  getModules: async (workbookId: string, appId?: string) => {
    const params = appId ? `?app_id=${appId}` : '';
    const response = await apiClient.get(`/workbook/${workbookId}/modules${params}`);
    return response.data.modules as CodeModule[];
  },

  getDependencies: async (workbookId: string) => {
    const response = await apiClient.get(`/workbook/${workbookId}/dependencies`);
    return response.data.dependencies;
  },

  getBusinessRules: async (workbookId: string) => {
    const response = await apiClient.get(`/workbook/${workbookId}/business-rules`);
    return response.data.business_rules;
  },

  getDashboardSummary: async (workbookId: string) => {
    const response = await apiClient.get(`/workbook/${workbookId}/dashboard-summary`);
    return response.data as DashboardSummary;
  },

  getRisks: async (workbookId: string) => {
    const response = await apiClient.get(`/workbook/${workbookId}/risks`);
    return response.data.risks as Risk[];
  },
};

export const agentAPI = {
  analyzeWithAgent: async (workbookId: string, agentType: string, context: Record<string, any> = {}) => {
    const response = await apiClient.post('/agent/analyze', {
      workbook_id: workbookId,
      agent_type: agentType,
      context,
    });
    return response.data;
  },

  buildDependencyGraph: async (workbookId: string, filters?: string[]) => {
    const response = await apiClient.post('/dependency-graph/analyze', {
      workbook_id: workbookId,
      filters: filters || [],
      orphan_detection: true,
      cycle_detection: true,
    });
    return response.data as DependencyGraphData;
  },
};

export const traceabilityAPI = {
  traceFinding: async (workbookId: string, findingId: string, findingType: string) => {
    const response = await apiClient.post(`/traceability/trace?workbook_id=${workbookId}&finding_id=${findingId}&finding_type=${findingType}`);
    return response.data.trace;
  },
};

export default apiClient;
