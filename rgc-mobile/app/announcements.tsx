import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, RefreshControl } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { ENDPOINTS } from '../constants/Api';
import { Colors } from '../constants/Colors';
import { Card, Loader, Empty } from '../components/UI';

export default function AnnouncementsScreen() {
  const router = useRouter();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetch_ = async () => {
    try {
      const resp = await fetch(ENDPOINTS.ANNOUNCEMENTS);
      if (resp.ok) { const d = await resp.json(); setItems(d.results || d); }
    } catch (e) {} finally { setLoading(false); setRefreshing(false); }
  };

  useEffect(() => { fetch_(); }, []);

  if (loading) return <Loader message="Loading announcements..." />;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 10 }}>
          <Ionicons name="arrow-back" size={22} color="#fff" />
        </TouchableOpacity>
        <Ionicons name="megaphone" size={22} color={Colors.gold} />
        <Text style={styles.title}>Announcements</Text>
      </View>

      <FlatList
        data={items}
        keyExtractor={i => String(i.id)}
        contentContainerStyle={{ padding: 16, gap: 12, paddingBottom: 30 }}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetch_(); }} tintColor={Colors.gold} />}
        ListEmptyComponent={<Empty title="No announcements yet" subtitle="Check back soon for updates from RGC Nyahururu." />}
        renderItem={({ item }) => (
          <Card style={[styles.card, item.is_urgent && styles.urgent]}>
            {item.is_urgent && (
              <View style={styles.urgentTag}>
                <Ionicons name="warning" size={12} color="#1a1a1a" />
                <Text style={styles.urgentTagText}>URGENT</Text>
              </View>
            )}
            <Text style={styles.annTitle}>{item.title}</Text>
            <Text style={styles.annBody}>{item.content}</Text>
            <View style={styles.annMeta}>
              <Ionicons name="person-outline" size={12} color={Colors.textMuted} />
              <Text style={styles.metaText}>{item.posted_by_name}</Text>
              <Ionicons name="time-outline" size={12} color={Colors.textMuted} />
              <Text style={styles.metaText}>{new Date(item.date_posted).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' })}</Text>
            </View>
          </Card>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  header: { backgroundColor: Colors.black, paddingTop: 56, paddingBottom: 18, paddingHorizontal: 20, flexDirection: 'row', alignItems: 'center', gap: 10 },
  title: { fontSize: 20, fontWeight: '700', color: Colors.gold, flex: 1 },
  card: {},
  urgent: { borderLeftWidth: 4, borderLeftColor: Colors.gold, backgroundColor: '#fffbea' },
  urgentTag: { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: Colors.gold, borderRadius: 20, paddingHorizontal: 10, paddingVertical: 4, alignSelf: 'flex-start', marginBottom: 8 },
  urgentTagText: { fontSize: 10, fontWeight: '700', color: '#1a1a1a' },
  annTitle: { fontSize: 16, fontWeight: '700', color: Colors.textPrimary, marginBottom: 8 },
  annBody: { fontSize: 14, color: Colors.textSecondary, lineHeight: 21, marginBottom: 12 },
  annMeta: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  metaText: { fontSize: 12, color: Colors.textMuted, marginRight: 8 },
});
