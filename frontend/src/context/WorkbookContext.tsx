// src/context/WorkbookContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { Workbook } from '../types';

interface WorkbookContextType {
  currentWorkbook: Workbook | null;
  setCurrentWorkbook: (workbook: Workbook | null) => void;
}

const WorkbookContext = createContext<WorkbookContextType | undefined>(undefined);

export function WorkbookProvider({ children }: { children: React.ReactNode }) {
  const [currentWorkbook, setCurrentWorkbook] = useState<Workbook | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('currentWorkbook');
    if (stored) {
      try {
        setCurrentWorkbook(JSON.parse(stored));
      } catch (e) {
        console.error('Failed to load workbook from storage:', e);
      }
    }
  }, []);

  // Save to localStorage when workbook changes
  useEffect(() => {
    if (currentWorkbook) {
      localStorage.setItem('currentWorkbook', JSON.stringify(currentWorkbook));
    } else {
      localStorage.removeItem('currentWorkbook');
    }
  }, [currentWorkbook]);

  return (
    <WorkbookContext.Provider value={{ currentWorkbook, setCurrentWorkbook }}>
      {children}
    </WorkbookContext.Provider>
  );
}

export function useWorkbook() {
  const context = useContext(WorkbookContext);
  if (context === undefined) {
    throw new Error('useWorkbook must be used within WorkbookProvider');
  }
  return context;
}
