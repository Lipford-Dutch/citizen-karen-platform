import { Route, Routes } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { AccessibilityPage } from "./pages/AccessibilityPage";
import { DirectoryPage } from "./pages/DirectoryPage";
import { FccComplaintPage } from "./pages/FccComplaintPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { PrivacyPage } from "./pages/PrivacyPage";
import { SecurityPage } from "./pages/SecurityPage";
import { TrackCasePage } from "./pages/TrackCasePage";


export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<DirectoryPage />} />
        <Route path="file" element={<FccComplaintPage />} />
        <Route path="track" element={<TrackCasePage />} />
        <Route path="privacy" element={<PrivacyPage />} />
        <Route path="accessibility" element={<AccessibilityPage />} />
        <Route path="security" element={<SecurityPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
