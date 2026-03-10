export function buildMediaUrl(pathOrUrl) {
  if (!pathOrUrl) return "";
  if (pathOrUrl.startsWith("http://") || pathOrUrl.startsWith("https://")) {
    return pathOrUrl;
  }

  const base = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");
  const path = pathOrUrl.startsWith("/") ? pathOrUrl : `/${pathOrUrl}`;
  return `${base}${path}`;
}
