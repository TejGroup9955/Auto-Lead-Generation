import React from 'react';
import { 
  LayoutDashboard, 
  Package, 
  Target, 
  Users, 
  CheckSquare, 
  Settings,
  Activity,
  LogOut,
  Building2
} from 'lucide-react';
import { useAuthContext } from '../../context/AuthContext';

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export default function Sidebar({ activeSection, onSectionChange }: SidebarProps) {
  const { profile, signOut, hasPermission } = useAuthContext();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: ['admin', 'sales_coordinator', 'reviewer', 'bdm'] },
    { id: 'campaigns', label: 'Campaigns', icon: Target, roles: ['admin', 'sales_coordinator', 'reviewer'] },
    { id: 'auto-leads', label: 'Auto Leads', icon: Users, roles: ['admin', 'sales_coordinator', 'reviewer'] },
    { id: 'final-leads', label: 'Final Leads', icon: CheckSquare, roles: ['admin', 'sales_coordinator', 'reviewer', 'bdm'] },
    { id: 'products', label: 'Products', icon: Package, roles: ['admin'] },
    { id: 'users', label: 'User Management', icon: Settings, roles: ['admin'] },
    { id: 'activity', label: 'Activity Logs', icon: Activity, roles: ['admin'] }
  ];

  const filteredMenuItems = menuItems.filter(item => 
    hasPermission(item.roles)
  );

  const handleSignOut = async () => {
    await signOut();
  };

  return (
    <div className="bg-slate-900 text-white w-64 min-h-screen flex flex-col">
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center space-x-3">
          <Building2 className="h-8 w-8 text-blue-400" />
          <div>
            <h1 className="text-xl font-bold">SMART CRM</h1>
            <p className="text-sm text-slate-400">Lead Generation</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {filteredMenuItems.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.id}>
                <button
                  onClick={() => onSectionChange(item.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    activeSection === item.id
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="p-4 border-t border-slate-700">
        <div className="mb-4">
          <p className="text-sm font-medium">{profile?.full_name}</p>
          <p className="text-xs text-slate-400 capitalize">{profile?.role?.replace('_', ' ')}</p>
        </div>
        <button
          onClick={handleSignOut}
          className="w-full flex items-center space-x-3 px-4 py-3 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition-colors"
        >
          <LogOut className="h-5 w-5" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  );
}