import React, { useRef } from 'react';
import { Dimensions, Image, Modal, PanResponder, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

interface FullscreenReaderProps {
  visible: boolean;
  imageUrl: string;
  pageLabel: string;
  onClose: () => void;
  onNext: () => void;
  onPrev: () => void;
  onAudioPress: () => void;
}

const FullscreenReader: React.FC<FullscreenReaderProps> = ({
  visible,
  imageUrl,
  pageLabel,
  onClose,
  onNext,
  onPrev,
  onAudioPress,
}) => {
  const panResponder = useRef(
    PanResponder.create({
      onMoveShouldSetPanResponder: (_, gestureState) => Math.abs(gestureState.dy) > 14,
      onPanResponderRelease: (_, gestureState) => {
        if (gestureState.dy > 40) {
          onClose();
        }
      },
    })
  ).current;

  return (
    <Modal visible={visible} transparent={false} animationType="fade">
      <View style={styles.container} {...panResponder.panHandlers}>
        <TouchableOpacity
          style={styles.imageTouch}
          onPress={(event) => {
            const tapX = event.nativeEvent.locationX;
            if (tapX < Dimensions.get('window').width / 2) {
              onPrev();
            } else {
              onNext();
            }
          }}
        >
          <Image source={{ uri: imageUrl }} style={styles.image} resizeMode="contain" />
        </TouchableOpacity>

        <View style={styles.footer}>
          <Text style={styles.pageLabel}>{pageLabel}</Text>
          <TouchableOpacity style={styles.audioButton} onPress={onAudioPress}>
            <Text style={styles.audioButtonText}>Audio</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Text style={styles.closeText}>Close</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
  },
  imageTouch: {
    flex: 1,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  footer: {
    position: 'absolute',
    bottom: 20,
    left: 0,
    right: 0,
    alignItems: 'center',
    gap: 10,
  },
  pageLabel: {
    color: '#fff',
    fontSize: 14,
  },
  audioButton: {
    paddingHorizontal: 18,
    paddingVertical: 10,
    borderRadius: 10,
    backgroundColor: '#1f7a8c',
  },
  audioButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  closeButton: {
    paddingHorizontal: 18,
    paddingVertical: 10,
    borderRadius: 10,
    backgroundColor: '#374151',
  },
  closeText: {
    color: '#fff',
    fontSize: 14,
  },
});

export default FullscreenReader;
