import { useEffect, useRef } from 'react';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import { API_URL } from '../constants/Api';

// How to show notifications when app is in foreground
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export function usePushNotifications() {
  const notificationListener = useRef<Notifications.EventSubscription>();
  const responseListener = useRef<Notifications.EventSubscription>();

  useEffect(() => {
    registerForPushNotifications();

    // Listener: notification received while app is open
    notificationListener.current = Notifications.addNotificationReceivedListener(notification => {
      console.log('Push received:', notification.request.content.title);
    });

    // Listener: user tapped on notification
    responseListener.current = Notifications.addNotificationResponseReceivedListener(response => {
      const data = response.notification.request.content.data as any;
      // Navigation based on screen data from server
      if (data?.screen) {
        console.log('Navigate to:', data.screen, 'id:', data.id);
        // You can add router.push() here if you import useRouter
      }
    });

    return () => {
      notificationListener.current?.remove();
      responseListener.current?.remove();
    };
  }, []);
}

export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) {
    console.log('Push notifications only work on real devices');
    return null;
  }

  // Request permission
  const { status: existing } = await Notifications.getPermissionsAsync();
  let finalStatus = existing;

  if (existing !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.log('Push notification permission denied');
    return null;
  }

  // Android channel setup
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('rgc-church', {
      name: 'RGC Nyahururu',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#8b0000',
      sound: 'default',
    });
  }

  // Get Expo push token
  try {
    const tokenData = await Notifications.getExpoPushTokenAsync({
      projectId: 'rgc-nyahururu',  // matches app.json slug
    });
    const token = tokenData.data;
    console.log('Expo push token:', token);

    // Register token with Django backend
    await registerTokenWithServer(token);
    return token;
  } catch (e) {
    console.log('Failed to get push token:', e);
    return null;
  }
}

async function registerTokenWithServer(token: string): Promise<void> {
  try {
    const accessToken = await SecureStore.getItemAsync('access_token');
    if (!accessToken) return; // Not logged in yet

    const platform = Platform.OS === 'ios' ? 'ios' : 'android';
    const resp = await fetch(`${API_URL}/notifications/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ token, platform }),
    });

    if (resp.ok) {
      console.log('Push token registered with server');
      await SecureStore.setItemAsync('push_token', token);
    }
  } catch (e) {
    console.log('Token registration failed:', e);
  }
}

export async function unregisterPushToken(): Promise<void> {
  try {
    const token = await SecureStore.getItemAsync('push_token');
    const accessToken = await SecureStore.getItemAsync('access_token');
    if (!token || !accessToken) return;

    await fetch(`${API_URL}/notifications/unregister/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ token }),
    });
    await SecureStore.deleteItemAsync('push_token');
  } catch (e) {
    console.log('Token unregister failed:', e);
  }
}
