import React, { useState, useEffect } from 'react';
import { X, ExternalLink, Mail, Phone, MapPin, Building2, Users, MessageSquare } from 'lucide-react';
import { AutoLead, FinalLead, LeadNote } from '../../types';
import { leadNotesApi, finalLeadsApi } from '../../services/api';
import { useAuthContext } from '../../context/AuthContext';

interface LeadDetailsModalProps {
  lead: AutoLead | FinalLead;
  type: 'auto' | 'final';
  onClose: () => void;
  onUpdate: () => void;
}

export default function LeadDetailsModal({ lead, type, onClose, onUpdate }: LeadDetailsModalProps) {
  const [notes, setNotes] = useState<LeadNote[]>([]);
  const [newNote, setNewNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [notesLoading, setNotesLoading] = useState(true);
  const { profile } = useAuthContext();

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      const data = await leadNotesApi.getByLead(lead.id, type);
      setNotes(data);
    } catch (error) {
      console.error('Error fetching notes:', error);
    } finally {
      setNotesLoading(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim() || !profile) return;

    setLoading(true);
    try {
      await leadNotesApi.create({
        lead_id: lead.id,
        lead_type: type,
        note: newNote.trim(),
        is_internal: true,
        created_by: profile.id
      });
      setNewNote('');
      fetchNotes();
    } catch (error) {
      console.error('Error adding note:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (status: string) => {
    if (type === 'final') {
      try {
        await finalLeadsApi.update(lead.id, { status: status as any });
        onUpdate();
      } catch (error) {
        console.error('Error updating status:', error);
      }
    }
  };

  const isFinalLead = (lead: AutoLead | FinalLead): lead is FinalLead => {
    return type === 'final';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <Building2 className="h-6 w-6 text-blue-600" />
            <h3 className="text-xl font-semibold text-gray-900">{lead.company_name}</h3>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              lead.status === 'approved' ? 'bg-green-100 text-green-800' :
              lead.status === 'contacted' ? 'bg-blue-100 text-blue-800' :
              lead.status === 'generated' ? 'bg-gray-100 text-gray-800' :
              'bg-yellow-100 text-yellow-800'
            }`}>
              {lead.status}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Lead Details */}
            <div>
              <h4 className="text-lg font-medium text-gray-900 mb-4">Company Information</h4>
              <div className="space-y-4">
                {lead.website && (
                  <div className="flex items-center space-x-3">
                    <ExternalLink className="h-5 w-5 text-gray-400" />
                    <a
                      href={lead.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800"
                    >
                      {lead.website}
                    </a>
                  </div>
                )}

                {lead.email && (
                  <div className="flex items-center space-x-3">
                    <Mail className="h-5 w-5 text-gray-400" />
                    <a
                      href={`mailto:${lead.email}`}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      {lead.email}
                    </a>
                  </div>
                )}

                {lead.phone && (
                  <div className="flex items-center space-x-3">
                    <Phone className="h-5 w-5 text-gray-400" />
                    <a
                      href={`tel:${lead.phone}`}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      {lead.phone}
                    </a>
                  </div>
                )}

                {lead.address && (
                  <div className="flex items-center space-x-3">
                    <MapPin className="h-5 w-5 text-gray-400" />
                    <span className="text-gray-700">{lead.address}</span>
                  </div>
                )}

                {lead.industry && (
                  <div className="flex items-center space-x-3">
                    <Building2 className="h-5 w-5 text-gray-400" />
                    <span className="text-gray-700">{lead.industry}</span>
                  </div>
                )}

                {lead.employee_count && (
                  <div className="flex items-center space-x-3">
                    <Users className="h-5 w-5 text-gray-400" />
                    <span className="text-gray-700">{lead.employee_count} employees</span>
                  </div>
                )}

                <div className="pt-4">
                  <span className="text-sm font-medium text-gray-500">Relevance Score:</span>
                  <div className="mt-1 flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          lead.relevance_score >= 0.8 ? 'bg-green-600' :
                          lead.relevance_score >= 0.6 ? 'bg-yellow-600' : 'bg-red-600'
                        }`}
                        style={{ width: `${lead.relevance_score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-700">
                      {Math.round(lead.relevance_score * 100)}%
                    </span>
                  </div>
                </div>

                <div className="pt-2">
                  <span className="text-sm font-medium text-gray-500">Keywords Matched:</span>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {lead.keywords_matched.map((keyword, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>

                {isFinalLead(lead) && (
                  <div className="pt-4 space-y-3">
                    <div>
                      <span className="text-sm font-medium text-gray-500">Priority:</span>
                      <span className={`ml-2 text-sm font-medium capitalize ${
                        lead.priority === 'high' ? 'text-red-600' :
                        lead.priority === 'medium' ? 'text-yellow-600' : 'text-green-600'
                      }`}>
                        {lead.priority}
                      </span>
                    </div>
                    
                    {lead.assigned_user && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Assigned to:</span>
                        <span className="ml-2 text-sm text-gray-700">{lead.assigned_user.full_name}</span>
                      </div>
                    )}

                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleStatusUpdate('contacted')}
                        disabled={lead.status === 'contacted'}
                        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded disabled:opacity-50 transition-colors"
                      >
                        Mark Contacted
                      </button>
                      <button
                        onClick={() => handleStatusUpdate('rejected')}
                        disabled={lead.status === 'rejected'}
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded disabled:opacity-50 transition-colors"
                      >
                        Mark Rejected
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Notes Section */}
            <div>
              <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center space-x-2">
                <MessageSquare className="h-5 w-5" />
                <span>Notes & Communication</span>
              </h4>

              {/* Add Note Form */}
              <form onSubmit={handleAddNote} className="mb-6">
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 resize-none"
                  rows={3}
                  placeholder="Add a note about this lead..."
                />
                <div className="mt-2 flex justify-end">
                  <button
                    type="submit"
                    disabled={!newNote.trim() || loading}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded disabled:opacity-50 transition-colors"
                  >
                    {loading ? 'Adding...' : 'Add Note'}
                  </button>
                </div>
              </form>

              {/* Notes List */}
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {notesLoading ? (
                  <div className="animate-pulse space-y-3">
                    {Array(3).fill(0).map((_, i) => (
                      <div key={i} className="p-3 bg-gray-100 rounded">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    ))}
                  </div>
                ) : notes.length === 0 ? (
                  <p className="text-gray-500 text-sm">No notes yet. Add the first note above.</p>
                ) : (
                  notes.map((note) => (
                    <div key={note.id} className="p-3 bg-gray-50 rounded">
                      <p className="text-sm text-gray-900 mb-2">{note.note}</p>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>{note.user?.full_name}</span>
                        <span>{new Date(note.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}