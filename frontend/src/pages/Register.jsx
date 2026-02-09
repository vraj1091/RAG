import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.jsx';
import LoadingSpinner from '../components/LoadingSpinner.jsx';

function Register() {
  const [formData, setFormData] = useState({
    username: '', email: '', password: '', confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const validateForm = () => {
    return formData.username.trim() && formData.email.trim() && 
           formData.password.length >= 6 && formData.password === formData.confirmPassword;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    try {
      await register(formData.username, formData.email, formData.password);
      navigate('/dashboard');
    } catch (err) {
      // Error handled by auth context
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-blue-100 py-12 px-4">
      <div className="max-w-md w-full space-y-8 animate-fade-in">
        <div className="text-center">

          <h2 className="text-3xl font-bold text-gray-900">Create your account</h2>
          <p className="mt-2 text-sm text-gray-600">Start building your personalized AI knowledge base</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">Username</label>
              <input
                id="username" name="username" type="text" required className="input-field"
                placeholder="Choose a username" value={formData.username}
                onChange={handleChange} disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                id="email" name="email" type="email" required className="input-field"
                placeholder="Enter your email" value={formData.email}
                onChange={handleChange} disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input
                id="password" name="password" type="password" required className="input-field"
                placeholder="Create a password (min 6 chars)" value={formData.password}
                onChange={handleChange} disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">Confirm Password</label>
              <input
                id="confirmPassword" name="confirmPassword" type="password" required className="input-field"
                placeholder="Confirm your password" value={formData.confirmPassword}
                onChange={handleChange} disabled={loading}
              />
            </div>

            <button type="submit" disabled={loading || !validateForm()} className="w-full btn-primary flex items-center justify-center">
              {loading ? <><LoadingSpinner size="small" color="white" className="mr-2" />Creating account...</> : 'Create account'}
            </button>

            <div className="text-center">
              <p className="text-sm text-gray-600">
                Already have an account? <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">Sign in here</Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Register;