'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadAPI } from '@/lib/api';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';

interface UploadZoneProps {
  onUploadSuccess: (fileId: string, columns: string[], filename: string) => void;
}

export function UploadZone({ onUploadSuccess }: UploadZoneProps) {
  const [uploading, setUploading] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const onDrop = useCallback(async (files: File[]) => {
    const file = files[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setSuccess(false);
    setFileName(file.name);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const { data } = await uploadAPI.uploadFile(formData);
      setSuccess(true);
      onUploadSuccess(data.file_id, data.columns, data.filename);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 
      'text/csv': ['.csv'], 
      'application/vnd.ms-excel': ['.xlsx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all
        ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-slate-400'}
        ${success ? 'border-green-500 bg-green-50' : ''}
        ${error ? 'border-red-500 bg-red-50' : ''}
      `}
    >
      <input {...getInputProps()} />
      
      {uploading ? (
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-blue-600">Uploading {fileName}...</p>
        </div>
      ) : success ? (
        <div className="flex flex-col items-center">
          <CheckCircle className="h-12 w-12 text-green-600 mb-4" />
          <p className="text-green-600 font-medium">{fileName} — ready for analysis</p>
        </div>
      ) : error ? (
        <div className="flex flex-col items-center">
          <AlertCircle className="h-12 w-12 text-red-600 mb-4" />
          <p className="text-red-600">{error}</p>
          <p className="text-slate-500 mt-2">Click to try again</p>
        </div>
      ) : (
        <div className="flex flex-col items-center">
          {isDragActive ? (
            <Upload className="h-12 w-12 text-blue-600 mb-4" />
          ) : (
            <FileText className="h-12 w-12 text-slate-400 mb-4" />
          )}
          <p className="text-slate-600">
            {isDragActive 
              ? 'Drop your CSV here' 
              : 'Drag & drop your CSV or XLSX file here'}
          </p>
          <p className="text-slate-400 text-sm mt-2">Maximum file size: 10MB</p>
        </div>
      )}
    </div>
  );
}