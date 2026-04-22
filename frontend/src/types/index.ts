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
  text_available: boolean;
  chapter_text_length: number;
}

export interface OcrPageResult {
  page_id: number;
  page_number: number;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'partial';
  engine_name: string;
  raw_text: string | null;
  cleaned_text: string | null;
  text_length: number;
  error_message: string | null;
}

export interface OcrChapterRunResponse {
  chapter_id: string;
  pages_processed: number;
  success_count: number;
  failure_count: number;
  completed_count: number;
}

export interface OcrChapterResult {
  chapter_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'partial';
  pages_total: number;
  completed_count: number;
  failed_count: number;
  processing_count: number;
  pending_count: number;
  chapter_text: string;
  chapter_text_length: number;
  page_results: OcrPageResult[];
}
