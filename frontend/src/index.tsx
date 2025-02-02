// frontend/src/index.tsx
import { registerRootComponent } from 'expo';
import App from './App';

// registerRootComponent ensures that whether your app is running in Expo Go or as a native build,
// the environment is set up properly.
registerRootComponent(App);
