// App.tsx - Main application component

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { WorkbookProvider, useWorkbook } from './context/WorkbookContext';
import Navigation from './components/common/Navigation';
import UploadPage from './pages/UploadPage';
import DashboardPage from './pages/DashboardPage';
import UnderstandPage from './pages/UnderstandPage';
import DocumentPage from './pages/DocumentPage';
import DependencyMapPage from './pages/DependencyMapPage';
import ParityLabPage from './pages/ParityLabPage';
import ModernizationPage from './pages/ModernizationPage';
import TraceabilityPage from './pages/TraceabilityPage';

function AppContent() {
  const { currentWorkbook } = useWorkbook();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      {currentWorkbook && <Navigation workbook={currentWorkbook} />}
      
      <Routes>
        <Route 
          path="/" 
          element={<UploadPage />} 
        />
        
        <Route path="/dashboard" element={currentWorkbook ? <DashboardPage workbook={currentWorkbook} /> : <UploadPage />} />
        <Route path="/understand" element={currentWorkbook ? <UnderstandPage workbook={currentWorkbook} /> : <UploadPage />} />
        <Route path="/document" element={currentWorkbook ? <DocumentPage workbook={currentWorkbook} /> : <UploadPage />} />
        <Route path="/dependencies" element={currentWorkbook ? <DependencyMapPage workbook={currentWorkbook} /> : <UploadPage />} />
        <Route path="/parity" element={currentWorkbook ? <ParityLabPage workbook={currentWorkbook} /> : <UploadPage />} />
        <Route path="/modernize" element={currentWorkbook ? <ModernizationPage workbook={currentWorkbook} /> : <UploadPage />} />
        <Route path="/traceability" element={currentWorkbook ? <TraceabilityPage workbook={currentWorkbook} /> : <UploadPage />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <Router>
      <WorkbookProvider>
        <AppContent />
      </WorkbookProvider>
    </Router>
  );
}

export default App;
