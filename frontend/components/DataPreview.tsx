'use client';

import { FileText } from 'lucide-react';

interface DataPreviewProps {
  filename: string;
  columns: string[];
  rows: number;
}

export function DataPreview({ filename, columns, rows }: DataPreviewProps) {
  return (
    <div className="bg-white rounded-xl p-6 border border-slate-200">
      <div className="flex items-center gap-3 mb-4">
        <FileText className="h-5 w-5 text-blue-600" />
        <div>
          <h3 className="font-medium text-slate-900">{filename}</h3>
          <p className="text-sm text-slate-500">{rows} rows • {columns.length} columns</p>
        </div>
      </div>
      
      <div>
        <h4 className="text-sm font-medium text-slate-700 mb-2">Columns</h4>
        <div className="flex flex-wrap gap-2">
          {columns.map((col, index) => (
            <span 
              key={index}
              className="px-3 py-1 bg-slate-100 text-slate-700 text-sm rounded-full"
            >
              {col}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}