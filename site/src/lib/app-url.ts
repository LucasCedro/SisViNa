/**
 * URL do sistema Vue (sistema-viveiro-nativas).
 * Defina VITE_APP_URL no build (.env ou ARG do Docker).
 * Ex.: http://localhost:5173  →  abre /login
 */
export function getAppLoginUrl(): string {
  const raw = (import.meta.env.VITE_APP_URL as string | undefined)?.trim() || "http://localhost:5173";
  const base = raw.replace(/\/$/, "");
  if (base.endsWith("/login")) return base;
  return `${base}/login`;
}

export function getAppRootUrl(): string {
  const login = getAppLoginUrl();
  return login.replace(/\/login\/?$/, "") || login;
}
