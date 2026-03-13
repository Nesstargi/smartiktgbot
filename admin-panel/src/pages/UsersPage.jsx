import { useEffect, useMemo, useState } from "react";

import {
  createAdminUser,
  deleteAdminUser,
  getAdminUsers,
  getAvailablePermissions,
  updateAdminPermissions,
  updateAdminRole,
} from "../api/users.api";

const PERMISSION_LABELS = {
  manage_categories: "Категории",
  manage_subcategories: "Подкатегории",
  manage_products: "Товары",
  manage_promotions: "Акции",
  manage_leads: "Заявки",
  manage_bot_settings: "Настройки бота",
  manage_notifications: "Рассылки",
  manage_users: "Управление админами",
  manage_consultation: "Консультация",
  manage_about: "О компании",
};

function formatPermission(perm) {
  return PERMISSION_LABELS[perm] || perm;
}

function normalizePermissions(values) {
  return Array.from(new Set(values)).sort();
}

function getErrorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    const messages = detail.map((item) => item?.msg).filter(Boolean);
    if (messages.length) return messages.join(", ");
    return "Ошибка валидации";
  }
  if (detail) return detail;
  if (error?.message) return error.message;
  return "Не удалось создать администратора";
}

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [availablePermissions, setAvailablePermissions] = useState([]);
  const [loading, setLoading] = useState(true);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSuperAdmin, setIsSuperAdmin] = useState(false);
  const [selectedPermissions, setSelectedPermissions] = useState([]);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState("");
  const [createSuccess, setCreateSuccess] = useState("");

  const [editingUserId, setEditingUserId] = useState(null);
  const [editingPermissions, setEditingPermissions] = useState([]);
  const [savingPermissionsFor, setSavingPermissionsFor] = useState(null);

  const canSubmit = useMemo(() => email.trim() && password.trim().length >= 8, [email, password]);
  const passwordInvalid = useMemo(
    () => password.trim().length > 0 && password.trim().length < 8,
    [password],
  );

  const load = async () => {
    setLoading(true);
    try {
      const [u, p] = await Promise.all([getAdminUsers(), getAvailablePermissions()]);
      setUsers(u || []);
      setAvailablePermissions(p || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const togglePermission = (perm) => {
    setSelectedPermissions((prev) =>
      prev.includes(perm) ? prev.filter((p) => p !== perm) : [...prev, perm],
    );
  };

  const onCreate = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setCreateError("Введите email");
      return;
    }
    if (password.trim().length < 8) {
      setCreateError("Пароль должен быть не короче 8 символов");
      return;
    }

    setCreateError("");
    setCreateSuccess("");
    setCreating(true);
    try {
      await createAdminUser({
        email: email.trim(),
        password: password.trim(),
        is_super_admin: isSuperAdmin,
        permissions: normalizePermissions(selectedPermissions),
      });

      setEmail("");
      setPassword("");
      setIsSuperAdmin(false);
      setSelectedPermissions([]);
      setCreateSuccess("Администратор создан");
      await load();
    } catch (error) {
      setCreateError(getErrorMessage(error));
    } finally {
      setCreating(false);
    }
  };

  const onStartEditPermissions = (user) => {
    setEditingUserId(user.id);
    setEditingPermissions([...(user.permissions || [])]);
  };

  const onCancelEditPermissions = () => {
    setEditingUserId(null);
    setEditingPermissions([]);
  };

  const onToggleEditingPermission = (perm) => {
    setEditingPermissions((prev) =>
      prev.includes(perm) ? prev.filter((p) => p !== perm) : [...prev, perm],
    );
  };

  const onSavePermissions = async (user) => {
    setSavingPermissionsFor(user.id);
    try {
      await updateAdminPermissions(user.id, normalizePermissions(editingPermissions));
      setEditingUserId(null);
      setEditingPermissions([]);
      await load();
    } finally {
      setSavingPermissionsFor(null);
    }
  };

  const onToggleSuperAdmin = async (user) => {
    const has = (user.roles || []).includes("super_admin");
    await updateAdminRole(user.id, !has);
    await load();
  };

  const onDelete = async (user) => {
    if (!window.confirm(`Удалить пользователя ${user.email}?`)) return;
    await deleteAdminUser(user.id);
    await load();
  };

  return (
    <section>
      <h2 className="page-title">Пользователи и права</h2>

      <article className="card">
        <h3>Добавить администратора</h3>
        <form className="stack-form" onSubmit={onCreate}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Пароль (мин. 8 символов)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={8}
            required
            aria-invalid={passwordInvalid}
            style={
              passwordInvalid
                ? { borderColor: "#e11d48", outlineColor: "#e11d48" }
                : undefined
            }
          />

          <label className="checkbox">
            <input
              type="checkbox"
              checked={isSuperAdmin}
              onChange={(e) => setIsSuperAdmin(e.target.checked)}
            />
            Назначить super_admin
          </label>

          <div className="permissions-grid">
            {availablePermissions.map((perm) => (
              <label key={perm} className="checkbox" title={perm}>
                <input
                  type="checkbox"
                  checked={selectedPermissions.includes(perm)}
                  onChange={() => togglePermission(perm)}
                />
                {formatPermission(perm)}
              </label>
            ))}
          </div>

          <button type="submit" disabled={!canSubmit || creating}>
            {creating ? "Создание..." : "Создать"}
          </button>
          {createError && <p className="error-text">{createError}</p>}
          {createSuccess && <p className="success-text">{createSuccess}</p>}
        </form>
      </article>

      <article className="card">
        <h3>Список админов</h3>
        {loading ? (
          <p className="muted">Загрузка...</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Роли</th>
                <th>Права</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {users.map((user) => {
                const isEditing = editingUserId === user.id;
                const isSaving = savingPermissionsFor === user.id;

                return (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td>{user.email}</td>
                    <td>{(user.roles || []).join(", ") || "-"}</td>
                    <td>
                      {isEditing ? (
                        <div className="permissions-grid permissions-grid-inline">
                          {availablePermissions.map((perm) => (
                            <label key={perm} className="checkbox" title={perm}>
                              <input
                                type="checkbox"
                                checked={editingPermissions.includes(perm)}
                                onChange={() => onToggleEditingPermission(perm)}
                              />
                              {formatPermission(perm)}
                            </label>
                          ))}
                        </div>
                      ) : (
                        (user.permissions || []).map(formatPermission).join(", ") || "-"
                      )}
                    </td>
                    <td className="actions">
                      {isEditing ? (
                        <>
                          <button onClick={() => onSavePermissions(user)} disabled={isSaving}>
                            {isSaving ? "Сохранение..." : "Сохранить"}
                          </button>
                          <button onClick={onCancelEditPermissions} disabled={isSaving}>
                            Отмена
                          </button>
                        </>
                      ) : (
                        <button onClick={() => onStartEditPermissions(user)}>Права</button>
                      )}

                      <button onClick={() => onToggleSuperAdmin(user)}>
                        {(user.roles || []).includes("super_admin") ? "Снять super" : "Сделать super"}
                      </button>
                      <button onClick={() => onDelete(user)}>Удалить</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </article>
    </section>
  );
}

