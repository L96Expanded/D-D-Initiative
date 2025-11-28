import * as React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import Encounter from './pages/Encounter';
import EncounterControl from './components/EncounterControl';
import EncounterDisplayPage from './pages/EncounterDisplayPage';

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode;
}
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }: ProtectedRouteProps) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="glass p-8 text-center">
          <div className="spinner mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }
  
  return user ? <>{children}</> : <Navigate to="/login" replace />;
};

// Public Route Component (redirect if authenticated)
interface PublicRouteProps {
  children: React.ReactNode;
}
const PublicRoute: React.FC<PublicRouteProps> = ({ children }: PublicRouteProps) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="glass p-8 text-center">
          <div className="spinner mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }
  
  return user ? <Navigate to="/home" replace /> : <>{children}</>;
};

const App: React.FC = () => {
  // Load Ko-fi widget on mount (except for encounter display page)
  React.useEffect(() => {
    // Check if current path is encounter-display
    const isDisplayPage = window.location.pathname.includes('/encounter-display/');
    
    // Don't load Ko-fi widget on encounter display page
    if (isDisplayPage) {
      return;
    }
    
    // Load Ko-fi overlay script
    const script = document.createElement('script');
    script.src = 'https://storage.ko-fi.com/cdn/scripts/overlay-widget.js';
    script.async = true;
    script.onload = () => {
      // Initialize Ko-fi widget after script loads
      if ((window as any).kofiWidgetOverlay) {
        (window as any).kofiWidgetOverlay.draw('Barope', {
          'type': 'floating-chat',
          'floating-chat.donateButton.text': 'Support Me',
          'floating-chat.donateButton.background-color': '#00b9fe',
          'floating-chat.donateButton.text-color': '#fff'
        });
      }
    };
    document.body.appendChild(script);

    return () => {
      // Cleanup script on unmount
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, []);

  return (
    <Router>
      <AuthProvider>
        <div className="App">
          <Routes>
            {/* Public routes */}
            <Route
              path="/login"
              element={
                <PublicRoute>
                  <Login />
                </PublicRoute>
              }
            />
            <Route
              path="/register"
              element={
                <PublicRoute>
                  <Register />
                </PublicRoute>
              }
            />
            
            {/* Protected routes */}
            <Route
              path="/home"
              element={
                <ProtectedRoute>
                  <Home />
                </ProtectedRoute>
              }
            />
            <Route
              path="/encounter/:id"
              element={
                <ProtectedRoute>
                  <EncounterControl />
                </ProtectedRoute>
              }
            />
            <Route
              path="/encounter-display/:id"
              element={
                <ProtectedRoute>
                  <EncounterDisplayPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/encounters"
              element={
                <ProtectedRoute>
                  <Home />
                </ProtectedRoute>
              }
            />
            
            {/* Legacy route for backward compatibility */}
            <Route
              path="/encounter-legacy/:id"
              element={
                <ProtectedRoute>
                  <Encounter />
                </ProtectedRoute>
              }
            />
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/home" replace />} />
            
            {/* 404 fallback */}
            <Route
              path="*"
              element={
                <div className="min-h-screen flex items-center justify-center">
                  <div className="glass p-8 text-center">
                    <h1>404 - Page Not Found</h1>
                    <p className="mb-4">The page you're looking for doesn't exist.</p>
                    <a href="/home" className="btn btn-primary">
                      Go Home
                    </a>
                  </div>
                </div>
              }
            />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  );
};

export default App;