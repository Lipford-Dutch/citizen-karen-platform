import { BrowserRouter, Link, Navigate, Route, Routes } from "react-router-dom";
import ComplaintsPage from "./pages/ComplaintsPage";
import StatusLookupPage from "./pages/StatusLookupPage";

function App() {
  return (
    <BrowserRouter>
      <main>
        <h1>Citizen Karen Platform</h1>
        <nav aria-label="Primary">
          <ul>
            <li>
              <Link to="/complaints">Complaints</Link>
            </li>
            <li>
              <Link to="/status-lookup">Status Lookup</Link>
            </li>
          </ul>
        </nav>
        <Routes>
          <Route path="/" element={<Navigate to="/complaints" replace />} />
          <Route path="/complaints" element={<ComplaintsPage />} />
          <Route path="/status-lookup" element={<StatusLookupPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
