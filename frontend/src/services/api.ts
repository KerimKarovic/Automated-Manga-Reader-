import { API_BASE_URL } from '../config/api';
import { AudioGenerateResponse, AudioStatusResponse, Manga, MangaDexChapter, MangaDexManga, OcrChapterResult, OcrChapterRunResponse, Page } from '../types';

function extractApiErrorMessage(detail: unknown): string {
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  if (detail && typeof detail === 'object') {
    const detailRecord = detail as Record<string, unknown>;
    if (typeof detailRecord.message === 'string' && detailRecord.message.trim()) {
      return detailRecord.message;
    }
    if ('detail' in detailRecord) {
      return extractApiErrorMessage(detailRecord.detail);
    }
  }

  return 'Request failed';
}

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
    throw new Error(extractApiErrorMessage(detail));
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
  generateChapterAudio: (chapterId: string, pageText?: string) =>
    request<AudioGenerateResponse>(`/audio/chapter/${encodeURIComponent(chapterId)}/generate`, {
      method: 'POST',
      body: pageText ? JSON.stringify({ text: pageText }) : undefined,
    }),
  getChapterAudioStatus: (chapterId: string) =>
    request<AudioStatusResponse>(`/audio/chapter/${encodeURIComponent(chapterId)}`),
  runChapterOcr: (chapterId: string) =>
    request<OcrChapterRunResponse>(`/ocr/chapter/${encodeURIComponent(chapterId)}`, {
      method: 'POST',
    }),
  getChapterOcr: (chapterId: string) =>
    request<OcrChapterResult>(`/ocr/chapter/${encodeURIComponent(chapterId)}`),
};
