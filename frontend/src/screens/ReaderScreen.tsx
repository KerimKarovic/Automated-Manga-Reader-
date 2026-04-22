import React from 'react';
import { Image, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

import { Manga, MangaDexChapter, Page } from '../types';

interface ReaderScreenProps {
  manga: Manga;
  chapter: MangaDexChapter;
  pages: Page[];
  pageIndex: number;
  ocrStatusText: string;
  ocrRunning: boolean;
  onBack: () => void;
  onRunChapterOcr: () => void;
  onOpenFullscreen: () => void;
  onNext: () => void;
  onPrev: () => void;
}

const ReaderScreen: React.FC<ReaderScreenProps> = ({
  manga,
  chapter,
  pages,
  pageIndex,
  ocrStatusText,
  ocrRunning,
  onBack,
  onRunChapterOcr,
  onOpenFullscreen,
  onNext,
  onPrev,
}) => {
  const currentPage = pages[pageIndex];

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.backButton} onPress={onBack}>
        <Text style={styles.backText}>Back to Chapters</Text>
      </TouchableOpacity>

      <Text style={styles.title}>{manga.title}</Text>
      <Text style={styles.subtitle}>Chapter {chapter.chapter_number || '?'}</Text>

      {currentPage ? (
        <TouchableOpacity style={styles.imageWrap} onPress={onOpenFullscreen}>
          <Image source={{ uri: currentPage.image_url }} style={styles.image} resizeMode="contain" />
        </TouchableOpacity>
      ) : (
        <Text style={styles.loading}>Loading pages...</Text>
      )}

      <Text style={styles.pageLabel}>
        Page {pages.length ? pageIndex + 1 : 0} / {pages.length}
      </Text>

      <View style={styles.ocrRow}>
        <TouchableOpacity style={styles.ocrButton} onPress={onRunChapterOcr} disabled={ocrRunning}>
          <Text style={styles.ocrButtonText}>{ocrRunning ? 'Running OCR...' : 'Run Chapter OCR'}</Text>
        </TouchableOpacity>
        <Text style={styles.ocrStatus}>{ocrStatusText}</Text>
      </View>

      <View style={styles.controls}>
        <TouchableOpacity style={styles.controlButton} onPress={onPrev}>
          <Text style={styles.controlText}>Prev</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.controlButton} onPress={onNext}>
          <Text style={styles.controlText}>Next</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f6f4',
    padding: 20,
    paddingTop: 50,
    alignItems: 'center',
  },
  backButton: {
    alignSelf: 'flex-start',
    backgroundColor: '#334e68',
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 14,
  },
  backText: {
    color: '#fff',
    fontWeight: '600',
  },
  title: {
    marginTop: 12,
    fontSize: 24,
    fontWeight: '700',
    color: '#102a43',
    textAlign: 'center',
  },
  subtitle: {
    marginTop: 6,
    marginBottom: 10,
    fontSize: 16,
    color: '#486581',
  },
  imageWrap: {
    width: '100%',
    flex: 1,
    borderRadius: 10,
    overflow: 'hidden',
    backgroundColor: '#fff',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  loading: {
    marginTop: 20,
    color: '#486581',
  },
  pageLabel: {
    marginTop: 10,
    color: '#243b53',
  },
  ocrRow: {
    marginTop: 10,
    width: '100%',
    alignItems: 'center',
    gap: 6,
  },
  ocrButton: {
    backgroundColor: '#0f766e',
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 14,
  },
  ocrButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  ocrStatus: {
    color: '#334e68',
    fontSize: 13,
    textAlign: 'center',
  },
  controls: {
    marginTop: 12,
    flexDirection: 'row',
    gap: 10,
  },
  controlButton: {
    backgroundColor: '#1f7a8c',
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 14,
  },
  controlText: {
    color: '#fff',
    fontWeight: '600',
  },
});

export default ReaderScreen;
