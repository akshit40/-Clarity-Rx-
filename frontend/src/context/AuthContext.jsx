import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    return localStorage.getItem('clarityRxUser') || null;
  });

  const loginUser = (username) => {
    localStorage.setItem('clarityRxUser', username);
    setUser(username);
  };

  const logoutUser = () => {
    localStorage.removeItem('clarityRxUser');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loginUser, logoutUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
