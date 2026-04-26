import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import Dashboard from './pages/Dashboard';
import ChatPage from './pages/ChatPage';
import './styles/main.css';

function App() {
  const lastFileId = localStorage.getItem('lastFileId') || '0';
  
  return (
    <BrowserRouter>
      <nav className="navbar">
        <NavLink to="/" className="navbar-brand">
          <div className="logo-icon">🧠</div>
          <span>FinCopilot</span>
        </NavLink>
        <div className="navbar-links">
          <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>
            Upload
          </NavLink>
          <NavLink to={`/dashboard/${lastFileId}`} className={({ isActive }) => isActive ? 'active' : ''}>
            Dashboard
          </NavLink>
          <NavLink to="/chat" className={({ isActive }) => isActive ? 'active' : ''}>
            Chat
          </NavLink>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/dashboard/:fileId" element={<Dashboard />} />
        <Route path="/chat" element={<ChatPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
