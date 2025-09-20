import React, { useState, useEffect } from 'react';
import { DashboardStats } from '../../types';
import { dashboardApi } from '../../services/api';
import DashboardStatsComponent from './DashboardStats';
import RecentActivity from './RecentActivity';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalLeads: 0,
    approvedLeads: 0,
    activeCampaigns: 0,
    conversionRate: 0,
    leadsThisMonth: 0,
    leadsLastMonth: 0,
    topRegions: [],
    topProducts: [],
    recentActivity: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const data = await dashboardApi.getStats();
      setStats(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome to your lead generation command center</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">Last updated</p>
          <p className="text-sm font-medium text-gray-900">
            {new Date().toLocaleString()}
          </p>
        </div>
      </div>

      <DashboardStatsComponent stats={stats} loading={loading} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <RecentActivity activities={stats.recentActivity} loading={loading} />
        
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full p-4 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all">
              <div className="font-medium text-gray-900">Create New Campaign</div>
              <div className="text-sm text-gray-600">Start generating leads for a product/service</div>
            </button>
            <button className="w-full p-4 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all">
              <div className="font-medium text-gray-900">Review Auto Leads</div>
              <div className="text-sm text-gray-600">Check generated leads and move to final</div>
            </button>
            <button className="w-full p-4 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all">
              <div className="font-medium text-gray-900">Export Final Leads</div>
              <div className="text-sm text-gray-600">Download approved leads for outreach</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}