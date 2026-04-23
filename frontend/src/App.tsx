import React, { useEffect, useMemo, useState } from 'react';
import { Alert } from 'react-native';
import { Audio } from 'expo-av';

import FullscreenReader from './components/FullscreenReader';
import ChapterListScreen from './screens/ChapterListScreen';
import HomeScreen from './screens/HomeScreen';
import ReaderScreen from './screens/ReaderScreen';
import { api } from './services/api';
import { Manga, MangaDexChapter, MangaDexManga, OcrChapterResult, Page } from './types';
import { API_BASE_URL } from './config/api';

const OCR_DEPENDENCY_MESSAGE = 'OCR cannot run because Tesseract OCR is not installed/configured on the backend.';

function isDependencyErrorMessage(message: string): boolean {
  const normalized = message.toLowerCase();
  return normalized.includes('tesseract') && (normalized.includes('not installed') || normalized.includes('path'));
}

function getOcrDependencyNotice(ocrStatus: OcrChapterResult | null): string | null {
  if (!ocrStatus || ocrStatus.completed_count > 0 || ocrStatus.failed_count === 0) {
    return null;
  }

  const failedMessages = ocrStatus.page_results
    .filter((pageResult) => pageResult.status === 'failed' && typeof pageResult.error_message === 'string')
    .map((pageResult) => pageResult.error_message?.trim() || '')
    .filter(Boolean);

  if (failedMessages.length === 0) {
    return null;
  }

  const uniqueMessages = Array.from(new Set(failedMessages));
  if (uniqueMessages.length !== 1 || !isDependencyErrorMessage(uniqueMessages[0])) {
    return null;
  }

  return OCR_DEPENDENCY_MESSAGE;
}

