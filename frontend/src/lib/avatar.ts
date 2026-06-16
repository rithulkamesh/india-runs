// Deterministic dicebear avatars — no backend asset hosting needed.
const STYLE = 'notionists';

export function avatarUrl(seed: string, size = 96): string {
  const s = encodeURIComponent(seed || 'india-runs');
  return `https://api.dicebear.com/9.x/${STYLE}/svg?seed=${s}&radius=12&backgroundColor=eaf3ff,e6e9ff,ffe6cc,f3f3f3&size=${size}`;
}
