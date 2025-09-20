import React, { useState, useEffect } from 'react';
import { CheckSquare, Filter, Download, Eye, Trash2, Star } from 'lucide-react';
import { FinalLead, LeadFilters } from '../../types';
import { finalLeadsApi } from '../../services/api';
import LeadDetailsModal from '../common/LeadDetailsModal';

export default function FinalLeadsList() {
  const [leads, setLeads] = useState<FinalLead[]>([]);
  const [loading, setLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<LeadFilters>({});
  const [selectedLead, setSelectedLead] = useState<FinalLead | null>(null);

  useEffect(() => {
    fetchLeads();
  }, [filters]);

  const fetchLeads = async () => {
    try {
      const data = await finalLeadsApi.getAll(filters);
      setLeads(data);
    } catch (error) {
      console.error('Error fetching leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this lead?')) {
      try {
        await finalLeadsApi.delete(id);
        fetchLeads();
      } catch (error) {
        console.error('Error deleting lead:', error);
      }
    }
  };

  const exportToCSV = () => {
    const csvData = leads.map(lead => ({
      'Company Name': lead.company_name,
      'Website': lead.website || '',
      'Email': lead.email || '',
      'Phone': lead.phone || '',
      'Industry': lead.industry || '',
      'Employee Count': lead.employee_count || '',
      'Priority': lead.priority,
      'Status': lead.status,
      'Relevance Score': lead.relevance_score,
      'Assigned To': lead.assigned_user?.full_name || '',
      'Last Contact': lead.last_contact_date || '',
      'Next Follow Up': lead.next_follow_up || '',
      'Approved Date': new Date(lead.approved_at).toLocaleDateString()
    }));

    const csv = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `final-leads-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'contacted': return 'bg-blue-100 text-blue-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getPriorityIcon = (priority: string) => {
    const colors = getPriorityColor(priority);
    return <Star className={`h-4 w-4 ${colors} ${priority === 'high' ? 'fill-current' : ''}`} />;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="space-y-4">
              {Array(8).fill(0).map((_, i) => (
                <div key={i} className="h-20 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-3">
          <CheckSquare className="h-8 w-8 text-green-600" />
          <h2 className="text-2xl font-bold text-gray-900">Final Leads</h2>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <Filter className="h-4 w-4" />
            <span>Filters</span>
          </button>
          <button
            onClick={exportToCSV}
            disabled={leads.length === 0}
            className="flex items-center space-x-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg disabled:opacity-50 transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {showFilters && (
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
              <input
                type="text"
                value={filters.search || ''}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                placeholder="Search companies, emails, or industries..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                multiple
                value={filters.status || []}
                onChange={(e) => setFilters(prev => ({ 
                  ...prev, 
                  status: Array.from(e.target.selectedOptions, option => option.value) as any
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="approved">Approved</option>
                <option value="contacted">Contacted</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setFilters({})}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      )}

      {leads.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <CheckSquare className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Final Leads</h3>
          <p className="text-gray-600">
            Approved leads from the Auto Leads section will appear here.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="p-4 bg-gray-50 border-b border-gray-200">
            <span className="text-sm font-medium text-gray-700">
              {leads.length} final leads
            </span>
          </div>

          <div className="divide-y divide-gray-200">
            {leads.map((lead) => (
              <div key={lead.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      {getPriorityIcon(lead.priority)}
                      <h3 className="text-lg font-semibold text-gray-900 truncate">
                        {lead.company_name}
                      </h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(lead.status)}`}>
                        {lead.status}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-3">
                      <div>
                        <span className="font-medium">Industry:</span> {lead.industry || 'N/A'}
                      </div>
                      <div>
                        <span className="font-medium">Size:</span> {lead.employee_count || 'N/A'}
                      </div>
                      <div>
                        <span className="font-medium">Score:</span> {Math.round(lead.relevance_score * 100)}%
                      </div>
                      <div>
                        <span className="font-medium">Assigned:</span> {lead.assigned_user?.full_name || 'Unassigned'}
                      </div>
                    </div>

                    {lead.next_follow_up && (
                      <div className="text-sm text-orange-600 mb-2">
                        <span className="font-medium">Next follow-up:</span> {new Date(lead.next_follow_up).toLocaleDateString()}
                      </div>
                    )}

                    <div className="flex flex-wrap gap-2">
                      {lead.keywords_matched.slice(0, 4).map((keyword, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                        >
                          {keyword}
                        </span>
                      ))}
                      {lead.keywords_matched.length > 4 && (
                        <span className="text-xs text-gray-500">
                          +{lead.keywords_matched.length - 4} more
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={() => setSelectedLead(lead)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="View Details"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(lead.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete Lead"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedLead && (
        <LeadDetailsModal
          lead={selectedLead}
          type="final"
          onClose={() => setSelectedLead(null)}
          onUpdate={() => {
            fetchLeads();
            setSelectedLead(null);
          }}
        />
      )}
    </div>
  );
}