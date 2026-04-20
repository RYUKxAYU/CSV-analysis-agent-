'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { sessionsAPI } from '@/lib/api';
import { UploadZone } from '@/components/UploadZone';
import { DataPreview } from '@/components/DataPreview';
import { ChatWindow } from '@/components/ChatWindow';
import { Plus, LogOut, FileText, Trash2 } from 'lucide-react';

interface Session {
  id: string;
  title: string;
  file_id: string | null;
  original_name: string | null;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSession, setCurrentSession] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<{fileId: string, columns: string[], filename: string, rows: number} | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = Cookies.get('access_token');
    if (!token) {
      router.push('/login');
      return;
    }
    loadSessions();
  }, [router]);

  const loadSessions = async () => {
    try {
      const response = await sessionsAPI.list();
      setSessions(response.data.sessions || []);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = async (fileId: string, columns: string[], filename: string) => {
    try {
      // Create a new session with the uploaded file
      const response = await sessionsAPI.create({
        file_id: fileId,
        title: filename.replace(/\.(csv|xlsx)$/i, '').replace(/_/g, ' ').title() + ' Analysis'
      });
      
      const session = response.data.session;
      setCurrentSession(session.id);
      setUploadedFile({ fileId, columns, filename, rows: 0 });
      loadSessions();
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const handleLogout = () => {
    Cookies.remove('access_token');
    Cookies.remove('user_id');
    router.push('/login');
  };

  const handleNewChat = () => {
    setCurrentSession(null);
    setUploadedFile(null);
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this session?')) return;
    
    try {
      await sessionsAPI.delete(sessionId);
      if (currentSession === sessionId) {
        handleNewChat();
      }
      loadSessions();
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-900">DataLens AI</h1>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 text-slate-600 hover:text-slate-900"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Sidebar - Sessions */}
          <div className="col-span-3">
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-slate-900">Sessions</h2>
                <button
                  onClick={handleNewChat}
                  className="p-2 hover:bg-slate-100 rounded-lg"
                  title="New Chat"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>

              <div className="space-y-2">
                {sessions.length === 0 ? (
                  <p className="text-slate-400 text-sm text-center py-4">
                    No sessions yet. Upload a file to start.
                  </p>
                ) : (
                  sessions.map(session => (
                    <div
                      key={session.id}
                      onClick={() => setCurrentSession(session.id)}
                      className={`p-3 rounded-lg cursor-pointer flex items-center justify-between group
                        ${currentSession === session.id 
                          ? 'bg-blue-50 border border-blue-200' 
                          : 'hover:bg-slate-50 border border-transparent'
                        }
                      `}
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <FileText className="h-4 w-4 text-slate-400 flex-shrink-0" />
                        <span className="text-sm text-slate-700 truncate">
                          {session.title || 'Untitled'}
                        </span>
                      </div>
                      <button
                        onClick={(e) => handleDeleteSession(session.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded"
                      >
                        <Trash2 className="h-3 w-3 text-red-500" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="col-span-9 space-y-6">
            {!uploadedFile ? (
              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Upload Your Data</h2>
                <UploadZone onUploadSuccess={handleUploadSuccess} />
              </div>
            ) : currentSession ? (
              <div className="space-y-6">
                <DataPreview
                  filename={uploadedFile.filename}
                  columns={uploadedFile.columns}
                  rows={uploadedFile.rows}
                />
                <ChatWindow
                  sessionId={currentSession}
                  onNewChat={handleNewChat}
                />
              </div>
            ) : null}
          </div>
        </div>
      </main>
    </div>
  );
}