const App: React.FC = () => {
  const [mangas, setMangas] = useState<Manga[]>([]);
  const [selectedManga, setSelectedManga] = useState<Manga | null>(null);
  const [chapters, setChapters] = useState<MangaDexChapter[]>([]);
  const [selectedChapter, setSelectedChapter] = useState<MangaDexChapter | null>(null);
  const [pages, setPages] = useState<Page[]>([]);
  const [currentPageIndex, setCurrentPageIndex] = useState<number>(0);
  const [fullscreenVisible, setFullscreenVisible] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<MangaDexManga[]>([]);
  const [loadingManga, setLoadingManga] = useState<boolean>(false);
  const [loadingSearch, setLoadingSearch] = useState<boolean>(false);
  const [loadingChapters, setLoadingChapters] = useState<boolean>(false);
  const [runningOcr, setRunningOcr] = useState<boolean>(false);
  const [ocrStatus, setOcrStatus] = useState<OcrChapterResult | null>(null);
  const [ocrNotice, setOcrNotice] = useState<string | null>(null);
  const [playingAudio, setPlayingAudio] = useState<boolean>(false);
  const [audioPlayer, setAudioPlayer] = useState<Audio.Sound | null>(null);

  const currentPage = useMemo(() => pages[currentPageIndex], [pages, currentPageIndex]);

  const loadLocalManga = async () => {
    try {
      setLoadingManga(true);
      const localManga = await api.listLocalManga();
      setMangas(localManga);
    } catch (error) {
      Alert.alert('Error', `Failed to load local manga: ${String(error)}`);
    } finally {
      setLoadingManga(false);
    }
  };

  useEffect(() => {
    loadLocalManga();
  }, []);

  useEffect(() => {
    const loadChapters = async () => {
      if (!selectedManga?.mangadex_id) {
        setChapters([]);
        return;
      }
      try {
        setLoadingChapters(true);
        const fetchedChapters = await api.getMangaDexChapters(selectedManga.mangadex_id);
        setChapters(fetchedChapters);
      } catch (error) {
        Alert.alert('Error', `Failed to load chapters: ${String(error)}`);
      } finally {
        setLoadingChapters(false);
      }
    };

    loadChapters();
  }, [selectedManga]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      return;
    }
    try {
      setLoadingSearch(true);
      const results = await api.searchMangaDex(searchQuery.trim());
      setSearchResults(results);
    } catch (error) {
      Alert.alert('Error', `Search failed: ${String(error)}`);
    } finally {
      setLoadingSearch(false);
    }
  };

  const handleImportManga = async (manga: MangaDexManga) => {
    try {
      await api.createLocalManga({
        title: manga.title,
        mangadex_id: manga.id,
        description: manga.description,
        status: manga.status,
        cover_url: manga.cover_url,
      });
      await loadLocalManga();
      Alert.alert('Imported', `${manga.title} was added to your local library.`);
    } catch (error) {
      Alert.alert('Import failed', String(error));
    }
  };

  const handleSelectChapter = async (chapter: MangaDexChapter) => {
    try {
      await api.storeChapter(chapter.id);
      const chapterPages = await api.getChapterPages(chapter.id);
      setSelectedChapter(chapter);
      setPages(chapterPages);
      setCurrentPageIndex(0);
      const initialOcrStatus = await api.getChapterOcr(chapter.id);
      setOcrStatus(initialOcrStatus);
      setOcrNotice(getOcrDependencyNotice(initialOcrStatus));
    } catch (error) {
      Alert.alert('Error', `Failed to open chapter: ${String(error)}`);
    }
  };

  const nextPage = async () => {
    await stopAudio();
    setCurrentPageIndex((prev) => Math.min(prev + 1, Math.max(0, pages.length - 1)));
  };

  const prevPage = async () => {
    await stopAudio();
    setCurrentPageIndex((prev) => Math.max(prev - 1, 0));
  };

  const stopAudio = async () => {
    if (audioPlayer) {
      try {
        await audioPlayer.stopAsync();
        await audioPlayer.unloadAsync();
      } catch (error) {
        console.error('Error stopping audio:', error);
      }
    }
    setAudioPlayer(null);
    setPlayingAudio(false);
  };

  const handleAudioPress = async () => {
    if (!selectedChapter) {
      return;
    }

    // If audio is already playing, stop it
    if (playingAudio && audioPlayer) {
      await stopAudio();
      return;
    }

    const currentPage = pages[currentPageIndex];
    if (!currentPage) {
      Alert.alert('No Page', 'Unable to load current page');
      return;
    }

    // Get current page OCR text (not entire chapter)
    const pageOcrText = currentPage.ocr_text?.trim();
    if (!pageOcrText) {
      Alert.alert('No Text', 'Current page has no OCR text. Please run OCR first.');
      return;
    }

    try {
      setPlayingAudio(true);

      // Generate audio for current page only
      Alert.alert('Generating Audio', 'Creating MP3 from current page text... this may take a moment.');
      try {
        const generated = await api.generateChapterAudio(selectedChapter.id, pageOcrText);
        Alert.alert('Audio Generated', `Ready to play current page. (Cached: ${generated.cached})`);
        // Get the audio URL
        if (!generated.audio_url) {
          setPlayingAudio(false);
          Alert.alert('Error', 'Generated audio URL is missing');
          return;
        }
        await playAudio(generated.audio_url);
      } catch (generateError) {
        const message = generateError instanceof Error ? generateError.message : String(generateError);
        if (message.includes('not installed') || message.includes('not available')) {
          Alert.alert('TTS Not Available', message);
        } else if (message.includes('OCR text')) {
          Alert.alert('No Text to Convert', message);
        } else {
          Alert.alert('Generation Failed', message);
        }
        setPlayingAudio(false);
        return;
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      Alert.alert('Playback Error', message);
      setPlayingAudio(false);
    }
  };

  const playAudio = async (audioUrl: string) => {
    try {
      // Stop any currently playing audio
      if (audioPlayer) {
        await audioPlayer.stopAsync();
        await audioPlayer.unloadAsync();
      }

      // Construct full URL if relative
      const fullUrl = audioUrl.startsWith('http') ? audioUrl : `${API_BASE_URL}${audioUrl}`;

      console.log('Loading audio from:', fullUrl);
      const sound = new Audio.Sound();
      
      // Set up callback for when playback finishes
      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.isLoaded && status.didJustFinish) {
          console.log('Audio playback finished');
          setPlayingAudio(false);
          setAudioPlayer(null);
          Alert.alert('Playback Complete', 'Audio finished playing');
        }
      });

      console.log('Loading audio file...');
      await sound.loadAsync({ uri: fullUrl });
      console.log('Audio loaded, starting playback...');
      await sound.playAsync();
      setAudioPlayer(sound);
      console.log('Playback started');
      Alert.alert('Playing Audio', 'Audio is now playing (you may hear silence if using fallback)');
    } catch (error) {
      setPlayingAudio(false);
      const message = error instanceof Error ? error.message : String(error);
      console.error('Audio playback error:', message);
      Alert.alert('Playback Error', `Failed to play audio: ${message}`);
    }
  };

  const handleRunChapterOcr = async () => {
    if (!selectedChapter) {
      return;
    }
    try {
      setRunningOcr(true);
      setOcrNotice(null);
      const runSummary = await api.runChapterOcr(selectedChapter.id);
      const latestStatus = await api.getChapterOcr(selectedChapter.id);
      setOcrStatus(latestStatus);
      setOcrNotice(getOcrDependencyNotice(latestStatus));
      Alert.alert(
        'OCR Complete',
        `Processed ${runSummary.pages_processed} pages. Success: ${runSummary.success_count}, Failed: ${runSummary.failure_count}.`
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      const dependencyNotice = isDependencyErrorMessage(message) || message === OCR_DEPENDENCY_MESSAGE
        ? OCR_DEPENDENCY_MESSAGE
        : null;
      setOcrNotice(dependencyNotice);
      Alert.alert('OCR', dependencyNotice ?? `Failed to run OCR: ${message}`);
    } finally {
      setRunningOcr(false);
    }
  };

  const ocrStatusText = selectedChapter
    ? ocrNotice
      ? `OCR: ${ocrNotice}`
      : ocrStatus
      ? `OCR: ${ocrStatus.completed_count}/${ocrStatus.pages_total} pages completed, text ${ocrStatus.chapter_text_length > 0 ? 'available' : 'not available yet'}.`
      : 'OCR: pending'
    : 'OCR: no chapter selected';

  if (!selectedManga) {
    return (
      <HomeScreen
        mangas={mangas}
        searchQuery={searchQuery}
        searchResults={searchResults}
        loadingManga={loadingManga}
        loadingSearch={loadingSearch}
        onSearchQueryChange={setSearchQuery}
        onSearch={handleSearch}
        onSelectLocalManga={setSelectedManga}
        onImportManga={handleImportManga}
      />
    );
  }

  if (selectedManga && !selectedChapter) {
    return (
      <ChapterListScreen
        selectedManga={selectedManga}
        chapters={chapters}
        loadingChapters={loadingChapters}
        onBack={() => setSelectedManga(null)}
        onSelectChapter={handleSelectChapter}
      />
    );
  }

  return (
    <>
      <ReaderScreen
        manga={selectedManga}
        chapter={selectedChapter as MangaDexChapter}
        pages={pages}
        pageIndex={currentPageIndex}
        ocrStatusText={ocrStatusText}
        ocrRunning={runningOcr}
        audioPlaying={playingAudio}
        onBack={async () => {
          await stopAudio();
          setSelectedChapter(null);
          setPages([]);
          setCurrentPageIndex(0);
          setOcrStatus(null);
          setOcrNotice(null);
        }}
        onRunChapterOcr={handleRunChapterOcr}
        onOpenFullscreen={() => setFullscreenVisible(true)}
        onNext={nextPage}
        onPrev={prevPage}
        onAudioPress={handleAudioPress}
      />

      {currentPage ? (
        <FullscreenReader
          visible={fullscreenVisible}
          imageUrl={currentPage.image_url}
          pageLabel={`Page ${currentPageIndex + 1} / ${pages.length}`}
          onClose={() => setFullscreenVisible(false)}
          onNext={nextPage}
          onPrev={prevPage}
          onAudioPress={handleAudioPress}
        />
      ) : null}
    </>
  );
};

export default App;
