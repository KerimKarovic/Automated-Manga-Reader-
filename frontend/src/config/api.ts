import Constants from 'expo-constants';
import { Platform } from 'react-native';

const EXPLICIT_API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL?.trim();

function resolveDefaultApiBaseUrl(): string {
  // Web runs in the same machine browser, so localhost is the safest default.
  if (Platform.OS === 'web') {
    return 'http://127.0.0.1:8000';
  }

  // In Expo Go, derive the dev machine host from Metro metadata.
  const hostUri =
    (Constants as any)?.expoConfig?.hostUri ??
    (Constants as any)?.manifest2?.extra?.expoClient?.hostUri ??
    (Constants as any)?.manifest?.debuggerHost;

  if (typeof hostUri === 'string' && hostUri.length > 0) {
    const host = hostUri.split(':')[0];
    if (host) {
      return `http://${host}:8000`;
    }
  }

  // Fallback for simulators / local development.
  return 'http://127.0.0.1:8000';
}

export const API_BASE_URL = EXPLICIT_API_BASE_URL || resolveDefaultApiBaseUrl();
