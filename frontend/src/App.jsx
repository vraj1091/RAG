import React, { useState, useEffect, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext.jsx';

// Lazy load pages and components
const Login = lazy(() => import('./pages/Login.jsx'));
const Register = lazy(() => import('./pages/Register.jsx'));
const Dashboard = lazy(() => import('./pages/Dashboard.jsx'));
const KnowledgeBase = lazy(() => import('./pages/KnowledgeBase.jsx'));
const TallyDataFetcher = lazy(() => import('./components/TallyDataFetcher.jsx'));
const TallyAnalytics = lazy(() => import('./pages/tallyanalytics.jsx')); // 🔥 NEW (match file casing)
const Chat = lazy(() => import('./pages/Chat.jsx'));
const Layout = lazy(() => import('./components/Layout.jsx'));
const LoadingSpinner = lazy(() => import('./components/LoadingSpinner.jsx'));

// Show loading spinner during auth loading and lazy loading
function LoadingWrapper() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <Suspense fallback={<div />}>
        <LoadingSpinner size="large" />
      </Suspense>
    </div>
  );
}

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingWrapper />;
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingWrapper />;
  }

  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
}

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    if (saved !== null) return saved === 'true';
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Sync dark mode with localStorage and html class
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  const DarkModeToggle = () => (
    <button
      className="ml-4 px-3 py-1 rounded border border-gray-600 dark:border-gray-300 text-sm"
      onClick={() => setDarkMode(!darkMode)}
      aria-label="Toggle dark mode"
      type="button"
    >
      {darkMode ? '🌙 Dark' : '☀️ Light'}
    </button>
  );

  return (
    <div className={`App min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100`}>
      <AuthProvider>
        <Router>
          <Suspense fallback={<LoadingWrapper />}>
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
              <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

              {/* Protected Routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Layout extraHeaderRight={<DarkModeToggle />}>
                      <Dashboard />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              {/* 🔥 NEW: Tally Analytics Dashboard */}
              <Route
                path="/tally-analytics"
                element={
                  <ProtectedRoute>
                    <Layout extraHeaderRight={<DarkModeToggle />}>
                      <TallyAnalytics />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/knowledge-base"
                element={
                  <ProtectedRoute>
                    <Layout extraHeaderRight={<DarkModeToggle />}>
                      <KnowledgeBase />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route
                path="/chat"
                element={
                  <ProtectedRoute>
                    <Layout extraHeaderRight={<DarkModeToggle />}>
                      <Chat />
                    </Layout>
                  </ProtectedRoute>
                }
              />

              <Route 
                path="/tally-realtime" 
                element={
                  <ProtectedRoute>
                    <Layout extraHeaderRight={<DarkModeToggle />}>
                      <TallyDataFetcher />
                    </Layout>
                  </ProtectedRoute>
                } 
              />

              {/* Redirect root and unknown routes to dashboard */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Suspense>
        </Router>

        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: { background: '#363636', color: '#fff' },
            success: { duration: 3000, iconTheme: { primary: '#22c55e', secondary: '#fff' } },
            error: { duration: 5000, iconTheme: { primary: '#ef4444', secondary: '#fff' } },
          }}
        />
      </AuthProvider>
    </div>
  );
}

export default App;
