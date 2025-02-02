// frontend/src/index.tsx
import { registerRootComponent } from 'expo';
import App from './App';

// registerRootComponent registers the main component of your app.
// This ensures that your app environment is properly set up whether you're in Expo Go or a native build.
registerRootComponent(App);
