import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  RefreshControl, Alert, ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { ENDPOINTS } from '../../constants/Api';
import { Colors } from '../../constants/Colors';
import { Badge, Card, Loader, Empty, Btn } from '../../components/UI';

export default function EventsScreen() {
  const { token, user } = useAuth();
  const [events, setEvents] = useState<any[]>([]);
  const [categories, setCategories] = useState<[string, string][]>([]);
  const [activeCat, setActiveCat] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [registering, setRegistering] = useState<number | null>(null);

  const fetchEvents = useCallback(async () => {
    try {
      const url = activeCat ? `${ENDPOINTS.EVENTS}?cat=${activeCat}` : ENDPOINTS.EVENTS;
      const resp = await fetch(url, token ? { headers: { Authorization: `Bearer ${token}` } } : {});
      if (resp.ok) {
        const data = await resp.json();
        setEvents(data.results || data);
        if (data.categories) setCategories(data.categories);
      }
    } catch (e) {} finally { setLoading(false); setRefreshing(false); }
  }, [activeCat, token]);

  useEffect(() => { fetchEvents(); }, [fetchEvents]);

  async function registerForEvent(eventId: number, title: string) {
    if (!token) { Alert.alert('Login Required', 'Please log in to register.'); return; }
    setRegistering(eventId);
    try {
      const resp = await fetch(`${ENDPOINTS.EVENTS}${eventId}/register/`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      const data = await resp.json();
      Alert.alert('Success', data.message || `Registered for ${title}!`);
      fetchEvents();
    } catch (e) {
      Alert.alert('Error', 'Registration failed. Please try again.');
    } finally { setRegistering(null); }
  }

  if (loading) return <Loader message="Loading events..." />;

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="calendar" size={24} color={Colors.gold} />
        <Text style={styles.headerTitle}>Church Events</Text>
        <Text style={styles.headerSub}>{events.length} upcoming</Text>
      </View>

      {/* Category filter */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filterRow}>
        <TouchableOpacity style={[styles.filterChip, !activeCat && styles.filterActive]} onPress={() => setActiveCat('')}>
          <Text style={[styles.filterText, !activeCat && styles.filterTextActive]}>All</Text>
        </TouchableOpacity>
        {categories.map(([value, label]) => (
          <TouchableOpacity key={value} style={[styles.filterChip, activeCat === value && styles.filterActive]} onPress={() => setActiveCat(value)}>
            <Text style={[styles.filterText, activeCat === value && styles.filterTextActive]}>{label}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Events list */}
      <FlatList
        data={events}
        keyExtractor={i => String(i.id)}
        contentContainerStyle={{ padding: 16, paddingBottom: 30, gap: 12 }}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchEvents(); }} tintColor={Colors.gold} />}
        ListEmptyComponent={<Empty title={`No events${activeCat ? ' in this category' : ''}`} subtitle="Check back later for upcoming events." />}
        renderItem={({ item }) => (
          <Card>
            {/* Date badge + category */}
            <View style={styles.evtTop}>
              <View style={styles.dateBadge}>
                <Text style={styles.dateDay}>{new Date(item.date).getDate()}</Text>
                <Text style={styles.dateMonth}>{new Date(item.date).toLocaleString('en', { month: 'short' }).toUpperCase()}</Text>
              </View>
              <View style={{ flex: 1, marginLeft: 12 }}>
                <Badge label={item.category_display} color={Colors.red} size="sm" />
                <Text style={styles.evtTitle}>{item.title}</Text>
              </View>
            </View>

            <Text style={styles.evtDesc} numberOfLines={3}>{item.description}</Text>

            <View style={styles.evtMeta}>
              <View style={styles.metaItem}><Ionicons name="time-outline" size={14} color={Colors.textMuted} /><Text style={styles.metaText}>{item.time?.slice(0, 5)}</Text></View>
              <View style={styles.metaItem}><Ionicons name="location-outline" size={14} color={Colors.textMuted} /><Text style={styles.metaText} numberOfLines={1}>{item.location}</Text></View>
              <View style={styles.metaItem}><Ionicons name="people-outline" size={14} color={Colors.textMuted} /><Text style={styles.metaText}>{item.attendee_count} registered</Text></View>
            </View>

            {user ? (
              item.is_registered ? (
                <View style={styles.registeredBadge}>
                  <Ionicons name="checkmark-circle" size={16} color={Colors.success} />
                  <Text style={styles.registeredText}>You are registered</Text>
                </View>
              ) : (
                <Btn
                  title={registering === item.id ? 'Registering...' : 'Register'}
                  onPress={() => registerForEvent(item.id, item.title)}
                  loading={registering === item.id}
                  size="sm"
                  style={{ marginTop: 12 }}
                />
              )
            ) : (
              <Text style={styles.loginPrompt}>Login to register for this event</Text>
            )}
          </Card>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  header: { backgroundColor: Colors.black, paddingTop: 56, paddingBottom: 18, paddingHorizontal: 20, flexDirection: 'row', alignItems: 'center', gap: 10 },
  headerTitle: { fontSize: 22, fontWeight: '700', color: Colors.gold, flex: 1 },
  headerSub: { fontSize: 12, color: 'rgba(255,255,255,0.5)' },
  filterRow: { paddingHorizontal: 16, paddingVertical: 12, gap: 8 },
  filterChip: { paddingHorizontal: 14, paddingVertical: 7, borderRadius: 20, borderWidth: 1.5, borderColor: Colors.border, backgroundColor: '#fff' },
  filterActive: { backgroundColor: Colors.red, borderColor: Colors.red },
  filterText: { fontSize: 12, fontWeight: '600', color: Colors.textMuted },
  filterTextActive: { color: '#fff' },
  evtTop: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 10 },
  dateBadge: { backgroundColor: Colors.red, borderRadius: 10, padding: 10, alignItems: 'center', minWidth: 52 },
  dateDay: { fontSize: 22, fontWeight: '700', color: '#fff', lineHeight: 24 },
  dateMonth: { fontSize: 10, color: 'rgba(255,255,255,0.85)', fontWeight: '700' },
  evtTitle: { fontSize: 16, fontWeight: '700', color: Colors.textPrimary, marginTop: 4 },
  evtDesc: { fontSize: 13, color: Colors.textSecondary, lineHeight: 19, marginBottom: 10 },
  evtMeta: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 4 },
  metaItem: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  metaText: { fontSize: 12, color: Colors.textMuted },
  registeredBadge: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 12, backgroundColor: '#f0fff4', borderRadius: 8, padding: 10 },
  registeredText: { color: Colors.success, fontWeight: '600', fontSize: 13 },
  loginPrompt: { marginTop: 10, fontSize: 12, color: Colors.textMuted, fontStyle: 'italic' },
});
