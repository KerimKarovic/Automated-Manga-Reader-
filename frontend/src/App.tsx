import React, { useEffect, useMemo, useState } from 'react';
import { Alert } from 'react-native';

import FullscreenReader from './components/FullscreenReader';
import ChapterListScreen from './screens/ChapterListScreen';
import HomeScreen from './screens/HomeScreen';
import ReaderScreen from './screens/ReaderScreen';
import { api } from './services/api';
import { Manga, MangaDexChapter, MangaDexManga, Page } from './types';

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
    } catch (error) {
      Alert.alert('Error', `Failed to open chapter: ${String(error)}`);
    }
  };

  const nextPage = () => {
    setCurrentPageIndex((prev) => Math.min(prev + 1, Math.max(0, pages.length - 1)));
  };

  const prevPage = () => {
    setCurrentPageIndex((prev) => Math.max(prev - 1, 0));
  };

  const handleAudioPress = async () => {
    if (!selectedChapter) {
      return;
    }
    try {
      const response = await api.getAudioStatus(selectedChapter.id);
      Alert.alert('Audio', response.message);
    } catch (error) {
      Alert.alert('Audio', `Unable to check audio status: ${String(error)}`);
    }
  };

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
        onBack={() => {
          setSelectedChapter(null);
          setPages([]);
          setCurrentPageIndex(0);
        }}
        onOpenFullscreen={() => setFullscreenVisible(true)}
        onNext={nextPage}
        onPrev={prevPage}
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
