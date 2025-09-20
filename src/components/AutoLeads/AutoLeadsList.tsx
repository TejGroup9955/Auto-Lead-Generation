import React, { useState, useEffect } from 'react';
import { Users, Filter, Download, CheckSquare, Eye } from 'lucide-react';
import { AutoLead, LeadFilters } from '../../types';
import { autoLeadsApi } from '../../services/api';
import { useAuthContext } from '../../context/AuthContext';
import LeadDetailsModal from '../common/LeadDetailsModal';

export default function AutoLeadsList() {
  const [leads, setLeads] = useState<AutoLead[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLeads, setSelectedLeads] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<LeadFilters>({});
  const [selectedLead, setSelectedLead] = useState<AutoLead | null>(null);
  const { profile } = useAuthContext();

  useEffect(() => {
    fetchLeads();
  }, [filters]);

  const fetchLeads = async () => {
    try {
      const data = await autoLeadsApi.getAll(filters);
      setLeads(data);
    } catch (error) {
      console.error('Error fetching leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectLead = (leadId: string) => {
    setSelectedLeads(prev => 
      prev.includes(leadId)
        ? prev.filter(id => id !== leadId)
        : [...prev, leadId]
    );
  };

  const handleSelectAll = () => {
    setSelectedLeads(
      selectedLeads.length === leads.length ? [] : leads.map(lead => lead.id)
    );
  };

  const handleMoveToFinal = async () => {
    if (selectedLeads.length === 0 || !profile) return;

    try {
      await autoLeadsApi.moveToFinal(selectedLeads, profile.id);
      setSelectedLeads([]);
      fetchLeads();
      alert(`${selectedLeads.length} leads moved to Final Leads successfully!`);
    } catch (error) {
      console.error('Error moving leads:', error);
      alert('Error moving leads to Final Leads');
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
      'Relevance Score': lead.relevance_score,
      'Status': lead.status,
      'Source': lead.source,
      'Created Date': new Date(lead.created_at).toLocaleDateString()
    }));

    const csv = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `auto-leads-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'generated': return 'bg-blue-100 text-blue-800';
      case 'reviewing': return 'bg-yellow-100 text-yellow-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="space-y-4">
              {Array(10).fill(0).map((_, i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
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
          <Users className="h-8 w-8 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Auto Generated Leads</h2>
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
          <button
            onClick={handleMoveToFinal}
            disabled={selectedLeads.length === 0}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg disabled:opacity-50 transition-colors"
          >
            <CheckSquare className="h-4 w-4" />
            <span>Move to Final ({selectedLeads.length})</span>
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
                <option value="generated">Generated</option>
                <option value="reviewing">Reviewing</option>
                <option value="approved">Approved</option>
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
          <Users className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Leads Found</h3>
          <p className="text-gray-600">
            {Object.keys(filters).length > 0 
              ? 'Try adjusting your filters or run some campaigns to generate leads.'
              : 'Start by creating and running some campaigns to generate leads.'
            }
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="p-4 bg-gray-50 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={selectedLeads.length === leads.length}
                onChange={handleSelectAll}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="text-sm font-medium text-gray-700">
                {selectedLeads.length > 0 
                  ? `${selectedLeads.length} of ${leads.length} selected`
                  : `${leads.length} leads found`
                }
              </span>
            </div>
          </div>

          <div className="divide-y divide-gray-200">
            {leads.map((lead) => (
              <div key={lead.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start space-x-4">
                  <input
                    type="checkbox"
                    checked={selectedLeads.includes(lead.id)}
                    onChange={() => handleSelectLead(lead.id)}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 truncate">
                        {lead.company_name}
                      </h3>
                      <div className="flex items-center space-x-3">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(lead.status)}`}>
                          {lead.status}
                        </span>
                        <span className={`text-sm font-medium ${getRelevanceColor(lead.relevance_score)}`}>
                          {Math.round(lead.relevance_score * 100)}% match
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600 mb-3">
                      <div>
                        <span className="font-medium">Industry:</span> {lead.industry || 'N/A'}
                      </div>
                      <div>
                        <span className="font-medium">Size:</span> {lead.employee_count || 'N/A'}
                      </div>
                      <div>
                        <span className="font-medium">Source:</span> {lead.source}
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex flex-wrap gap-2">
                        {lead.keywords_matched.slice(0, 3).map((keyword, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                          >
                            {keyword}
                          </span>
                        ))}
                        {lead.keywords_matched.length > 3 && (
                          <span className="text-xs text-gray-500">
                            +{lead.keywords_matched.length - 3} more
                          </span>
                        )}
                      </div>

                      <button
                        onClick={() => setSelectedLead(lead)}
                        className="flex items-center space-x-1 px-3 py-1 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      >
                        <Eye className="h-4 w-4" />
                        <span className="text-sm">View Details</span>
                      </button>
                    </div>
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
          type="auto"
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