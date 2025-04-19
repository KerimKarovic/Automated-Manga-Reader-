import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Image,
  ScrollView,
  Button,
  Modal,
  Dimensions,
  PanResponder
} from 'react-native';

interface Manga {
  id: number | string;
  title: string;
  author: string;
  mangadexId?: string;
}

interface Chapter {
  id: string;
  chapter: string;
  volume?: string | null;
}

const backendUrl = "http://192.168.2.122:8000";

const App: React.FC = () => {
  const [mangas, setMangas] = useState<Manga[]>([]);
  const [selectedManga, setSelectedManga] = useState<Manga | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [selectedChapter, setSelectedChapter] = useState<Chapter | null>(null);
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [currentPageIndex, setCurrentPageIndex] = useState<number>(0);
  const [fullscreenVisible, setFullscreenVisible] = useState<boolean>(false);
  const [audioSource, setAudioSource] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${backendUrl}/manga`)
      .then((res) => res.json())
      .then((data) => setMangas(data))
      .catch((err) => console.error("Error fetching mangas:", err));
  }, []);

  useEffect(() => {
    if (selectedManga) {
      let externalId: string | number;

      if (selectedManga.title === "Dandadan") {
        externalId = "68112dc1-2b80-4f20-beb8-2f2a8716a430";
      } else {
        externalId = selectedManga.mangadexId || selectedManga.id;
      }

      fetch(`${backendUrl}/mangadex/${externalId}/chapters?language=en`)
        .then((res) => res.json())
        .then((data) => setChapters(data.chapters || []))
        .catch((err) => {
          console.error("Error fetching chapters:", err);
          setChapters([]);
        });
    }
  }, [selectedManga]);

  useEffect(() => {
    if (selectedChapter) {
      fetch(`${backendUrl}/mangadex/chapter/${selectedChapter.id}/images?quality=data`)
        .then((res) => res.json())
        .then((data) => {
          setImageUrls(data.image_urls || []);
          setCurrentPageIndex(0);
        })
        .catch((err) => {
          console.error("Error fetching chapter images:", err);
          setImageUrls([]);
        });
    }
  }, [selectedChapter]);

  useEffect(() => {
    Audio.setAudioModeAsync({
      playsInSilentModeIOS: true,
      staysActiveInBackground: false,
    });
  }, []);
  

  const testWavAudio = async () => {
    console.log("🔊 Starting WAV audio test...");
  
    const remoteUri = 'https://file-examples.com/storage/fe0ff623e9b3dbb92bfa60d/2017/11/file_example_WAV_1MG.wav';
    const localUri = FileSystem.cacheDirectory + 'test.wav';
  
    try {
      const download = await FileSystem.downloadAsync(remoteUri, localUri);
      console.log("✅ File downloaded to:", download.uri);
  
      const { sound } = await Audio.Sound.createAsync({ uri: download.uri });
      console.log("🔊 Playing downloaded WAV...");
      await sound.playAsync();
    } catch (error) {
      console.error("❌ Failed to play WAV:", error);
    }
  };
  


  const handleReadPress = async () => {
    if (!selectedChapter) return;
  
    try {
      const uri = `${backendUrl}/tts/${selectedChapter.id}`;
      const localUri = `${FileSystem.cacheDirectory}tts_${selectedChapter.id}.wav`;
  
      // ✅ this is where we download the audio file from backend
      const downloadRes = await FileSystem.downloadAsync(uri, localUri);
  
      // ✅ now we can safely use it for debugging
      console.log("Downloading from:", uri);
      console.log("Saved to:", downloadRes.uri);
  
      setAudioSource(downloadRes.uri);
    } catch (error) {
      console.error("Error fetching TTS audio:", error);
    }
  };
  
  

  useEffect(() => {
    let sound: Audio.Sound;

    const loadAndPlayAudio = async () => {
      if (audioSource) {
        try {
          sound = new Audio.Sound();
          await sound.loadAsync({ uri: audioSource });
          await sound.playAsync();
        } catch (err) {
          console.error("Failed to load/play audio", err);
        }
      }
    };

    loadAndPlayAudio();

    return () => {
      if (sound) {
        sound.unloadAsync();
      }
    };
  }, [audioSource]);

  const nextPage = () => {
    setCurrentPageIndex((prev) => Math.min(prev + 1, imageUrls.length - 1));
  };

  const prevPage = () => {
    setCurrentPageIndex((prev) => Math.max(prev - 1, 0));
  };

  const panResponder = useRef(
    PanResponder.create({
      onMoveShouldSetPanResponder: (_, gesture) => Math.abs(gesture.dy) > 10,
      onPanResponderRelease: (_, gesture) => {
        if (gesture.dy > 30) setFullscreenVisible(false);
      },
    })
  ).current;

  const handlePagePress = (event: any) => {
    const { locationX } = event.nativeEvent;
    if (locationX < Dimensions.get('window').width / 2) {
      prevPage();
    } else {
      nextPage();
    }
  };

  if (!selectedManga) {
    return (
      <View style={[styles.container, { backgroundColor: '#C7E6E7' }]}>        
        <View style={styles.blob1} />
        <View style={styles.blob2} />
        <View style={styles.blob3} />
        <ScrollView contentContainerStyle={styles.overlayContent}>
          <Text style={styles.title}>Manga Reader</Text>
          {mangas.length === 0 ? (
            <Text>Loading mangas...</Text>
          ) : (
            <View style={styles.listContainer}>
              {mangas.map((manga) => (
                <TouchableOpacity key={manga.id} style={styles.mangaButton} onPress={() => setSelectedManga(manga)}>
                  <Text style={styles.mangaButtonText}>{manga.title} by {manga.author}</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
          
        </ScrollView>
      </View>
    );
  }

  if (selectedManga && !selectedChapter) {
    return (
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>{selectedManga.title} - Chapters</Text>
        <View style={{ padding: 20 }}>
  <Button title="🔊 Test WAV Audio" onPress={() => {
    console.log("WAV Test Pressed");
    testWavAudio();
  }} />
</View>

        <TouchableOpacity style={styles.backButton} onPress={() => setSelectedManga(null)}>
          <Text style={styles.backButtonText}>Back to Manga List</Text>
        </TouchableOpacity>
        {chapters.length === 0 ? (
          <Text>Loading chapters...</Text>
        ) : (
          <View style={styles.listContainer}>
            {chapters.map((chapter) => (
              <TouchableOpacity key={chapter.id} style={styles.mangaButton} onPress={() => setSelectedChapter(chapter)}>
                <Text style={styles.mangaButtonText}>Chapter {chapter.chapter} {chapter.volume ? `(Vol ${chapter.volume})` : ''}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </ScrollView>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{selectedManga?.title} - Chapter {selectedChapter?.chapter}</Text>
      <TouchableOpacity style={styles.backButton} onPress={() => setSelectedChapter(null)}>
        <Text style={styles.backButtonText}>Back to Chapters</Text>
      </TouchableOpacity>
      


      {imageUrls.length > 0 ? (
        <TouchableOpacity onPress={() => setFullscreenVisible(true)}>
          <Image source={{ uri: imageUrls[currentPageIndex] }} style={styles.image} resizeMode="contain" />
        </TouchableOpacity>
      ) : (
        <Text>Loading chapter images...</Text>
      )}

      <Text>Page {currentPageIndex + 1} of {imageUrls.length}</Text>

      <Modal visible={fullscreenVisible} transparent={false} animationType="fade">
        <View style={styles.fullscreenContainer} {...panResponder.panHandlers}>
          <TouchableOpacity style={styles.fullscreenOverlay} onPress={handlePagePress}>
            <Image source={{ uri: imageUrls[currentPageIndex] }} style={styles.fullscreenImage} resizeMode="contain" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.readButton} onPress={handleReadPress}>
            <Text style={styles.readButtonText}>Read</Text>
          </TouchableOpacity>
        </View>
      </Modal>
    </View>
  );
};

const { width, height } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  overlayContent: {
    width: '100%',
    alignItems: 'center',
    paddingTop: 100,
    zIndex: 1
  },
  title: {
    fontSize: 24,
    marginBottom: 20
  },
  listContainer: {
    width: '100%',
    alignItems: 'center'
  },
  mangaButton: {
    backgroundColor: '#E6F4E1',
    padding: 12,
    marginVertical: 6,
    borderRadius: 20,
    width: '100%',
    alignItems: 'center'
  },
  mangaButtonText: {
    fontSize: 16,
    color: '#000'
  },
  backButton: {
    marginBottom: 20,
    padding: 10,
    backgroundColor: '#ccc',
    borderRadius: 4
  },
  backButtonText: {
    fontSize: 16
  },
  readButton: {
    marginTop: 20,
    padding: 12,
    backgroundColor: '#6CB4EE',
    borderRadius: 12,
    alignSelf: 'center'
  },
  readButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  image: {
    width: width * 0.8,
    height: height * 0.6,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 4,
    marginBottom: 10
  },
  fullscreenContainer: {
    flex: 1,
    backgroundColor: 'black',
    justifyContent: 'center',
    alignItems: 'center'
  },
  fullscreenImage: {
    width: '100%',
    height: '100%'
  },
  fullscreenOverlay: {
    flex: 1,
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center'
  },
  blob1: {
    position: 'absolute',
    top: -50,
    left: -50,
    width: 200,
    height: 200,
    borderRadius: 100,
    backgroundColor: '#BACDE9',
    opacity: 0.3
  },
  blob2: {
    position: 'absolute',
    top: 100,
    right: -40,
    width: 180,
    height: 180,
    borderRadius: 90,
    backgroundColor: '#E9C2BA',
    opacity: 0.3
  },
  blob3: {
    position: 'absolute',
    bottom: -60,
    left: 50,
    width: 220,
    height: 220,
    borderRadius: 110,
    backgroundColor: '#E9BACB',
    opacity: 0.3
  }
});

export default App;
