import axios from 'axios';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { router } from 'expo-router';

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

// Attach token to every request
api.interceptors.request.use(async (config) =>
{
  // Retrieve the token
  const token = await AsyncStorage.getItem('token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config
}, (error) =>
{
  return Promise.reject(error);
})

// Handle export token globally
api.interceptors.response.use((response) =>
{
  return response;
}, async (error) =>
{
  if (error.response && error.response.status === 401) {
    console.warn("Token expired or invalid. Logging out user.");

    // Wipe the invalid data from the device
    await AsyncStorage.removeItem("auth_token");
    await AsyncStorage.removeItem("user_data");

    // Imperatively redirect the user to the login screen
    router.replace('/(auth)/login');
  }

  return Promise.reject(error);
})

export default api;
