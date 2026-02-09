import React, { useState, useEffect } from 'react';
import apiService from '../services/apiService.js';
import LoadingSpinner from '../components/LoadingSpinner.jsx';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { 
  TrendingUp, 
  DollarSign, 
  RefreshCw, 
  Download,
  AlertCircle,
  CheckCircle,
  Building2
} from 'lucide-react';
import toast from 'react-hot-toast';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

function TallyAnalytics() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [tallyConnected, setTallyConnected] = useState(false);
  const [companyInfo, setCompanyInfo] = useState(null);
  const [financialData, setFinancialData] = useState(null);
  const [ledgers, setLedgers] = useState([]);
  const [vouchers, setVouchers] = useState([]);
  const [dataSource, setDataSource] = useState('unknown');
  
  // 🔥 NEW: Multi-company support
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState('');
  const [loadingCompanies, setLoadingCompanies] = useState(false);
  
  const [dateRange, setDateRange] = useState({
    from: '20240401',
    to: '20250331'
  });

  useEffect(() => {
    loadCompanies();
  }, []);

  useEffect(() => {
    if (selectedCompany) {
      loadTallyData();
    }
  }, [selectedCompany]);

  // 🔥 NEW: Load available companies
  const loadCompanies = async () => {
    try {
      setLoadingCompanies(true);
      
      // Test connection first
      const connectionTest = await apiService.testTallyConnection().catch(() => ({ 
        status: 'disconnected' 
      }));
      
      setTallyConnected(connectionTest.status === 'connected');
      
      if (connectionTest.status === 'connected') {
        setCompanyInfo(connectionTest);
        
        // Fetch all companies
        const companiesResult = await apiService.getTallyCompanies().catch(() => ({
          companies: []
        }));
        
        const companyList = companiesResult.companies || [];
        setCompanies(companyList);
        
        // Auto-select first company
        if (companyList.length > 0 && !selectedCompany) {
          setSelectedCompany(companyList[0].name);
        }
        
        toast.success(`Found ${companyList.length} company(ies)`);
      } else {
        toast.error('Tally not connected');
      }
    } catch (error) {
      console.error('❌ Error loading companies:', error);
      toast.error('Failed to load companies');
    } finally {
      setLoadingCompanies(false);
    }
  };

  const loadTallyData = async () => {
    try {
      setLoading(true);

      if (!selectedCompany) {
        toast.error('Please select a company');
        return;
      }

      console.log('📊 Loading data for company:', selectedCompany);

      // 🔥 FIXED: Pass company_name to all API calls
      const [ledgersResult, vouchersResult, metricsResult] = await Promise.all([
        apiService.getTallyLedgers({ company_name: selectedCompany }).catch(() => ({ 
          status: 'error', ledgers: [] 
        })),
        apiService.getTallyVouchers({ 
          company_name: selectedCompany,
          from_date: dateRange.from,
          to_date: dateRange.to
        }).catch(() => ({ status: 'error', vouchers: [] })),
        apiService.getTallyFinancialMetrics({ company_name: selectedCompany }).catch(() => ({ 
          status: 'error', metrics: null 
        }))
      ]);

      console.log('📊 Metrics Result:', metricsResult);

      // Extract ledgers
      let ledgersData = [];
      if (ledgersResult.ledgers) {
        ledgersData = ledgersResult.ledgers;
      } else if (ledgersResult.data?.ledgers) {
        ledgersData = ledgersResult.data.ledgers;
      } else if (Array.isArray(ledgersResult.data)) {
        ledgersData = ledgersResult.data;
      }

      // Extract vouchers
      let vouchersData = [];
      if (vouchersResult.vouchers) {
        vouchersData = vouchersResult.vouchers;
      } else if (vouchersResult.data?.vouchers) {
        vouchersData = vouchersResult.data.vouchers;
      } else if (Array.isArray(vouchersResult.data)) {
        vouchersData = vouchersResult.data;
      }

      // Extract financial metrics
      let metrics = null;
      let source = 'unknown';

      if (metricsResult.status === 'success' || metricsResult.success) {
        if (metricsResult.metrics) {
          metrics = metricsResult.metrics;
          source = metricsResult.data_source || 'tally_live';
        } else if (metricsResult.data?.metrics) {
          metrics = metricsResult.data.metrics;
          source = metricsResult.data.data_source || metricsResult.data_source || 'tally_live';
        } else if (metricsResult.data && typeof metricsResult.data === 'object') {
          metrics = metricsResult.data;
          source = metricsResult.data_source || 'tally_live';
        }
      }

      console.log('📈 Parsed Metrics:', metrics, 'Source:', source);

      setLedgers(ledgersData);
      setVouchers(vouchersData);
      setFinancialData(metrics);
      setDataSource(source);

      if (source === 'demo') {
        toast.success('Using demo data. Connect Tally for real data.', {
          icon: '⚠️',
          duration: 5000
        });
      } else if (metrics) {
        toast.success('Financial data loaded successfully');
      }

    } catch (error) {
      console.error('❌ Error loading Tally data:', error);
      toast.error('Failed to load Tally data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadTallyData();
    setRefreshing(false);
    toast.success('Data refreshed successfully');
  };

  const handleExport = () => {
    const csvContent = generateCSV();
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `tally-report-${selectedCompany || 'unknown'}-${new Date().toISOString()}.csv`;
    link.click();
    toast.success('Report exported');
  };

  const generateCSV = () => {
    let csv = `Financial Report - ${selectedCompany || 'N/A'}\n\n`;
    
    if (financialData) {
      csv += 'Metric,Amount\n';
      csv += `Revenue,${financialData.revenue || 0}\n`;
      csv += `Expenses,${financialData.expenses || 0}\n`;
      csv += `Profit,${financialData.profit || 0}\n`;
      csv += `Assets,${financialData.assets || 0}\n`;
      csv += `Liabilities,${financialData.liabilities || 0}\n`;
      csv += `Net Worth,${financialData.net_worth || financialData.netWorth || 0}\n\n`;
    }

    if (ledgers.length > 0) {
      csv += '\n\nLedgers\n';
      csv += 'Name,Group,Balance\n';
      csv += ledgers.map(l => `${l.name},${l.parent || l.group || 'N/A'},${l.opening_balance || l.balance || 0}`).join('\n');
    }

    return csv;
  };

  if (loadingCompanies || (loading && !selectedCompany)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
        <p className="ml-3 text-gray-600">
          {loadingCompanies ? 'Loading companies...' : 'Loading Tally data...'}
        </p>
      </div>
    );
  }

  // Prepare chart data
  const revenueExpenseData = financialData ? [
    { 
      name: 'Revenue', 
      value: financialData.revenue || financialData.totalRevenue || 0,
    },
    { 
      name: 'Expenses', 
      value: financialData.expenses || financialData.totalExpenses || 0,
    },
    { 
      name: 'Profit', 
      value: financialData.profit || financialData.netProfit || 0,
    }
  ] : [];

  const topLedgers = ledgers
    .filter(l => l && (l.name || l.ledger_name))
    .slice(0, 10)
    .map(l => ({
      name: l.name || l.ledger_name,
      balance: Math.abs(parseFloat(l.opening_balance || l.balance || 0))
    }));

  return (
    <div className="p-6">
      {/* Header with Company Selector */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900">Tally Analytics Dashboard</h1>
          <div className="flex items-center mt-2 space-x-4">
            {/* 🔥 NEW: Company Selector */}
            {companies.length > 0 && (
              <div className="flex items-center">
                <Building2 className="w-4 h-4 mr-2 text-gray-600" />
                <select
                  value={selectedCompany}
                  onChange={(e) => setSelectedCompany(e.target.value)}
                  className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {companies.map((company, idx) => (
                    <option key={idx} value={company.name}>
                      {company.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
            
            <p className="text-gray-600 text-sm">
              Last Updated: {new Date().toLocaleTimeString()}
            </p>
            
            {dataSource === 'demo' && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                <AlertCircle className="w-3 h-3 mr-1" />
                Demo Data
              </span>
            )}
            {dataSource === 'tally_live' && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <CheckCircle className="w-3 h-3 mr-1" />
                Live Data
              </span>
            )}
          </div>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={handleExport}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      {financialData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Revenue"
            value={`₹${(financialData.revenue || financialData.totalRevenue || 0).toLocaleString()}`}
            color="green"
            icon={<DollarSign />}
          />
          <MetricCard
            title="Total Expenses"
            value={`₹${(financialData.expenses || financialData.totalExpenses || 0).toLocaleString()}`}
            color="red"
            icon={<TrendingUp />}
          />
          <MetricCard
            title="Net Profit"
            value={`₹${(financialData.profit || financialData.netProfit || 0).toLocaleString()}`}
            color="blue"
            icon={<TrendingUp />}
          />
          <MetricCard
            title="Net Worth"
            value={`₹${(financialData.net_worth || financialData.netWorth || financialData.cashBalance || 0).toLocaleString()}`}
            color="purple"
            icon={<DollarSign />}
          />
        </div>
      )}

      {/* No Data Warning */}
      {!financialData && !loading && (
        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6 mb-6">
          <div className="flex items-center">
            <AlertCircle className="w-6 h-6 text-yellow-600 mr-3" />
            <div>
              <h3 className="font-semibold text-gray-900">No Financial Data Available</h3>
              <p className="text-sm text-gray-600 mt-1">
                {tallyConnected 
                  ? `No data found for "${selectedCompany}". Try refreshing or check your Tally data.`
                  : 'Please connect to TallyPrime to view financial data.'
                }
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      {revenueExpenseData.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue vs Expenses */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Revenue vs Expenses</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={revenueExpenseData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                <Legend />
                <Bar dataKey="value" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Financial Distribution */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Financial Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={revenueExpenseData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={entry => `${entry.name}: ₹${entry.value.toLocaleString()}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {revenueExpenseData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Top Ledgers Chart */}
      {topLedgers.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Top 10 Ledgers</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={topLedgers} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={150} />
              <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
              <Legend />
              <Bar dataKey="balance" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Ledgers Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-bold text-gray-900">
            All Ledgers ({ledgers.length})
          </h3>
        </div>
        <div className="overflow-x-auto">
          {ledgers.length > 0 ? (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Group</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Balance</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {ledgers.map((ledger, idx) => {
                  const balance = parseFloat(ledger.opening_balance || ledger.balance || 0);
                  return (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {ledger.name || ledger.ledger_name || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {ledger.parent || ledger.group || 'N/A'}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-semibold ${
                        balance >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        ₹{balance.toLocaleString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <div className="p-12 text-center text-gray-500">
              <p className="text-lg">No ledger data available</p>
              <p className="text-sm mt-2">Select a company and refresh to load data</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, color, icon }) {
  const colorClasses = {
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    blue: 'bg-blue-50 text-blue-600',
    purple: 'bg-purple-50 text-purple-600',
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className={`inline-flex p-3 rounded-lg ${colorClasses[color]} mb-4`}>
        {icon}
      </div>
      <h3 className="text-gray-600 text-sm mb-1">{title}</h3>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

export default TallyAnalytics;
