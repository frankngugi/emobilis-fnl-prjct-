import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Alert, RefreshControl } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { ENDPOINTS } from '../constants/Api';
import { Colors } from '../constants/Colors';
import { Card, Badge, Btn, Loader, Empty } from '../components/UI';

export default function GroupsScreen() {
  const { user, token, isManager } = useAuth();
  const router = useRouter();
  const [groups, setGroups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [joining, setJoining] = useState<number | null>(null);

  const fetchGroups = async () => {
    try {
      const resp = await fetch(ENDPOINTS.GROUPS, token ? { headers: { Authorization: `Bearer ${token}` } } : {});
      if (resp.ok) { const d = await resp.json(); setGroups(d.results || d); }
    } catch (e) {} finally { setLoading(false); setRefreshing(false); }
  };

  useEffect(() => { fetchGroups(); }, []);

  async function joinGroup(groupId: number, groupName: string) {
    if (!token) { Alert.alert('Login Required', 'Please log in to join a group.'); return; }
    setJoining(groupId);
    try {
      const resp = await fetch(`${ENDPOINTS.GROUPS}${groupId}/join/`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      const data = await resp.json();
      if (resp.ok) { Alert.alert('Joined!', data.message); fetchGroups(); }
      else Alert.alert('Error', data.error || 'Could not join group.');
    } catch (e) { Alert.alert('Error', 'Network error.'); }
    finally { setJoining(null); }
  }

  const catIconMap: Record<string, any> = {
    ministry: 'church', fellowship: 'people', youth: 'rocket', women: 'flower', men: 'fitness', children: 'happy', choir: 'musical-notes', other: 'grid',
  };

  if (loading) return <Loader message="Loading groups..." />;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#fff" />
        </TouchableOpacity>
        <Ionicons name="people" size={24} color={Colors.gold} />
        <Text style={styles.headerTitle}>Groups & Ministries</Text>
        {isManager && (
          <TouchableOpacity style={styles.addBtn} onPress={() => Alert.alert('Create Group', 'Use the web portal (/create-group/) to create a new group.')}>
            <Ionicons name="add" size={22} color={Colors.gold} />
          </TouchableOpacity>
        )}
      </View>

      <FlatList
        data={groups}
        keyExtractor={g => String(g.id)}
        contentContainerStyle={{ padding: 16, gap: 12, paddingBottom: 30 }}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchGroups(); }} tintColor={Colors.gold} />}
        ListEmptyComponent={<Empty title="No groups yet" subtitle="Check back later or ask an admin to create groups." />}
        renderItem={({ item: g }) => (
          <Card>
            <View style={styles.groupHeader}>
              <View style={styles.groupIcon}>
                <Ionicons name={catIconMap[g.category] || 'people'} size={24} color={Colors.gold} />
              </View>
              <View style={{ flex: 1, marginLeft: 12 }}>
                <Text style={styles.groupName}>{g.name}</Text>
                <Badge label={g.category_display} color={Colors.black} size="sm" />
              </View>
              {g.is_member && (
                <View style={styles.memberTag}>
                  <Ionicons name="checkmark-circle" size={14} color={Colors.success} />
                  <Text style={styles.memberTagText}>Member</Text>
                </View>
              )}
            </View>
            <Text style={styles.groupDesc} numberOfLines={3}>{g.description}</Text>
            <View style={styles.groupMeta}>
              <View style={styles.metaItem}>
                <Ionicons name="people-outline" size={14} color={Colors.textMuted} />
                <Text style={styles.metaText}>{g.member_count} members</Text>
              </View>
              {g.leader_name && (
                <View style={styles.metaItem}>
                  <Ionicons name="person-outline" size={14} color={Colors.textMuted} />
                  <Text style={styles.metaText}>{g.leader_name}</Text>
                </View>
              )}
            </View>
            {!g.is_member && user && (
              <Btn
                title={joining === g.id ? 'Joining...' : 'Join This Group'}
                onPress={() => joinGroup(g.id, g.name)}
                loading={joining === g.id}
                size="sm"
                style={{ marginTop: 10 }}
              />
            )}
            {!user && (
              <Text style={styles.loginPrompt}>Login to join this group</Text>
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
  backBtn: {},
  headerTitle: { fontSize: 20, fontWeight: '700', color: Colors.gold, flex: 1 },
  addBtn: { padding: 4 },
  groupHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  groupIcon: { width: 48, height: 48, borderRadius: 12, backgroundColor: 'rgba(201,162,39,0.1)', alignItems: 'center', justifyContent: 'center' },
  groupName: { fontSize: 16, fontWeight: '700', color: Colors.textPrimary, marginBottom: 4 },
  memberTag: { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: '#f0fff4', borderRadius: 20, paddingHorizontal: 8, paddingVertical: 4 },
  memberTagText: { fontSize: 11, color: Colors.success, fontWeight: '600' },
  groupDesc: { fontSize: 13, color: Colors.textSecondary, lineHeight: 19, marginBottom: 10 },
  groupMeta: { flexDirection: 'row', gap: 16 },
  metaItem: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  metaText: { fontSize: 12, color: Colors.textMuted },
  loginPrompt: { marginTop: 10, fontSize: 12, color: Colors.textMuted, fontStyle: 'italic' },
});
