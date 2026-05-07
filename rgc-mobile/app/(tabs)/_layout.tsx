import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../../constants/Colors';
import { useAuth } from '../../context/AuthContext';
import { View, Text, StyleSheet } from 'react-native';

function TabIcon({ name, color, focused }: { name: any; color: string; focused: boolean }) {
  return <Ionicons name={focused ? name : `${name}-outline` as any} size={24} color={color} />;
}

export default function TabLayout() {
  const { isManager } = useAuth();

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: Colors.black,
          borderTopColor: '#333',
          borderTopWidth: 1,
          height: 62,
          paddingBottom: 8,
        },
        tabBarActiveTintColor: Colors.gold,
        tabBarInactiveTintColor: '#666',
        tabBarLabelStyle: { fontSize: 10, fontWeight: '600' },
      }}
    >
      <Tabs.Screen name="home" options={{ title: 'Home', tabBarIcon: ({ color, focused }) => <TabIcon name="home" color={color} focused={focused} /> }} />
      <Tabs.Screen name="bible" options={{ title: 'Bible', tabBarIcon: ({ color, focused }) => <TabIcon name="book" color={color} focused={focused} /> }} />
      <Tabs.Screen name="hymns" options={{ title: 'Hymns', tabBarIcon: ({ color, focused }) => <TabIcon name="musical-notes" color={color} focused={focused} /> }} />
      <Tabs.Screen name="events" options={{ title: 'Events', tabBarIcon: ({ color, focused }) => <TabIcon name="calendar" color={color} focused={focused} /> }} />
      <Tabs.Screen name="give" options={{ title: 'Give', tabBarIcon: ({ color, focused }) => <TabIcon name="heart" color={color} focused={focused} /> }} />
      <Tabs.Screen name="more" options={{ title: 'More', tabBarIcon: ({ color, focused }) => <TabIcon name="grid" color={color} focused={focused} /> }} />
    </Tabs>
  );
}
