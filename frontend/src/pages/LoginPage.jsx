import { useState } from 'react';
import { login, register } from '../api/client';
import { useAuth } from '../context/AuthContext';
import './LoginPage.css';

export default function LoginPage() {
  const { loginUser } = useAuth();
  const [activeTab, setActiveTab] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!username || !password) {
      setError('Please enter both username and password.');
      return;
    }

    setLoading(true);
    try {
      if (activeTab === 'login') {
        const data = await login(username, password);
        loginUser(data.username);
      } else {
        await register(username, password);
        setSuccess('Account created! You can now sign in.');
        setActiveTab('login');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      {/* Ambient background effects */}
      <div className="login-bg">
        <div className="bg-orb orb-1" />
        <div className="bg-orb orb-2" />
        <div className="bg-orb orb-3" />
        <div className="bg-grid" />
      </div>

      <div className="login-container animate-in">
        {/* Header */}
        <div className="login-header">
          <div className="login-logo animate-float">
            <span className="logo-icon">💊</span>
          </div>
          <h1 className="login-title font-display">
            <span className="text-gradient">Clarity Rx</span>
          </h1>
          <p className="login-subtitle">AI Prescription Assistant</p>
        </div>

        {/* Tabs */}
        <div className="login-tabs">
          <button
            className={`tab-btn ${activeTab === 'login' ? 'active' : ''}`}
            onClick={() => { setActiveTab('login'); setError(''); setSuccess(''); }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            Sign In
          </button>
          <button
            className={`tab-btn ${activeTab === 'register' ? 'active' : ''}`}
            onClick={() => { setActiveTab('register'); setError(''); setSuccess(''); }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>
            Sign Up
          </button>
        </div>

        {/* Form */}
        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-field">
            <label className="field-label font-mono">Username</label>
            <div className="input-wrap">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <input
                id="login-username"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
              />
            </div>
          </div>

          <div className="form-field">
            <label className="field-label font-mono">Password</label>
            <div className="input-wrap">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              <input
                id="login-password"
                type="password"
                placeholder={activeTab === 'register' ? 'Min 6 characters' : 'Enter your password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={activeTab === 'register' ? 'new-password' : 'current-password'}
              />
            </div>
          </div>

          {error && (
            <div className="form-alert alert-error">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
              {error}
            </div>
          )}

          {success && (
            <div className="form-alert alert-success">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              {success}
            </div>
          )}

          <button
            id="login-submit"
            type="submit"
            className="submit-btn"
            disabled={loading}
          >
            {loading ? (
              <div className="btn-loading">
                <div className="btn-spinner" />
                <span>{activeTab === 'login' ? 'Signing in...' : 'Creating account...'}</span>
              </div>
            ) : (
              <span>{activeTab === 'login' ? 'Sign In' : 'Create Account'}</span>
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="login-footer">
          <div className="footer-badges">
            <span className="footer-badge">
              <span className="badge-dot dot-green" />
              AI-Powered
            </span>
            <span className="footer-divider">·</span>
            <span className="footer-badge">
              <span className="badge-dot dot-cyan" />
              Secure
            </span>
            <span className="footer-divider">·</span>
            <span className="footer-badge">
              <span className="badge-dot dot-amber" />
              HIPAA-Aware
            </span>
          </div>
          <p className="footer-disclaimer">
            Clarity Rx helps understand prescriptions. Always consult a doctor.
          </p>
        </div>
      </div>
    </div>
  );
}
