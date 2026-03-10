import { Navigate, Route, Routes } from "react-router-dom";

import "./App.css";
import RequireAuth from "./auth/RequireAuth";
import RequirePermission from "./auth/RequirePermission";
import RequireSuperAdmin from "./auth/RequireSuperAdmin";
import AdminShell from "./components/AdminShell";
import BotSettingsPage from "./pages/BotSettingsPage";
import CatalogPage from "./pages/CatalogPage";
import Dashboard from "./pages/Dashboard";
import LeadsPage from "./pages/LeadsPage";
import Login from "./pages/Login";
import NotificationsPage from "./pages/NotificationsPage";
import PromotionsPage from "./pages/PromotionsPage";
import UsersPage from "./pages/UsersPage";

function ProtectedLayout() {
  return (
    <RequireAuth>
      <AdminShell />
    </RequireAuth>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route path="/" element={<ProtectedLayout />}>
        <Route index element={<Dashboard />} />
        <Route
          path="catalog"
          element={
            <RequirePermission allOf={["manage_categories", "manage_subcategories", "manage_products"]}>
              <CatalogPage />
            </RequirePermission>
          }
        />
        <Route
          path="promotions"
          element={
            <RequirePermission anyOf={["manage_promotions"]}>
              <PromotionsPage />
            </RequirePermission>
          }
        />
        <Route
          path="leads"
          element={
            <RequirePermission anyOf={["manage_leads"]}>
              <LeadsPage />
            </RequirePermission>
          }
        />
        <Route
          path="notifications"
          element={
            <RequirePermission anyOf={["manage_notifications"]}>
              <NotificationsPage />
            </RequirePermission>
          }
        />
        <Route
          path="bot-settings"
          element={
            <RequirePermission anyOf={["manage_bot_settings", "manage_consultation", "manage_about"]}>
              <BotSettingsPage />
            </RequirePermission>
          }
        />
        <Route
          path="users"
          element={
            <RequireSuperAdmin>
              <UsersPage />
            </RequireSuperAdmin>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
