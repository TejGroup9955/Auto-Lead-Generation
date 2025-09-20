import { supabase } from '../lib/supabase';
import { 
  Product, 
  Campaign, 
  AutoLead, 
  FinalLead, 
  Region, 
  LeadTag, 
  LeadNote, 
  ActivityLog,
  Profile,
  LeadFilters,
  DashboardStats
} from '../types';

// Profile API
export const profilesApi = {
  async getAll() {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('is_active', true)
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    return data as Profile[];
  },

  async update(id: string, updates: Partial<Profile>) {
    const { data, error } = await supabase
      .from('profiles')
      .update(updates)
      .eq('id', id)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }
};

// Products API
export const productsApi = {
  async getAll() {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('is_active', true)
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    return data as Product[];
  },

  async create(product: Omit<Product, 'id' | 'created_at' | 'updated_at'>) {
    const { data, error } = await supabase
      .from('products')
      .insert(product)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  },

  async update(id: string, updates: Partial<Product>) {
    const { data, error } = await supabase
      .from('products')
      .update(updates)
      .eq('id', id)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  },

  async delete(id: string) {
    const { error } = await supabase
      .from('products')
      .update({ is_active: false })
      .eq('id', id);
    
    if (error) throw error;
  }
};

// Regions API
export const regionsApi = {
  async getAll() {
    const { data, error } = await supabase
      .from('regions')
      .select('*')
      .eq('is_active', true)
      .order('name');
    
    if (error) throw error;
    return data as Region[];
  }
};

// Campaigns API
export const campaignsApi = {
  async getAll() {
    const { data, error } = await supabase
      .from('campaigns')
      .select(`
        *,
        product:products(*),
        region:regions(*)
      `)
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    return data as Campaign[];
  },

  async create(campaign: Omit<Campaign, 'id' | 'created_at' | 'updated_at' | 'leads_generated'>) {
    const { data, error } = await supabase
      .from('campaigns')
      .insert(campaign)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  },

  async update(id: string, updates: Partial<Campaign>) {
    const { data, error } = await supabase
      .from('campaigns')
      .update(updates)
      .eq('id', id)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  },

  async generateLeads(campaignId: string) {
    // Mock lead generation - in production this would call external APIs
    const mockLeads = [
      {
        campaign_id: campaignId,
        company_name: 'Tech Solutions Ltd',
        website: 'https://techsolutions.com',
        email: 'contact@techsolutions.com',
        phone: '+91-9876543210',
        industry: 'Technology',
        employee_count: '50-100',
        keywords_matched: ['ERP', 'Software'],
        relevance_score: 0.85,
        source: 'duckduckgo'
      },
      {
        campaign_id: campaignId,
        company_name: 'Business Dynamics Corp',
        website: 'https://businessdynamics.com',
        email: 'info@businessdynamics.com',
        phone: '+91-9876543211',
        industry: 'Manufacturing',
        employee_count: '100-500',
        keywords_matched: ['ERP', 'Enterprise'],
        relevance_score: 0.78,
        source: 'opencorporates'
      },
      {
        campaign_id: campaignId,
        company_name: 'Digital Innovations Inc',
        website: 'https://digitalinnovations.com',
        email: 'hello@digitalinnovations.com',
        phone: '+91-9876543212',
        industry: 'Digital Services',
        employee_count: '20-50',
        keywords_matched: ['Software', 'Digital'],
        relevance_score: 0.72,
        source: 'linkedin'
      }
    ];

    const { data, error } = await supabase
      .from('auto_leads')
      .insert(mockLeads)
      .select();
    
    if (error) throw error;

    // Update campaign leads count
    await supabase
      .from('campaigns')
      .update({ leads_generated: mockLeads.length })
      .eq('id', campaignId);

    return data;
  }
};

