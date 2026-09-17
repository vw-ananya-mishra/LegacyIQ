// Upload Page
// src/pages/UploadPage.tsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, CheckCircle, AlertCircle } from 'lucide-react';
import { useWorkbook } from '../context/WorkbookContext';
import { workbookAPI } from '../utils/api';

export default function UploadPage() {
  const navigate = useNavigate();
  const { setCurrentWorkbook } = useWorkbook();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f && f.name.endsWith('.xlsx')) {
      setFile(f);
      setError(null);
    } else {
      setError('Please select a valid Excel file (.xlsx)');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    try {
      setUploading(true);
      const workbook = await workbookAPI.upload(file);
      setResult(workbook);
      setCurrentWorkbook(workbook);
      
      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (err) {
      setError(`Upload failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            LegacyIQ
          </h1>
          <p className="text-xl text-slate-300 mb-2">
            Legacy Modernization Command Center
          </p>
          <p className="text-slate-400">
            AI-Powered Enterprise Application Modernization
          </p>
        </div>

        {/* Upload Card */}
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-8 shadow-2xl">
          <h2 className="text-2xl font-bold mb-8 text-slate-100">
            Upload Dataset
          </h2>

          {!result ? (
            <>
              {/* Drag & Drop Area */}
              <div
                className="border-2 border-dashed border-slate-600 rounded-lg p-12 text-center cursor-pointer hover:border-cyan-500 transition-colors mb-6"
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  const f = e.dataTransfer.files?.[0];
                  if (f) {
                    const event = {
                      target: { files: [f] }
                    } as any;
                    handleFileSelect(event);
                  }
                }}
              >
                <Upload className="w-16 h-16 mx-auto mb-4 text-slate-400" />
                <p className="text-lg text-slate-300 mb-2">
                  Drag and drop your file here
                </p>
                <p className="text-slate-400">
                  or click to select
                </p>
                <input
                  type="file"
                  accept=".xlsx"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-input"
                />
                <label htmlFor="file-input" className="cursor-pointer">
                  <div className="mt-4 inline-block text-cyan-400 hover:text-cyan-300">
                    Browse Files
                  </div>
                </label>
              </div>

              {/* Selected File Display */}
              {file && (
                <div className="mb-6 p-4 bg-slate-800 rounded-lg border border-slate-700">
                  <p className="text-slate-300">
                    <span className="font-semibold">Selected:</span> {file.name}
                  </p>
                  <p className="text-slate-400 text-sm">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              )}

              {/* Error Display */}
              {error && (
                <div className="mb-6 p-4 bg-red-900/20 border border-red-600 rounded-lg flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-red-200">{error}</p>
                </div>
              )}

              {/* Upload Button */}
              <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-all"
              >
                {uploading ? 'Ingesting Dataset...' : 'Upload & Analyze'}
              </button>

              {/* Info Box */}
              <div className="mt-8 p-4 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-300">
                <p className="font-semibold mb-2">Expected File:</p>
                <p>Legacy_Modernization_Synthetic_Dataset.xlsx</p>
                <p className="text-slate-400 mt-2 text-xs">
                  Should contain sheets: Applications, Code_Modules, Business_Rules, Dependencies, 
                  Data_Stores, Integrations, Test_Cases, Modernization_Backlog, Documentation_Artifacts
                </p>
              </div>
            </>
          ) : (
            <>
              {/* Success Display */}
              <div className="text-center">
                <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-400" />
                <h3 className="text-2xl font-bold text-slate-100 mb-4">
                  Dataset Ingested Successfully
                </h3>
                <div className="bg-slate-800 rounded-lg p-6 mb-6 text-left">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-slate-400">Workbook ID</p>
                      <p className="text-cyan-400 font-mono">{result.workbook_id}</p>
                    </div>
                    <div>
                      <p className="text-slate-400">Sheets</p>
                      <p className="text-slate-200">{result.sheets.length}</p>
                    </div>
                    {Object.entries(result.sheets).map(([name, count]: [string, any]) => (
                      <div key={name}>
                        <p className="text-slate-400">{name}</p>
                        <p className="text-slate-200">{count} records</p>
                      </div>
                    ))}
                  </div>
                </div>
                <p className="text-slate-400 mb-6">
                  Redirecting to dashboard...
                </p>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-slate-500 text-sm">
          <p>
            We don't migrate what we don't understand.
          </p>
          <p className="mt-2">
            Evidence → Intelligence → Parity → Risk-Aware Modernization
          </p>
        </div>
      </div>
    </div>
  );
}
