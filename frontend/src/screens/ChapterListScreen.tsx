import React from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

import { Manga, MangaDexChapter } from '../types';

interface ChapterListScreenProps {
  selectedManga: Manga;
  chapters: MangaDexChapter[];
  loadingChapters: boolean;
  onBack: () => void;
  onSelectChapter: (chapter: MangaDexChapter) => void;
}

const ChapterListScreen: React.FC<ChapterListScreenProps> = ({
  selectedManga,
  chapters,
  loadingChapters,
  onBack,
  onSelectChapter,
}) => {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TouchableOpacity style={styles.backButton} onPress={onBack}>
        <Text style={styles.backText}>Back to Library</Text>
      </TouchableOpacity>

      <Text style={styles.title}>{selectedManga.title}</Text>
      <Text style={styles.subtitle}>Chapters</Text>

      {loadingChapters ? <ActivityIndicator size="small" color="#1f7a8c" /> : null}

      <View style={styles.list}>
        {chapters.map((chapter) => (
          <TouchableOpacity key={chapter.id} style={styles.chapterButton} onPress={() => onSelectChapter(chapter)}>
            <Text style={styles.chapterText}>
              Chapter {chapter.chapter_number || '?'} {chapter.volume ? `(Vol ${chapter.volume})` : ''}
            </Text>
            {chapter.title ? <Text style={styles.chapterSub}>{chapter.title}</Text> : null}
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    backgroundColor: '#f3f6f4',
    gap: 10,
  },
  backButton: {
    marginTop: 40,
    backgroundColor: '#334e68',
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 14,
    alignSelf: 'flex-start',
  },
  backText: {
    color: '#fff',
    fontWeight: '600',
  },
  title: {
    fontSize: 26,
    fontWeight: '700',
    color: '#102a43',
  },
  subtitle: {
    fontSize: 18,
    color: '#486581',
  },
  list: {
    gap: 10,
  },
  chapterButton: {
    padding: 12,
    borderRadius: 10,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#d9e2ec',
  },
  chapterText: {
    color: '#102a43',
    fontWeight: '600',
    fontSize: 16,
  },
  chapterSub: {
    color: '#486581',
    marginTop: 4,
  },
});

export default ChapterListScreen;
