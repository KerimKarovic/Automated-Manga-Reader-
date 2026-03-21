import { API_BASE_URL } from '../config/api';
import { AudioStatus, Manga, MangaDexChapter, MangaDexManga, Page } from '../types';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
    ...init,
  });

  if (!response.ok) {
    let detail: unknown;
    try {
      detail = await response.json();
    } catch {
      detail = await response.text();
    }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }

  return response.json() as Promise<T>;
}

export const api = {
  getHealth: () => request<{ status: string; service: string; version: string }>('/health'),
  listLocalManga: () => request<Manga[]>('/manga'),
  createLocalManga: (payload: {
    title: string;
    author?: string | null;
    mangadex_id?: string | null;
    cover_url?: string | null;
    description?: string | null;
    status?: string | null;
  }) =>
    request<Manga>('/manga', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  searchMangaDex: (title: string) =>
    request<MangaDexManga[]>(`/mangadex/search?title=${encodeURIComponent(title)}`),
  getMangaDexChapters: (mangaDexId: string, language = 'en') =>
    request<MangaDexChapter[]>(
      `/mangadex/${encodeURIComponent(mangaDexId)}/chapters?language=${encodeURIComponent(language)}`
    ),
  storeChapter: (chapterId: string) =>
    request<{ chapter_id: string; manga_id: number; created_chapter: boolean; pages_created: number; total_pages: number }>(
      `/mangadex/store-chapter/${encodeURIComponent(chapterId)}`,
      { method: 'POST' }
    ),
  getChapterPages: (chapterId: string) =>
    request<Page[]>(`/chapters/${encodeURIComponent(chapterId)}/pages`),
  getAudioStatus: (chapterId: string) =>
    request<AudioStatus>(`/audio/chapter/${encodeURIComponent(chapterId)}`),
};
