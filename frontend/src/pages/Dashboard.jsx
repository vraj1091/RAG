import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.jsx';
import apiService from '../services/apiService.js';
import LoadingSpinner from '../components/LoadingSpinner.jsx';
import { 
  TrendingUp, 
  DollarSign, 
  Users, 
  ShoppingCart, 
  Activity,
  Database,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';

function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    documents: 0,
    conversations: 0,
    processedDocuments: 0,
    totalChunks: 0,
  });
  const [tallyStatus, setTallyStatus] = useState({
    connected: false,
    companyName: null,
    lastSync: null
  });
  const [financialMetrics, setFinancialMetrics] = useState({
    totalRevenue: 0,
    totalExpenses: 0,
    netProfit: 0,
    cashBalance: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    // eslint-disable-next-line
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load document stats
      const [documentStats, chatStats] = await Promise.all([
        apiService.getDocumentStats().catch(() => ({
          total_documents: 0,
          processed_documents: 0,
          vector_stats: { total_chunks: 0 },
        })),
        apiService.getChatStats().catch(() => ({ total_conversations: 0 }))
      ]);

      setStats({
        documents: documentStats.total_documents || 0,
        processedDocuments: documentStats.processed_documents || 0,
        totalChunks: documentStats.vector_stats?.total_chunks || 0,
        conversations: chatStats.total_conversations || 0,
      });

      // Check Tally connection
      try {
        const tallyTest = await apiService.testTallyConnection();
        if (tallyTest.status === 'connected') {
          setTallyStatus({
            connected: true,
            companyName: tallyTest.company_name,
            lastSync: new Date()
          });

          // Fetch financial metrics
          const metrics = await apiService.getTallyFinancialMetrics();
          if (metrics.success) {
            setFinancialMetrics(metrics.data);
          }
        } else {
          setTallyStatus({ connected: false, companyName: null, lastSync: null });
        }
      } catch (err) {
        console.log('Tally not connected');
        setTallyStatus({ connected: false, companyName: null, lastSync: null });
      }

    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.username || 'User'}!
        </h1>
        <p className="text-gray-600 mt-2">
          Here's your business intelligence overview
        </p>
      </div>

      {/* Tally Connection Status */}
      <div className={`mb-6 p-4 rounded-lg border-2 ${
        tallyStatus.connected 
          ? 'bg-green-50 border-green-200' 
          : 'bg-yellow-50 border-yellow-200'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {tallyStatus.connected ? (
              <CheckCircle className="w-6 h-6 text-green-600" />
            ) : (
              <AlertCircle className="w-6 h-6 text-yellow-600" />
            )}
            <div>
              <h3 className="font-semibold text-gray-900">
                {tallyStatus.connected ? 'Tally Connected' : 'Tally Not Connected'}
              </h3>
              {tallyStatus.connected && (
                <p className="text-sm text-gray-600">
                  Company: {tallyStatus.companyName || 'Loading...'} | Last synced: {new Date(tallyStatus.lastSync).toLocaleTimeString()}
                </p>
              )}
              {!tallyStatus.connected && (
                <p className="text-sm text-yellow-700">
                  Connect to Tally to view real-time financial data
                </p>
              )}
            </div>
          </div>
          <Link
            to="/tally-analytics"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            {tallyStatus.connected ? 'View Analytics' : 'Setup Tally'}
          </Link>
        </div>
      </div>

      {/* Financial Metrics - Only show if Tally connected */}
      {tallyStatus.connected && (
        <>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Financial Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <MetricCard
              title="Total Revenue"
              value={`₹${financialMetrics.totalRevenue.toLocaleString()}`}
              icon={<DollarSign className="w-8 h-8" />}
              color="green"
              trend="+12.5%"
            />
            <MetricCard
              title="Total Expenses"
              value={`₹${financialMetrics.totalExpenses.toLocaleString()}`}
              icon={<ShoppingCart className="w-8 h-8" />}
              color="red"
              trend="-5.2%"
            />
            <MetricCard
              title="Net Profit"
              value={`₹${financialMetrics.netProfit.toLocaleString()}`}
              icon={<TrendingUp className="w-8 h-8" />}
              color="blue"
              trend="+18.3%"
            />
            <MetricCard
              title="Cash Balance"
              value={`₹${financialMetrics.cashBalance.toLocaleString()}`}
              icon={<Activity className="w-8 h-8" />}
              color="purple"
            />
          </div>
        </>
      )}

      {/* System Stats */}
      <h2 className="text-xl font-bold text-gray-900 mb-4">System Statistics</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Documents"
          value={stats.documents}
          icon={<Database className="w-8 h-8" />}
          linkTo="/knowledge-base"
          linkText="Manage"
        />
        <StatCard
          title="Processed Docs"
          value={stats.processedDocuments}
          icon={<CheckCircle className="w-8 h-8" />}
          color="green"
        />
        <StatCard
          title="Vector Chunks"
          value={stats.totalChunks}
          icon={<Activity className="w-8 h-8" />}
          color="purple"
        />
        <StatCard
          title="Conversations"
          value={stats.conversations}
          icon={<Users className="w-8 h-8" />}
          linkTo="/chat"
          linkText="Chat"
        />
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ActionCard
            title="Ask AI About Finances"
            description="Get insights from your Tally data"
            linkTo="/chat"
            color="blue"
          />
          <ActionCard
            title="View Financial Reports"
            description="Detailed analytics and dashboards"
            linkTo="/tally-analytics"
            color="green"
          />
          <ActionCard
            title="Upload Documents"
            description="Add more data to your knowledge base"
            linkTo="/knowledge-base"
            color="purple"
          />
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon, color, trend }) {
  const colorClasses = {
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    blue: 'bg-blue-50 text-blue-600',
    purple: 'bg-purple-50 text-purple-600',
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
        {trend && (
          <span className={`text-sm font-semibold ${
            trend.startsWith('+') ? 'text-green-600' : 'text-red-600'
          }`}>
            {trend}
          </span>
        )}
      </div>
      <h3 className="text-gray-600 text-sm mb-1">{title}</h3>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

function StatCard({ title, value, icon, color = 'blue', linkTo, linkText }) {
  const colorClass = `text-${color}-600`;
  
  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <div className={`${colorClass}`}>{icon}</div>
      </div>
      <h3 className="text-gray-600 text-sm mb-1">{title}</h3>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
      {linkTo && (
        <Link
          to={linkTo}
          className="mt-3 inline-block text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          {linkText} →
        </Link>
      )}
    </div>
  );
}

function ActionCard({ title, description, linkTo, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 hover:bg-blue-100 border-blue-200',
    green: 'bg-green-50 hover:bg-green-100 border-green-200',
    purple: 'bg-purple-50 hover:bg-purple-100 border-purple-200',
  };

  return (
    <Link
      to={linkTo}
      className={`p-6 rounded-lg border-2 transition ${colorClasses[color]}`}
    >
      <h3 className="font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </Link>
  );
}

export default Dashboard;
