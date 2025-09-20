import React, { useState } from 'react';
import { AuthProvider, useAuthContext } from './context/AuthContext';
import LoginForm from './components/Auth/LoginForm';
import Sidebar from './components/Layout/Sidebar';
import Dashboard from './components/Dashboard/Dashboard';
import ProductsList from './components/Products/ProductsList';
import CampaignsList from './components/Campaigns/CampaignsList';
import AutoLeadsList from './components/AutoLeads/AutoLeadsList';
import FinalLeadsList from './components/FinalLeads/FinalLeadsList';
import UsersList from './components/Users/UsersList';
import ActivityLogs from './components/Activity/ActivityLogs';

function AppContent() {
  const { user, loading } = useAuthContext();
  const [activeSection, setActiveSection] = useState('dashboard');

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return <LoginForm />;
  }

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <Dashboard />;
      case 'products':
        return <ProductsList />;
      case 'campaigns':
        return <CampaignsList />;
      case 'auto-leads':
        return <AutoLeadsList />;
      case 'final-leads':
        return <FinalLeadsList />;
      case 'users':
        return <UsersList />;
      case 'activity':
        return <ActivityLogs />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar 
        activeSection={activeSection} 
        onSectionChange={setActiveSection} 
      />
      <main className="flex-1">
        {renderContent()}
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;