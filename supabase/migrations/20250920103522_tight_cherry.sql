/*
  # Auto Lead Generation CRM Database Schema

  1. New Tables
    - `profiles` - User profile information with roles
    - `products` - Product/service definitions with keywords
    - `campaigns` - Lead generation campaigns
    - `auto_leads` - Generated leads from campaigns
    - `final_leads` - Approved leads ready for outreach
    - `lead_tags` - Tagging system for lead categorization
    - `lead_notes` - Communication and notes on leads
    - `activity_logs` - Audit trail for all user actions
    - `regions` - Geographic regions for targeting

  2. Security
    - Enable RLS on all tables
    - Add policies for role-based access control
    - Secure data access based on user roles
*/

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE user_role AS ENUM ('admin', 'sales_coordinator', 'reviewer', 'bdm');
CREATE TYPE lead_status AS ENUM ('generated', 'reviewing', 'approved', 'rejected', 'contacted');
CREATE TYPE campaign_status AS ENUM ('active', 'paused', 'completed', 'scheduled');
CREATE TYPE activity_type AS ENUM ('login', 'logout', 'create', 'update', 'delete', 'approve', 'reject', 'export');

-- Profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  email text NOT NULL UNIQUE,
  full_name text NOT NULL,
  role user_role NOT NULL DEFAULT 'bdm',
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  description text,
  keywords text[] NOT NULL DEFAULT '{}',
  is_active boolean DEFAULT true,
  created_by uuid REFERENCES profiles(id),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Regions table
CREATE TABLE IF NOT EXISTS regions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  country text NOT NULL DEFAULT 'India',
  state text,
  city text,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  description text,
  product_id uuid REFERENCES products(id),
  region_id uuid REFERENCES regions(id),
  keywords text[] NOT NULL DEFAULT '{}',
  status campaign_status DEFAULT 'scheduled',
  scheduled_at timestamptz,
  is_recurring boolean DEFAULT false,
  recurrence_pattern text, -- 'weekly', 'monthly', etc.
  leads_generated integer DEFAULT 0,
  created_by uuid REFERENCES profiles(id),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Auto leads table
CREATE TABLE IF NOT EXISTS auto_leads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id uuid REFERENCES campaigns(id),
  company_name text NOT NULL,
  website text,
  linkedin_url text,
  email text,
  phone text,
  address text,
  industry text,
  employee_count text,
  revenue_range text,
  keywords_matched text[],
  relevance_score decimal(3,2) DEFAULT 0.0,
  status lead_status DEFAULT 'generated',
  is_selected boolean DEFAULT false,
  source text, -- 'duckduckgo', 'opencorporates', etc.
  raw_data jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Final leads table
CREATE TABLE IF NOT EXISTS final_leads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  auto_lead_id uuid REFERENCES auto_leads(id),
  company_name text NOT NULL,
  website text,
  linkedin_url text,
  email text,
  phone text,
  address text,
  industry text,
  employee_count text,
  revenue_range text,
  keywords_matched text[],
  relevance_score decimal(3,2) DEFAULT 0.0,
  status lead_status DEFAULT 'approved',
  priority text DEFAULT 'medium', -- 'high', 'medium', 'low'
  assigned_to uuid REFERENCES profiles(id),
  last_contact_date timestamptz,
  next_follow_up timestamptz,
  conversion_probability decimal(3,2),
  notes text,
  approved_by uuid REFERENCES profiles(id),
  approved_at timestamptz DEFAULT now(),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Lead tags table
CREATE TABLE IF NOT EXISTS lead_tags (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  color text DEFAULT '#3b82f6',
  description text,
  created_by uuid REFERENCES profiles(id),
  created_at timestamptz DEFAULT now()
);

-- Lead tag assignments
CREATE TABLE IF NOT EXISTS lead_tag_assignments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id uuid, -- Can reference either auto_leads or final_leads
  lead_type text NOT NULL CHECK (lead_type IN ('auto', 'final')),
  tag_id uuid REFERENCES lead_tags(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now(),
  UNIQUE(lead_id, tag_id, lead_type)
);

-- Lead notes table
CREATE TABLE IF NOT EXISTS lead_notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id uuid, -- Can reference either auto_leads or final_leads
  lead_type text NOT NULL CHECK (lead_type IN ('auto', 'final')),
  note text NOT NULL,
  is_internal boolean DEFAULT true,
  created_by uuid REFERENCES profiles(id),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Activity logs table
