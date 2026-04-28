import axios from 'axios';
import { Platform } from 'react-native';

// Dynamically resolve the backend URL
let API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

if (!API_URL) {
  if (Platform.OS === 'web') {
    // On Vercel Web, relative paths automatically hit the same domain!
    API_URL = '';
  } else {
    // On React Native Mobile, we must use an absolute URL
    API_URL = "http://127.0.0.1:8000";
  }
}

// Create the centralized Axios instance
export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
