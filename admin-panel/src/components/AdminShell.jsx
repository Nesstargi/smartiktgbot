import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export default function AdminShell() {
  const { logout, hasPermission, isSuperAdmin } = useAuth();
  const navigate = useNavigate();

  const links = [
    { to: "/", label: "Дашборд", show: true },
    {
      to: "/catalog",
      label: "Каталог",
      show:
        hasPermission("manage_categories") ||
        hasPermission("manage_subcategories") ||
        hasPermission("manage_products"),
    },
    { to: "/promotions", label: "Акции", show: hasPermission("manage_promotions") },
    { to: "/leads", label: "Заявки", show: hasPermission("manage_leads") },
    {
      to: "/notifications",
      label: "Уведомления",
      show: hasPermission("manage_notifications"),
    },
    {
      to: "/bot-settings",
      label: "Настройки бота",
      show:
        hasPermission("manage_bot_settings") ||
        hasPermission("manage_consultation") ||
        hasPermission("manage_about"),
    },
    { to: "/users", label: "Админы", show: isSuperAdmin },
  ];

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1 className="brand">SmartIKT</h1>
        <nav className="nav-list">
          {links
            .filter((link) => link.show)
            .map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === "/"}
                className={({ isActive }) => `nav-link ${isActive ? "nav-link-active" : ""}`}
              >
                {link.label}
              </NavLink>
            ))}
        </nav>
        <button className="ghost-btn" onClick={handleLogout}>
          Выйти
        </button>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
