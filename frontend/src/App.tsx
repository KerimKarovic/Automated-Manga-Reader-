import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Image, ScrollView } from 'react-native';

interface Manga {
  id: string;
  title: string;
  author: string;
}

interface Chapter {
  id: string;
  chapter: string;
  volume?: string | null;
}

const App: React.FC = () => {
  const [mangas, setMangas] = useState<Manga[]>([]);
  const [selectedManga, setSelectedManga] = useState<Manga | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [selectedChapter, setSelectedChapter] = useState<Chapter | null>(null);
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [currentPageIndex, setCurrentPageIndex] = useState<number>(0);

  // Fetch available mangas from your backend
  useEffect(() => {
    fetch('http://127.0.0.1:8000/manga')
      .then((res) => res.json())
      .then((data) => setMangas(data))
      .catch((err) => console.error("Error fetching mangas:", err));
  }, []);

  // Fetch chapters for the selected manga
  useEffect(() => {
    if (selectedManga) {
      fetch(`http://127.0.0.1:8000/mangadex/${selectedManga.id}/chapters?language=en`)
        .then((res) => res.json())
        .then((data) => setChapters(data.chapters))
        .catch((err) => console.error("Error fetching chapters:", err));
    }
  }, [selectedManga]);

  // Fetch chapter images when a chapter is selected
  useEffect(() => {
    if (selectedChapter) {
      fetch(`http://127.0.0.1:8000/mangadex/chapter/${selectedChapter.id}/images?quality=data`)
        .then((res) => res.json())
        .then((data) => {
          setImageUrls(data.image_urls);
          setCurrentPageIndex(0);
        })
        .catch((err) => console.error("Error fetching chapter images:", err));
    }
  }, [selectedChapter]);

  const nextPage = () => {
    setCurrentPageIndex((prev) => Math.min(prev + 1, imageUrls.length - 1));
  };

  const prevPage = () => {
    setCurrentPageIndex((prev) => Math.max(prev - 1, 0));
  };

  if (!selectedManga) {
    return (
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Manga Reader</Text>
        <Text style={styles.subtitle}>Select a Manga</Text>
        {mangas.map((manga) => (
          <TouchableOpacity
            key={manga.id}
            style={styles.button}
            onPress={() => setSelectedManga(manga)}
          >
            <Text style={styles.buttonText}>
              {manga.title} by {manga.author}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    );
  }

  if (selectedManga && !selectedChapter) {
    return (
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>{selectedManga.title} - Chapters</Text>
        <TouchableOpacity style={styles.backButton} onPress={() => setSelectedManga(null)}>
          <Text style={styles.backButtonText}>Back to Manga List</Text>
        </TouchableOpacity>
        {chapters.map((chapter) => (
          <TouchableOpacity
            key={chapter.id}
            style={styles.button}
            onPress={() => setSelectedChapter(chapter)}
          >
            <Text style={styles.buttonText}>
              Chapter {chapter.chapter} {chapter.volume ? `(Volume ${chapter.volume})` : ''}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    );
  }

  // When a chapter is selected, display its images with navigation.
  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        {selectedManga?.title} - Chapter {selectedChapter?.chapter}
      </Text>
      <TouchableOpacity style={styles.backButton} onPress={() => setSelectedChapter(null)}>
        <Text style={styles.backButtonText}>Back to Chapters</Text>
      </TouchableOpacity>
      {imageUrls.length > 0 ? (
        <View style={styles.imageContainer}>
          <TouchableOpacity style={styles.navArea} onPress={prevPage} />
          <Image
            source={{ uri: imageUrls[currentPageIndex] }}
            style={styles.image}
            resizeMode="contain"
          />
          <TouchableOpacity style={styles.navArea} onPress={nextPage} />
        </View>
      ) : (
        <Text>Loading chapter images...</Text>
      )}
      <Text>
        Page {currentPageIndex + 1} of {imageUrls.length}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center'
  },
  title: {
    fontSize: 24,
    marginBottom: 20,
    color: '#333'
  },
  subtitle: {
    fontSize: 18,
    marginBottom: 10,
    color: '#555'
  },
  button: {
    backgroundColor: '#007bff',
    padding: 10,
    marginVertical: 5,
    borderRadius: 4,
    width: '100%',
    alignItems: 'center'
  },
  buttonText: {
    color: 'white',
    fontSize: 16
  },
  backButton: {
    marginBottom: 20,
    padding: 10,
    backgroundColor: '#ccc',
    borderRadius: 4
  },
  backButtonText: {
    fontSize: 16,
    color: '#333'
  },
  imageContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 20
  },
  navArea: {
    flex: 1
  },
  image: {
    width: '80%',
    height: 300,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 4
  }
});

export default App;
