import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.jsx';
import LoadingSpinner from '../components/LoadingSpinner.jsx';

function Login() {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.username.trim() || !formData.password.trim()) return;

    setLoading(true);
    try {
      await login(formData.username, formData.password);
      navigate('/dashboard'); // redirect on successful login
    } catch (err) {
      // Error handled by auth context toast
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-blue-100 py-12 px-4">
      <div className="max-w-md w-full space-y-8 animate-fade-in">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Welcome back</h2>
          <p className="mt-2 text-sm text-gray-600">Sign in to your AI-powered knowledge base</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">Username</label>
              <input
                id="username" name="username" type="text" required className="input-field"
                placeholder="Enter your username" value={formData.username}
                onChange={handleChange} disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input
                id="password" name="password" type="password" required className="input-field"
                placeholder="Enter your password" value={formData.password}
                onChange={handleChange} disabled={loading}
              />
            </div>

            <button type="submit" disabled={loading} className="w-full btn-primary flex items-center justify-center">
              {loading ? <><LoadingSpinner size="small" color="white" className="mr-2" />Signing in...</> : 'Sign in'}
            </button>

            <div className="text-center">
              <p className="text-sm text-gray-600">
                Don't have an account? <Link to="/register" className="font-medium text-primary-600 hover:text-primary-500">Create one now</Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Login;