CREATE TABLE IF NOT EXISTS activity_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES profiles(id),
  activity_type activity_type NOT NULL,
  entity_type text, -- 'lead', 'campaign', 'product', etc.
  entity_id uuid,
  description text NOT NULL,
  metadata jsonb DEFAULT '{}',
  ip_address inet,
  user_agent text,
  created_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE regions ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE auto_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE final_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_tag_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Profiles policies
CREATE POLICY "Users can read all active profiles" ON profiles
  FOR SELECT TO authenticated
  USING (is_active = true);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Admins can manage all profiles" ON profiles
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles 
      WHERE user_id = auth.uid() AND role = 'admin'
    )
  );

-- Products policies
CREATE POLICY "All users can read active products" ON products
  FOR SELECT TO authenticated
  USING (is_active = true);

CREATE POLICY "Admins can manage products" ON products
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles 
      WHERE user_id = auth.uid() AND role = 'admin'
    )
  );

-- Regions policies
CREATE POLICY "All users can read active regions" ON regions
  FOR SELECT TO authenticated
  USING (is_active = true);

CREATE POLICY "Admins can manage regions" ON regions
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles 
      WHERE user_id = auth.uid() AND role = 'admin'
    )
  );

-- Campaigns policies
CREATE POLICY "Users can read campaigns" ON campaigns
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "Sales coordinators and admins can manage campaigns" ON campaigns
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles 
      WHERE user_id = auth.uid() 
      AND role IN ('admin', 'sales_coordinator')
    )
  );

-- Auto leads policies
CREATE POLICY "Users can read auto leads" ON auto_leads
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "Sales coordinators and admins can manage auto leads" ON auto_leads
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles 
      WHERE user_id = auth.uid() 
      AND role IN ('admin', 'sales_coordinator', 'reviewer')
    )
  );

-- Final leads policies
CREATE POLICY "Users can read final leads" ON final_leads
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "Authorized users can manage final leads" ON final_leads
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles 
      WHERE user_id = auth.uid() 
      AND role IN ('admin', 'sales_coordinator', 'reviewer')
    )
  );

-- Lead tags policies
CREATE POLICY "Users can read lead tags" ON lead_tags
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "Users can create lead tags" ON lead_tags
  FOR INSERT TO authenticated
  WITH CHECK (created_by IN (
    SELECT id FROM profiles WHERE user_id = auth.uid()
  ));

-- Lead tag assignments policies
CREATE POLICY "Users can read tag assignments" ON lead_tag_assignments
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "Users can manage tag assignments" ON lead_tag_assignments
  FOR ALL TO authenticated
  USING (true);

-- Lead notes policies
CREATE POLICY "Users can read lead notes" ON lead_notes
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "Users can create notes" ON lead_notes
  FOR INSERT TO authenticated
  WITH CHECK (created_by IN (
    SELECT id FROM profiles WHERE user_id = auth.uid()
  ));

-- Activity logs policies
CREATE POLICY "Admins can read all activity logs" ON activity_logs
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles 
      WHERE user_id = auth.uid() AND role = 'admin'
    )
  );

CREATE POLICY "Users can read own activity logs" ON activity_logs
  FOR SELECT TO authenticated
  USING (
    user_id IN (
      SELECT id FROM profiles WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "System can insert activity logs" ON activity_logs
  FOR INSERT TO authenticated
  WITH CHECK (true);

-- Insert some sample data

-- Insert sample regions
INSERT INTO regions (name, country, state, city) VALUES
  ('Mumbai', 'India', 'Maharashtra', 'Mumbai'),
  ('Bangalore', 'India', 'Karnataka', 'Bangalore'),
  ('Delhi NCR', 'India', 'Delhi', 'New Delhi'),
  ('Hyderabad', 'India', 'Telangana', 'Hyderabad'),
  ('Chennai', 'India', 'Tamil Nadu', 'Chennai'),
  ('Pune', 'India', 'Maharashtra', 'Pune');

-- Insert sample lead tags
INSERT INTO lead_tags (name, color, description) VALUES
  ('High Budget', '#ef4444', 'Companies with high budget potential'),
  ('Startup', '#8b5cf6', 'Early stage startups'),
  ('Enterprise', '#059669', 'Large enterprise clients'),
  ('SMB', '#0284c7', 'Small and medium businesses'),
  ('Hot Lead', '#ea580c', 'High priority leads'),
  ('Follow Up', '#eab308', 'Requires follow up');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_auto_leads_campaign_id ON auto_leads(campaign_id);
CREATE INDEX IF NOT EXISTS idx_auto_leads_status ON auto_leads(status);
CREATE INDEX IF NOT EXISTS idx_final_leads_status ON final_leads(status);
CREATE INDEX IF NOT EXISTS idx_final_leads_assigned_to ON final_leads(assigned_to);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at);