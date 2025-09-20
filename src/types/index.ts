export type UserRole = 'admin' | 'sales_coordinator' | 'reviewer' | 'bdm';

export type LeadStatus = 'generated' | 'reviewing' | 'approved' | 'rejected' | 'contacted';

export type CampaignStatus = 'active' | 'paused' | 'completed' | 'scheduled';

export type ActivityType = 'login' | 'logout' | 'create' | 'update' | 'delete' | 'approve' | 'reject' | 'export';

export interface Profile {
  id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  keywords: string[];
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Region {
  id: string;
  name: string;
  country: string;
  state: string;
  city: string;
  is_active: boolean;
  created_at: string;
}

export interface Campaign {
  id: string;
  name: string;
  description: string;
  product_id: string;
  region_id: string;
  keywords: string[];
  status: CampaignStatus;
  scheduled_at: string;
  is_recurring: boolean;
  recurrence_pattern: string;
  leads_generated: number;
  created_by: string;
  created_at: string;
  updated_at: string;
  product?: Product;
  region?: Region;
}

export interface AutoLead {
  id: string;
  campaign_id: string;
  company_name: string;
  website?: string;
  linkedin_url?: string;
  email?: string;
  phone?: string;
  address?: string;
  industry?: string;
  employee_count?: string;
  revenue_range?: string;
  keywords_matched: string[];
  relevance_score: number;
  status: LeadStatus;
  is_selected: boolean;
  source: string;
  raw_data?: any;
  created_at: string;
  updated_at: string;
  campaign?: Campaign;
  tags?: LeadTag[];
  notes?: LeadNote[];
}

export interface FinalLead {
  id: string;
  auto_lead_id?: string;
  company_name: string;
  website?: string;
  linkedin_url?: string;
  email?: string;
  phone?: string;
  address?: string;
  industry?: string;
  employee_count?: string;
  revenue_range?: string;
  keywords_matched: string[];
  relevance_score: number;
  status: LeadStatus;
  priority: 'high' | 'medium' | 'low';
  assigned_to?: string;
  last_contact_date?: string;
  next_follow_up?: string;
  conversion_probability?: number;
  notes?: string;
  approved_by: string;
  approved_at: string;
  created_at: string;
  updated_at: string;
  tags?: LeadTag[];
  lead_notes?: LeadNote[];
  assigned_user?: Profile;
}

export interface LeadTag {
  id: string;
  name: string;
  color: string;
  description?: string;
  created_by: string;
  created_at: string;
}

export interface LeadNote {
  id: string;
  lead_id: string;
  lead_type: 'auto' | 'final';
  note: string;
  is_internal: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
  user?: Profile;
}

export interface ActivityLog {
  id: string;
  user_id: string;
  activity_type: ActivityType;
  entity_type?: string;
  entity_id?: string;
  description: string;
  metadata?: any;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
  user?: Profile;
}

export interface LeadFilters {
  status?: LeadStatus[];
  industry?: string[];
  tags?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
  relevanceScore?: {
    min: number;
    max: number;
  };
  search?: string;
}

export interface DashboardStats {
  totalLeads: number;
  approvedLeads: number;
  activeCampaigns: number;
  conversionRate: number;
  leadsThisMonth: number;
  leadsLastMonth: number;
  topRegions: { name: string; count: number }[];
  topProducts: { name: string; count: number }[];
  recentActivity: ActivityLog[];
}