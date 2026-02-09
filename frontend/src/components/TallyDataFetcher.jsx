import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiService } from '../services/apiService.js';

const TallyDataFetcher = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isDataFetching, setIsDataFetching] = useState(false);
  const [connectionDetails, setConnectionDetails] = useState(null);
  const [realTimeData, setRealTimeData] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [refreshInterval, setRefreshInterval] = useState(30);
  const [loading, setLoading] = useState(false);

  const intervalRef = useRef(null);

  const showMessage = useCallback((msg, type = 'info') => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => setMessage(''), 4000);
  }, []);

  const fetchTallyData = useCallback(async () => {
    try {
      const response = await apiService.getTallyLiveData();

      if (response.success) {
        setRealTimeData(response.data);
        setLastUpdated(new Date());
      } else {
        setIsConnected(false);
        showMessage('⚠️ Data fetch failed', 'warning');
      }
    } catch (error) {
      console.error('Error fetching Tally data:', error);
      setIsConnected(false);
      showMessage('❌ Lost connection to Tally', 'error');
    }
  }, [showMessage]);

  const stopDataFetching = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsDataFetching(false);
    showMessage('⏹️ Stopped real-time data fetching', 'info');
  }, [showMessage]);

  const startDataFetching = useCallback(async () => {
    if (!isConnected) {
      showMessage('⚠️ Please connect to Tally first', 'warning');
      return;
    }

    setIsDataFetching(true);
    showMessage('🔄 Started real-time data fetching', 'success');

    await fetchTallyData();

    intervalRef.current = setInterval(() => {
      fetchTallyData();
    }, refreshInterval * 1000);
  }, [isConnected, refreshInterval, fetchTallyData, showMessage]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopDataFetching();
    };
  }, [stopDataFetching]);

  const connectToTally = async () => {
    setLoading(true);
    try {
      const odbcConfig = {
        dsn: 'TallyODBC',
        server: 'localhost',
        port: '9000',
        database: 'TallyDB',
        username: '',
        password: '',
        driver: 'Tally.ODBC.9.0'
      };

      const response = await apiService.connectTallyOdbc(odbcConfig);

      if (response.success) {
        setIsConnected(true);
        setConnectionDetails({
          status: 'Connected',
          type: 'ODBC',
          server: odbcConfig.server,
          port: odbcConfig.port,
          timestamp: new Date().toLocaleString()
        });
        showMessage('✅ Connected to Tally successfully!', 'success');
      } else {
        showMessage(`❌ Connection failed: ${response.error}`, 'error');
        setIsConnected(false);
      }
    } catch (error) {
      showMessage(`❌ Connection error: ${error.message}`, 'error');
      setIsConnected(false);
    } finally {
      setLoading(false);
    }
  };

  const disconnectFromTally = async () => {
    try {
      await apiService.disconnectTallyOdbc();
      setIsConnected(false);
      setConnectionDetails(null);
      stopDataFetching();
      showMessage('🔌 Disconnected from Tally', 'info');
    } catch (error) {
      showMessage(`❌ Disconnect error: ${error.message}`, 'error');
    }
  };

  const formatNumber = (num) => {
    if (!num) return '0.00';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(num);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-6">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Tally Real-Time Data</h1>
          <p className="text-gray-600">Connect and fetch live data from your Tally system</p>
        </div>

        {message && (
          <div className={`mb-4 p-3 rounded-md text-sm ${
            messageType === 'success' ? 'bg-green-50 border border-green-200 text-green-800' :
            messageType === 'error' ? 'bg-red-50 border border-red-200 text-red-800' :
            messageType === 'warning' ? 'bg-yellow-50 border border-yellow-200 text-yellow-800' :
            'bg-blue-50 border border-blue-200 text-blue-800'
          }`}>
            {message}
          </div>
        )}

        {/* Connection Control Panel */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Connection Status</h2>
              <div className="flex items-center mt-1">
                <div className={`w-3 h-3 rounded-full mr-2 ${
                  isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`}></div>
                <span className={`text-sm font-medium ${
                  isConnected ? 'text-green-700' : 'text-red-700'
                }`}>
                  {isConnected ? 'Connected to Tally' : 'Disconnected'}
                </span>
              </div>
            </div>

            <div className="flex space-x-3">
              {!isConnected ? (
                <button
                  onClick={connectToTally}
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50 flex items-center"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Connecting...
                    </>
                  ) : (
                    <>🔗 Connect to Tally</>
                  )}
                </button>
              ) : (
                <button
                  onClick={disconnectFromTally}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center"
                >
                  🔌 Disconnect
                </button>
              )}
            </div>
          </div>

          {connectionDetails && (
            <div className="bg-gray-50 rounded p-3 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <div><strong>Type:</strong> {connectionDetails.type}</div>
                <div><strong>Connected:</strong> {connectionDetails.timestamp}</div>
                {connectionDetails.server && (
                  <>
                    <div><strong>Server:</strong> {connectionDetails.server}</div>
                    <div><strong>Port:</strong> {connectionDetails.port}</div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Data Fetching Control */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Real-Time Data Fetching</h2>
              <div className="flex items-center mt-1">
                <div className={`w-3 h-3 rounded-full mr-2 ${
                  isDataFetching ? 'bg-blue-500 animate-pulse' : 'bg-gray-400'
                }`}></div>
                <span className={`text-sm font-medium ${
                  isDataFetching ? 'text-blue-700' : 'text-gray-600'
                }`}>
                  {isDataFetching ? 'Fetching data automatically' : 'Data fetching stopped'}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <label className="text-sm text-gray-600">Interval:</label>
                <select
                  value={refreshInterval}
                  onChange={(e) => setRefreshInterval(Number(e.target.value))}
                  disabled={isDataFetching}
                  className="border border-gray-300 rounded px-2 py-1 text-sm"
                >
                  <option value={10}>10s</option>
                  <option value={30}>30s</option>
                  <option value={60}>1min</option>
                  <option value={300}>5min</option>
                </select>
              </div>

              {!isDataFetching ? (
                <button
                  onClick={startDataFetching}
                  disabled={!isConnected}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50 flex items-center"
                >
                  ▶️ Start Fetching Data
                </button>
              ) : (
                <button
                  onClick={stopDataFetching}
                  className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center"
                >
                  ⏹️ Stop Fetching
                </button>
              )}
            </div>
          </div>

          {lastUpdated && (
            <div className="text-sm text-gray-500">
              Last updated: {lastUpdated.toLocaleString()}
            </div>
          )}
        </div>

        {/* Real-Time Data Display */}
        {realTimeData && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Live Financial Data</h2>
              {isDataFetching && (
                <div className="flex items-center text-sm text-blue-600">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                  Auto-updating every {refreshInterval}s
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="text-2xl mr-3">📊</div>
                  <div>
                    <p className="text-sm font-medium text-blue-700">Total Transactions</p>
                    <p className="text-xl font-bold text-blue-900">
                      {realTimeData.summary?.total_transactions || 0}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="text-2xl mr-3">💰</div>
                  <div>
                    <p className="text-sm font-medium text-green-700">Cash Inflows</p>
                    <p className="text-xl font-bold text-green-900">
                      {formatNumber(realTimeData.summary?.cash_inflows)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-red-50 to-red-100 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="text-2xl mr-3">💸</div>
                  <div>
                    <p className="text-sm font-medium text-red-700">Cash Outflows</p>
                    <p className="text-xl font-bold text-red-900">
                      {formatNumber(realTimeData.summary?.cash_outflows)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-center space-x-4">
          <button
            onClick={fetchTallyData}
            disabled={!isConnected}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
          >
            🔄 Fetch Data Now
          </button>

          <button
            onClick={() => setRealTimeData(null)}
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            🗑️ Clear Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default TallyDataFetcher;