// Auto Leads API
export const autoLeadsApi = {
  async getAll(filters?: LeadFilters) {
    let query = supabase
      .from('auto_leads')
      .select(`
        *,
        campaign:campaigns(
          *,
          product:products(*),
          region:regions(*)
        )
      `);

    if (filters?.status && filters.status.length > 0) {
      query = query.in('status', filters.status);
    }

    if (filters?.search) {
      query = query.or(`company_name.ilike.%${filters.search}%,email.ilike.%${filters.search}%,industry.ilike.%${filters.search}%`);
    }

    const { data, error } = await query.order('created_at', { ascending: false });
    
    if (error) throw error;
    return data as AutoLead[];
  },

  async update(id: string, updates: Partial<AutoLead>) {
    const { data, error } = await supabase
      .from('auto_leads')
      .update(updates)
      .eq('id', id)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  },

  async moveToFinal(leadIds: string[], approvedBy: string) {
    // Get the selected leads
    const { data: leads, error: fetchError } = await supabase
      .from('auto_leads')
      .select('*')
      .in('id', leadIds);

    if (fetchError) throw fetchError;

    // Convert to final leads
    const finalLeads = leads.map(lead => ({
      auto_lead_id: lead.id,
      company_name: lead.company_name,
      website: lead.website,
      linkedin_url: lead.linkedin_url,
      email: lead.email,
      phone: lead.phone,
      address: lead.address,
      industry: lead.industry,
      employee_count: lead.employee_count,
      revenue_range: lead.revenue_range,
      keywords_matched: lead.keywords_matched,
      relevance_score: lead.relevance_score,
      status: 'approved' as const,
      approved_by: approvedBy,
      approved_at: new Date().toISOString()
    }));

    const { data, error } = await supabase
      .from('final_leads')
      .insert(finalLeads)
      .select();

    if (error) throw error;

    // Update auto leads status
    await supabase
      .from('auto_leads')
      .update({ status: 'approved', is_selected: true })
      .in('id', leadIds);

    return data;
  }
};

// Final Leads API
export const finalLeadsApi = {
  async getAll(filters?: LeadFilters) {
    let query = supabase
      .from('final_leads')
      .select(`
        *,
        assigned_user:profiles!final_leads_assigned_to_fkey(*)
      `);

    if (filters?.status && filters.status.length > 0) {
      query = query.in('status', filters.status);
    }

    if (filters?.search) {
      query = query.or(`company_name.ilike.%${filters.search}%,email.ilike.%${filters.search}%,industry.ilike.%${filters.search}%`);
    }

    const { data, error } = await query.order('created_at', { ascending: false });
    
    if (error) throw error;
    return data as FinalLead[];
  },

  async update(id: string, updates: Partial<FinalLead>) {
    const { data, error } = await supabase
      .from('final_leads')
      .update(updates)
      .eq('id', id)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  },

  async delete(id: string) {
    const { error } = await supabase
      .from('final_leads')
      .delete()
      .eq('id', id);
    
    if (error) throw error;
  }
};

// Lead Tags API
export const leadTagsApi = {
  async getAll() {
    const { data, error } = await supabase
      .from('lead_tags')
      .select('*')
      .order('name');
    
    if (error) throw error;
    return data as LeadTag[];
  },

  async create(tag: Omit<LeadTag, 'id' | 'created_at'>) {
    const { data, error } = await supabase
      .from('lead_tags')
      .insert(tag)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }
};

// Lead Notes API
export const leadNotesApi = {
  async create(note: Omit<LeadNote, 'id' | 'created_at' | 'updated_at'>) {
    const { data, error } = await supabase
      .from('lead_notes')
      .insert(note)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  },

  async getByLead(leadId: string, leadType: 'auto' | 'final') {
    const { data, error } = await supabase
      .from('lead_notes')
      .select(`
        *,
        user:profiles(*)
      `)
      .eq('lead_id', leadId)
      .eq('lead_type', leadType)
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    return data as LeadNote[];
  }
};

// Activity Logs API
export const activityLogsApi = {
  async create(log: Omit<ActivityLog, 'id' | 'created_at'>) {
    const { data, error } = await supabase
      .from('activity_logs')
      .insert(log)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  },

  async getRecent(limit = 10) {
    const { data, error } = await supabase
      .from('activity_logs')
      .select(`
        *,
        user:profiles(*)
      `)
      .order('created_at', { ascending: false })
      .limit(limit);
    
    if (error) throw error;
    return data as ActivityLog[];
  }
};

// Dashboard API
export const dashboardApi = {
  async getStats(): Promise<DashboardStats> {
    const [
      { count: totalLeads },
      { count: approvedLeads },
      { count: activeCampaigns },
      recentActivity
    ] = await Promise.all([
      supabase.from('auto_leads').select('*', { count: 'exact', head: true }),
      supabase.from('final_leads').select('*', { count: 'exact', head: true }),
      supabase.from('campaigns').select('*', { count: 'exact', head: true }).eq('status', 'active'),
      activityLogsApi.getRecent(5)
    ]);

    return {
      totalLeads: totalLeads || 0,
      approvedLeads: approvedLeads || 0,
      activeCampaigns: activeCampaigns || 0,
      conversionRate: totalLeads ? ((approvedLeads || 0) / totalLeads) * 100 : 0,
      leadsThisMonth: 0, // Would require date filtering in production
      leadsLastMonth: 0,
      topRegions: [],
      topProducts: [],
      recentActivity: recentActivity || []
    };
  }
};