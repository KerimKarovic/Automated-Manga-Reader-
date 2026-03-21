import React from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

import { Manga, MangaDexManga } from '../types';

interface HomeScreenProps {
  mangas: Manga[];
  searchQuery: string;
  searchResults: MangaDexManga[];
  loadingManga: boolean;
  loadingSearch: boolean;
  onSearchQueryChange: (value: string) => void;
  onSearch: () => void;
  onSelectLocalManga: (manga: Manga) => void;
  onImportManga: (manga: MangaDexManga) => void;
}

const HomeScreen: React.FC<HomeScreenProps> = ({
  mangas,
  searchQuery,
  searchResults,
  loadingManga,
  loadingSearch,
  onSearchQueryChange,
  onSearch,
  onSelectLocalManga,
  onImportManga,
}) => {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Automated Manga Reader</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Search MangaDex</Text>
        <View style={styles.searchRow}>
          <TextInput
            placeholder="Search title..."
            value={searchQuery}
            onChangeText={onSearchQueryChange}
            style={styles.input}
          />
          <TouchableOpacity style={styles.searchButton} onPress={onSearch}>
            <Text style={styles.searchButtonText}>Search</Text>
          </TouchableOpacity>
        </View>
        {loadingSearch ? <ActivityIndicator size="small" color="#1f7a8c" /> : null}

        {searchResults.map((item) => (
          <View key={item.id} style={styles.card}>
            <Text style={styles.cardTitle}>{item.title}</Text>
            {item.status ? <Text style={styles.cardSub}>Status: {item.status}</Text> : null}
            <TouchableOpacity style={styles.importButton} onPress={() => onImportManga(item)}>
              <Text style={styles.importButtonText}>Import Locally</Text>
            </TouchableOpacity>
          </View>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Local Library</Text>
        {loadingManga ? <ActivityIndicator size="small" color="#1f7a8c" /> : null}
        {mangas.map((manga) => (
          <TouchableOpacity key={manga.id} style={styles.mangaButton} onPress={() => onSelectLocalManga(manga)}>
            <Text style={styles.mangaButtonText}>{manga.title}</Text>
            <Text style={styles.mangaMeta}>{manga.author || 'Unknown author'}</Text>
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
    gap: 18,
  },
  title: {
    marginTop: 40,
    fontSize: 28,
    fontWeight: '700',
    color: '#102a43',
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 14,
    gap: 10,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#243b53',
  },
  searchRow: {
    flexDirection: 'row',
    gap: 8,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#bcccdc',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: '#fff',
  },
  searchButton: {
    backgroundColor: '#1f7a8c',
    borderRadius: 10,
    paddingHorizontal: 14,
    justifyContent: 'center',
  },
  searchButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  card: {
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#d9e2ec',
    padding: 10,
    gap: 4,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#243b53',
  },
  cardSub: {
    color: '#486581',
  },
  importButton: {
    marginTop: 6,
    backgroundColor: '#334e68',
    alignSelf: 'flex-start',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  importButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  mangaButton: {
    borderRadius: 10,
    padding: 12,
    backgroundColor: '#d9f2f2',
  },
  mangaButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#102a43',
  },
  mangaMeta: {
    color: '#486581',
    marginTop: 2,
  },
});

export default HomeScreen;
