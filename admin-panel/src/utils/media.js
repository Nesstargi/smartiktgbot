export function buildMediaUrl(pathOrUrl) {
  if (!pathOrUrl) return "";
  if (pathOrUrl.startsWith("http://") || pathOrUrl.startsWith("https://")) {
    return pathOrUrl;
  }

  const base = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");
  const normalized = pathOrUrl.includes("/") ? pathOrUrl : `/media/${pathOrUrl}`;
  const path = normalized.startsWith("/") ? normalized : `/${normalized}`;
  return `${base}${path}`;
}
