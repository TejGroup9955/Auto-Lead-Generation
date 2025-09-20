-- Auto Lead Generation CRM Database Schema
-- MySQL Database Initialization Script

CREATE DATABASE IF NOT EXISTS crm_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE crm_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'sales_coordinator', 'reviewer', 'bdm') DEFAULT 'bdm',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    keywords JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_by CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_name (name),
    INDEX idx_active (is_active)
);

-- Regions table
CREATE TABLE IF NOT EXISTS regions (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) DEFAULT 'India',
    state VARCHAR(100),
    city VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_country (country)
);

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    product_id CHAR(36),
    region_id CHAR(36),
    keywords JSON,
    status ENUM('active', 'paused', 'completed', 'scheduled') DEFAULT 'scheduled',
    scheduled_at TIMESTAMP NULL,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern VARCHAR(50),
    leads_generated INT DEFAULT 0,
    created_by CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (region_id) REFERENCES regions(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_status (status),
    INDEX idx_product (product_id),
    INDEX idx_region (region_id)
);

-- Auto leads table
CREATE TABLE IF NOT EXISTS auto_leads (
    id CHAR(36) PRIMARY KEY,
    campaign_id CHAR(36),
    company_name VARCHAR(255) NOT NULL,
    website VARCHAR(500),
    linkedin_url VARCHAR(500),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    industry VARCHAR(255),
    employee_count VARCHAR(50),
    revenue_range VARCHAR(50),
    keywords_matched JSON,
    relevance_score DECIMAL(3,2) DEFAULT 0.00,
    status ENUM('generated', 'reviewing', 'approved', 'rejected', 'contacted') DEFAULT 'generated',
    is_selected BOOLEAN DEFAULT FALSE,
    source VARCHAR(100),
    raw_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
    INDEX idx_campaign (campaign_id),
    INDEX idx_status (status),
    INDEX idx_company (company_name),
    INDEX idx_relevance (relevance_score)
);

-- Final leads table
CREATE TABLE IF NOT EXISTS final_leads (
    id CHAR(36) PRIMARY KEY,
    auto_lead_id CHAR(36),
    company_name VARCHAR(255) NOT NULL,
    website VARCHAR(500),
    linkedin_url VARCHAR(500),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    industry VARCHAR(255),
    employee_count VARCHAR(50),
    revenue_range VARCHAR(50),
    keywords_matched JSON,
    relevance_score DECIMAL(3,2) DEFAULT 0.00,
    status ENUM('generated', 'reviewing', 'approved', 'rejected', 'contacted') DEFAULT 'approved',
    priority ENUM('high', 'medium', 'low') DEFAULT 'medium',
    assigned_to CHAR(36),
    last_contact_date TIMESTAMP NULL,
    next_follow_up TIMESTAMP NULL,
    conversion_probability DECIMAL(3,2),
    notes TEXT,
    approved_by CHAR(36),
    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (auto_lead_id) REFERENCES auto_leads(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_assigned (assigned_to),
    INDEX idx_company (company_name)
);

-- Lead tags table
CREATE TABLE IF NOT EXISTS lead_tags (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#3b82f6',
    description VARCHAR(500),
    created_by CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_name (name)
);

-- Lead tag assignments table
CREATE TABLE IF NOT EXISTS lead_tag_assignments (
    id CHAR(36) PRIMARY KEY,
    lead_id CHAR(36) NOT NULL,
    lead_type ENUM('auto', 'final') NOT NULL,
    tag_id CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tag_id) REFERENCES lead_tags(id) ON DELETE CASCADE,
    UNIQUE KEY unique_assignment (lead_id, tag_id, lead_type),
    INDEX idx_lead (lead_id, lead_type),
    INDEX idx_tag (tag_id)
);

-- Lead notes table
CREATE TABLE IF NOT EXISTS lead_notes (
    id CHAR(36) PRIMARY KEY,
    lead_id CHAR(36) NOT NULL,
    lead_type ENUM('auto', 'final') NOT NULL,
    note TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT TRUE,
    created_by CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_lead (lead_id, lead_type),
    INDEX idx_created_by (created_by)
);

-- Activity logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    activity_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id CHAR(36),
    description TEXT NOT NULL,
    metadata JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user (user_id),
    INDEX idx_type (activity_type),
    INDEX idx_created (created_at)
);

-- Insert sample regions
INSERT IGNORE INTO regions (id, name, country, state, city) VALUES
(UUID(), 'Mumbai', 'India', 'Maharashtra', 'Mumbai'),
(UUID(), 'Bangalore', 'India', 'Karnataka', 'Bangalore'),
(UUID(), 'Delhi NCR', 'India', 'Delhi', 'New Delhi'),
(UUID(), 'Hyderabad', 'India', 'Telangana', 'Hyderabad'),
(UUID(), 'Chennai', 'India', 'Tamil Nadu', 'Chennai'),
(UUID(), 'Pune', 'India', 'Maharashtra', 'Pune'),
(UUID(), 'Kolkata', 'India', 'West Bengal', 'Kolkata'),
(UUID(), 'Ahmedabad', 'India', 'Gujarat', 'Ahmedabad'),
(UUID(), 'Jaipur', 'India', 'Rajasthan', 'Jaipur'),
(UUID(), 'Surat', 'India', 'Gujarat', 'Surat');

-- Insert sample lead tags
INSERT IGNORE INTO lead_tags (id, name, color, description) VALUES
(UUID(), 'High Budget', '#ef4444', 'Companies with high budget potential'),
(UUID(), 'Startup', '#8b5cf6', 'Early stage startups'),
(UUID(), 'Enterprise', '#059669', 'Large enterprise clients'),
(UUID(), 'SMB', '#0284c7', 'Small and medium businesses'),
(UUID(), 'Hot Lead', '#ea580c', 'High priority leads'),
(UUID(), 'Follow Up', '#eab308', 'Requires follow up'),
(UUID(), 'Qualified', '#16a34a', 'Qualified prospects'),
(UUID(), 'Cold Lead', '#6b7280', 'Low engagement leads');

-- Create default admin user (password: admin123)
INSERT IGNORE INTO users (id, email, full_name, password_hash, role) VALUES
(UUID(), 'admin@smartcrm.com', 'System Administrator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJflLxQjO', 'admin');