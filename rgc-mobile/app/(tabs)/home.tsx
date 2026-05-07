import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, ScrollView, StyleSheet, RefreshControl,
  TouchableOpacity, FlatList,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { Colors } from '../../constants/Colors';
import { ENDPOINTS } from '../../constants/Api';
import { Card, SectionHeader, Badge, Loader, Empty } from '../../components/UI';

export default function HomeScreen() {
  const { user, isManager } = useAuth();
  const router = useRouter();
  const [announcements, setAnnouncements] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [annResp, evtResp] = await Promise.all([
        fetch(ENDPOINTS.ANNOUNCEMENTS),
        fetch(ENDPOINTS.EVENTS),
      ]);
      if (annResp.ok) {
        const d = await annResp.json();
        setAnnouncements((d.results || d).slice(0, 5));
      }
      if (evtResp.ok) {
        const d = await evtResp.json();
        setEvents((d.results || d).slice(0, 4));
      }
    } catch (e) { /* network error */ }
    finally { setLoading(false); setRefreshing(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const onRefresh = () => { setRefreshing(true); fetchData(); };

  if (loading) return <Loader message="Loading..." />;

  const urgent = announcements.filter(a => a.is_urgent);
  const normal = announcements.filter(a => !a.is_urgent);

  return (
    <ScrollView
      style={styles.container}
      showsVerticalScrollIndicator={false}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.gold} />}
    >
      {/* Hero */}
      <View style={styles.hero}>
        <Text style={styles.heroGreeting}>Welcome,</Text>
        <Text style={styles.heroName}>{user?.first_name || user?.username}!</Text>
        <Text style={styles.herySub}>Redeemed Gospel Church Nyahururu</Text>
        <Text style={styles.heroTagline}>"Where everybody is somebody"</Text>

        {/* Quick actions */}
        <View style={styles.quickGrid}>
          {[
            { icon: 'book', label: 'Bible', route: '/(tabs)/bible' },
            { icon: 'musical-notes', label: 'Hymns', route: '/(tabs)/hymns' },
            { icon: 'heart', label: 'Give', route: '/(tabs)/give' },
            { icon: 'people', label: 'Groups', route: '/groups' },
          ].map(q => (
            <TouchableOpacity key={q.label} style={styles.quickBtn} onPress={() => router.push(q.route as any)} activeOpacity={0.8}>
              <View style={styles.quickIcon}>
                <Ionicons name={q.icon as any} size={22} color={Colors.gold} />
              </View>
              <Text style={styles.quickLabel}>{q.label}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Admin shortcut */}
        {isManager && (
          <TouchableOpacity style={styles.adminBanner} onPress={() => router.push('/admin')}>
            <Ionicons name="shield" size={18} color={Colors.gold} />
            <Text style={styles.adminBannerText}>Open Admin Dashboard</Text>
            <Ionicons name="chevron-forward" size={18} color={Colors.gold} />
          </TouchableOpacity>
        )}
      </View>

      <View style={styles.body}>
        {/* Urgent announcements */}
        {urgent.length > 0 && (
          <View style={styles.urgentBanner}>
            <Ionicons name="megaphone" size={16} color={Colors.gold} />
            <Text style={styles.urgentText} numberOfLines={2}>{urgent[0].title}</Text>
            <TouchableOpacity onPress={() => router.push('/announcements' as any)}>
              <Text style={styles.urgentMore}>More →</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Announcements */}
        <SectionHeader
          title="Announcements"
          action={{ label: 'See All', onPress: () => router.push('/announcements' as any) }}
          style={{ marginHorizontal: 16 }}
        />
        {normal.length === 0 ? (
          <Empty title="No announcements yet" style={{ paddingVertical: 20 }} />
        ) : (
          normal.map(ann => (
            <Card key={ann.id} style={styles.annCard}>
              <Text style={styles.annTitle} numberOfLines={1}>{ann.title}</Text>
              <Text style={styles.annContent} numberOfLines={3}>{ann.content}</Text>
              <Text style={styles.annDate}><Ionicons name="time-outline" size={11} /> {new Date(ann.date_posted).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' })}</Text>
            </Card>
          ))
        )}

        {/* Events */}
        <SectionHeader
          title="Upcoming Events"
          action={{ label: 'See All', onPress: () => router.push('/(tabs)/events') }}
          style={{ marginHorizontal: 16, marginTop: 8 }}
        />
        {events.length === 0 ? (
          <Empty title="No upcoming events" style={{ paddingVertical: 20 }} />
        ) : (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ paddingHorizontal: 16, gap: 12, paddingBottom: 8 }}>
            {events.map(ev => (
              <Card key={ev.id} style={styles.evtCard}>
                <View style={styles.evtDateBadge}>
                  <Text style={styles.evtDay}>{new Date(ev.date).getDate()}</Text>
                  <Text style={styles.evtMonth}>{new Date(ev.date).toLocaleString('en', { month: 'short' }).toUpperCase()}</Text>
                </View>
                <Text style={styles.evtTitle} numberOfLines={2}>{ev.title}</Text>
                <View style={styles.evtMeta}>
                  <Ionicons name="time-outline" size={12} color={Colors.textMuted} />
                  <Text style={styles.evtMetaText}>{ev.time?.slice(0, 5)}</Text>
                </View>
                <View style={styles.evtMeta}>
                  <Ionicons name="location-outline" size={12} color={Colors.textMuted} />
                  <Text style={styles.evtMetaText} numberOfLines={1}>{ev.location}</Text>
                </View>
                <Badge label={ev.category_display} color={Colors.red} size="sm" />
              </Card>
            ))}
          </ScrollView>
        )}

        {/* Service times */}
        <View style={styles.serviceCard}>
          <Text style={styles.serviceTitle}>Service Times</Text>
          {[
            ['Sunday Service', '9:00 AM'],
            ['Sunday School', '8:00 AM'],
            ['Wed Bible Study', '6:00 PM'],
            ['Fri Prayer Meeting', '6:00 PM'],
          ].map(([day, time]) => (
            <View key={day} style={styles.serviceRow}>
              <Text style={styles.serviceDay}>{day}</Text>
              <Text style={styles.serviceTime}>{time}</Text>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  hero: { backgroundColor: Colors.black, paddingTop: 60, paddingBottom: 24, paddingHorizontal: 20 },
  heroGreeting: { fontSize: 14, color: 'rgba(255,255,255,0.6)', marginTop: 4 },
  heroName: { fontSize: 28, fontWeight: '700', color: Colors.gold },
  herySub: { fontSize: 13, color: 'rgba(255,255,255,0.7)', marginTop: 2 },
  heroTagline: { fontSize: 12, color: 'rgba(255,255,255,0.4)', fontStyle: 'italic', marginTop: 2, marginBottom: 20 },
  quickGrid: { flexDirection: 'row', gap: 10 },
  quickBtn: { flex: 1, alignItems: 'center', gap: 6 },
  quickIcon: { width: 48, height: 48, borderRadius: 12, backgroundColor: 'rgba(201,162,39,0.12)', borderWidth: 1, borderColor: 'rgba(201,162,39,0.3)', alignItems: 'center', justifyContent: 'center' },
  quickLabel: { fontSize: 11, color: 'rgba(255,255,255,0.7)', fontWeight: '600' },
  adminBanner: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: 'rgba(201,162,39,0.1)', borderRadius: 10, padding: 12, marginTop: 16, borderWidth: 1, borderColor: 'rgba(201,162,39,0.2)' },
  adminBannerText: { flex: 1, color: Colors.gold, fontWeight: '600', fontSize: 14 },
  body: { paddingTop: 16, paddingBottom: 40 },
  urgentBanner: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: Colors.gold, padding: 12, marginHorizontal: 16, marginBottom: 16, borderRadius: 10 },
  urgentText: { flex: 1, fontWeight: '700', color: '#1a1a1a', fontSize: 13 },
  urgentMore: { fontWeight: '700', color: '#1a1a1a', fontSize: 13 },
  annCard: { marginHorizontal: 16 },
  annTitle: { fontSize: 15, fontWeight: '700', color: Colors.textPrimary, marginBottom: 5 },
  annContent: { fontSize: 13, color: Colors.textSecondary, lineHeight: 19, marginBottom: 8 },
  annDate: { fontSize: 11, color: Colors.textMuted },
  evtCard: { width: 200, marginBottom: 0 },
  evtDateBadge: { backgroundColor: Colors.red, borderRadius: 8, padding: 8, alignSelf: 'flex-start', alignItems: 'center', minWidth: 48, marginBottom: 10 },
  evtDay: { fontSize: 20, fontWeight: '700', color: '#fff', lineHeight: 22 },
  evtMonth: { fontSize: 10, color: 'rgba(255,255,255,0.85)', fontWeight: '600' },
  evtTitle: { fontSize: 14, fontWeight: '700', color: Colors.textPrimary, marginBottom: 8 },
  evtMeta: { flexDirection: 'row', alignItems: 'center', gap: 4, marginBottom: 4 },
  evtMetaText: { fontSize: 12, color: Colors.textMuted, flex: 1 },
  serviceCard: { backgroundColor: '#fff', borderRadius: 14, marginHorizontal: 16, marginTop: 20, padding: 18, elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.06, shadowRadius: 6 },
  serviceTitle: { fontSize: 15, fontWeight: '700', color: Colors.textPrimary, marginBottom: 12, borderBottomWidth: 2, borderBottomColor: Colors.gold, paddingBottom: 8 },
  serviceRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 7, borderBottomWidth: 1, borderBottomColor: Colors.border },
  serviceDay: { fontSize: 13, color: Colors.textPrimary, fontWeight: '500' },
  serviceTime: { fontSize: 13, color: Colors.red, fontWeight: '700' },
});
