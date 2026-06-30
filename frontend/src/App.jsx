import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './store/AppContext';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import Files from './pages/Files/Files';
import Downloads from './pages/Downloads/Downloads';
import Peers from './pages/Peers/Peers';
import Statistics from './pages/Statistics/Statistics';
import Settings from './pages/Settings/Settings';
import Developer from './pages/Developer/Developer';

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/files" element={<Files />} />
            <Route path="/downloads" element={<Downloads />} />
            <Route path="/peers" element={<Peers />} />
            <Route path="/statistics" element={<Statistics />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/developer" element={<Developer />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}
