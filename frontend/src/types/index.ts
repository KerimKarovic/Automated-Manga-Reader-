export interface Manga {
  id: number;
  title: string;
  author: string | null;
  mangadex_id: string | null;
  cover_url: string | null;
  description: string | null;
  status: string | null;
  created_at: string;
}

export interface MangaDexManga {
  id: string;
  title: string;
  description: string | null;
  status: string | null;
  cover_url: string | null;
}

export interface MangaDexChapter {
  id: string;
  volume: string | null;
  chapter_number: string | null;
  title: string | null;
  translated_language: string | null;
}

export interface Page {
  id: number;
  chapter_id: string;
  page_number: number;
  image_url: string;
  quality: string;
  local_image_path: string | null;
  created_at: string;
}

export interface AudioStatus {
  chapter_id: string;
  status: 'unavailable' | 'ready';
  message: string;
}
