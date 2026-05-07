import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { ENDPOINTS } from '../../constants/Api';
import { Colors } from '../../constants/Colors';
import { Card, SectionHeader, Badge, Loader, Btn } from '../../components/UI';

export default function AdminDashboard() {
  const { user, token, isManager, isAdmin } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStats = async () => {
    try {
      const resp = await fetch(ENDPOINTS.DASHBOARD, { headers: { Authorization: `Bearer ${token}` } });
      if (resp.ok) setStats(await resp.json());
      else Alert.alert('Access Denied', 'You do not have admin access.');
    } catch (e) {} finally { setLoading(false); setRefreshing(false); }
  };

  useEffect(() => { fetchStats(); }, []);

  if (loading) return <Loader message="Loading dashboard..." />;

  const statCards = [
    { label: 'Members', value: stats?.total_members, icon: 'people', color: Colors.red },
    { label: 'Events', value: stats?.total_events, icon: 'calendar', color: Colors.gold },
    { label: 'Groups', value: stats?.total_groups, icon: 'grid', color: Colors.black },
    { label: 'Payments', value: stats?.total_payments, icon: 'card', color: Colors.success },
  ];

  const quickActions = [
    { icon: 'megaphone', label: 'Post Announcement', color: Colors.red, web: '/announcements/add/' },
    { icon: 'calendar-plus', label: 'Add Event', color: Colors.gold, web: '/adminn/addevents' },
    { icon: 'person-add', label: 'Manage Users', color: Colors.black, screen: '/admin/users' },
    { icon: 'images', label: 'Upload Media', color: Colors.info, web: '/adminn/uploadimages' },
  ];

  return (
    <ScrollView
      style={styles.container}
      showsVerticalScrollIndicator={false}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchStats(); }} tintColor={Colors.gold} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#fff" />
        </TouchableOpacity>
        <Ionicons name="shield" size={28} color={Colors.gold} />
        <View style={{ flex: 1, marginLeft: 10 }}>
          <Text style={styles.headerTitle}>Admin Dashboard</Text>
          <Text style={styles.headerSub}>Welcome, {user?.first_name || user?.username}</Text>
        </View>
        {stats?.pending_role_requests > 0 && (
          <TouchableOpacity onPress={() => router.push('/admin/users' as any)} style={styles.alertBadge}>
            <Ionicons name="notifications" size={16} color="#fff" />
            <Text style={styles.alertBadgeText}>{stats.pending_role_requests}</Text>
          </TouchableOpacity>
        )}
      </View>

      <View style={styles.body}>
        {/* Stats grid */}
        <View style={styles.statsGrid}>
          {statCards.map(s => (
            <View key={s.label} style={[styles.statCard, { borderLeftColor: s.color }]}>
              <Ionicons name={s.icon as any} size={22} color={s.color} />
              <Text style={styles.statValue}>{s.value ?? '—'}</Text>
              <Text style={styles.statLabel}>{s.label}</Text>
            </View>
          ))}
        </View>

        {/* Quick Actions */}
        <SectionHeader title="Quick Actions" />
        <View style={styles.actionsGrid}>
          {quickActions.map(a => (
            <TouchableOpacity
              key={a.label}
              style={[styles.actionBtn, { borderColor: a.color }]}
              onPress={() => a.screen ? router.push(a.screen as any) : Alert.alert('Web Action', `Open ${a.web} in your browser or web portal.`)}
              activeOpacity={0.8}
            >
              <View style={[styles.actionIcon, { backgroundColor: `${a.color}15` }]}>
                <Ionicons name={a.icon as any} size={22} color={a.color} />
              </View>
              <Text style={styles.actionLabel} numberOfLines={2}>{a.label}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Pending role requests */}
        {stats?.pending_role_requests > 0 && (
          <TouchableOpacity style={styles.pendingAlert} onPress={() => router.push('/admin/users' as any)}>
            <Ionicons name="hourglass" size={20} color={Colors.gold} />
            <Text style={styles.pendingText}>{stats.pending_role_requests} pending role request{stats.pending_role_requests > 1 ? 's' : ''} waiting for review</Text>
            <Ionicons name="chevron-forward" size={16} color={Colors.gold} />
          </TouchableOpacity>
        )}

        {/* Recent Members */}
        {stats?.recent_members?.length > 0 && (
          <>
            <SectionHeader title="Recent Members" action={{ label: 'All Members', onPress: () => router.push('/admin/users' as any) }} style={{ marginTop: 8 }} />
            {stats.recent_members.map((m: any) => (
              <Card key={m.id} style={styles.memberRow}>
                <View style={styles.memberAvatar}>
                  <Text style={styles.memberAvatarText}>{(m.first_name?.[0] || m.username?.[0] || '?').toUpperCase()}</Text>
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.memberName}>{m.full_name || m.username}</Text>
                  <Text style={styles.memberEmail}>{m.email}</Text>
                </View>
                <Badge label={m.role} color={m.role === 'admin' ? Colors.red : m.role === 'manager' ? Colors.gold : Colors.border} textColor={m.role === 'manager' ? '#1a1a1a' : m.role === 'member' ? Colors.textPrimary : '#fff'} />
              </Card>
            ))}
          </>
        )}

        {/* Upcoming Events */}
        {stats?.upcoming_events?.length > 0 && (
          <>
            <SectionHeader title="Upcoming Events" style={{ marginTop: 8 }} />
            {stats.upcoming_events.map((e: any) => (
              <Card key={e.id} style={{ flexDirection: 'row', gap: 12, alignItems: 'center' }}>
                <View style={styles.evtDate}>
                  <Text style={styles.evtDay}>{new Date(e.date).getDate()}</Text>
                  <Text style={styles.evtMon}>{new Date(e.date).toLocaleString('en', { month: 'short' }).toUpperCase()}</Text>
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.evtTitle}>{e.title}</Text>
                  <Text style={styles.evtLoc}><Ionicons name="location-outline" size={12} /> {e.location}</Text>
                </View>
                <Badge label={e.category_display} color={Colors.red} size="sm" />
              </Card>
            ))}
          </>
        )}

        {/* Recent Payments */}
        {stats?.recent_payments?.length > 0 && (
          <>
            <SectionHeader title="Recent Contributions" style={{ marginTop: 8 }} />
            {stats.recent_payments.map((p: any) => (
              <Card key={p.id} style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
                <View style={styles.payIcon}>
                  <Ionicons name="card" size={18} color={Colors.success} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.payPhone}>{p.phone_number}</Text>
                  <Text style={styles.payPurpose}>{p.purpose_display}</Text>
                </View>
                <View style={{ alignItems: 'flex-end' }}>
                  <Text style={styles.payAmount}>KES {p.amount}</Text>
                  <Badge label={p.status} color={p.status === 'completed' ? Colors.success : p.status === 'pending' ? Colors.warning : Colors.error} size="sm" />
                </View>
              </Card>
            ))}
          </>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  header: { backgroundColor: Colors.black, paddingTop: 56, paddingBottom: 20, paddingHorizontal: 20, flexDirection: 'row', alignItems: 'center', gap: 4 },
  backBtn: { marginRight: 6 },
  headerTitle: { fontSize: 20, fontWeight: '700', color: Colors.gold },
  headerSub: { fontSize: 12, color: 'rgba(255,255,255,0.6)' },
  alertBadge: { backgroundColor: Colors.red, borderRadius: 20, paddingHorizontal: 10, paddingVertical: 6, flexDirection: 'row', alignItems: 'center', gap: 4 },
  alertBadgeText: { color: '#fff', fontWeight: '700', fontSize: 13 },
  body: { padding: 16, paddingBottom: 40 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 20 },
  statCard: { flex: 1, minWidth: '45%', backgroundColor: '#fff', borderRadius: 12, padding: 16, borderLeftWidth: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.06, shadowRadius: 6, elevation: 2, gap: 4 },
  statValue: { fontSize: 28, fontWeight: '700', color: Colors.textPrimary },
  statLabel: { fontSize: 12, color: Colors.textMuted, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.5 },
  actionsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 16 },
  actionBtn: { flex: 1, minWidth: '45%', backgroundColor: '#fff', borderRadius: 12, padding: 14, alignItems: 'center', gap: 8, borderWidth: 1.5 },
  actionIcon: { width: 44, height: 44, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  actionLabel: { fontSize: 12, fontWeight: '700', color: Colors.textPrimary, textAlign: 'center' },
  pendingAlert: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: 'rgba(201,162,39,0.1)', borderRadius: 10, padding: 14, marginBottom: 16, borderWidth: 1, borderColor: 'rgba(201,162,39,0.3)' },
  pendingText: { flex: 1, fontWeight: '600', color: Colors.textPrimary, fontSize: 14 },
  memberRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  memberAvatar: { width: 40, height: 40, borderRadius: 20, backgroundColor: Colors.red, alignItems: 'center', justifyContent: 'center' },
  memberAvatarText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  memberName: { fontSize: 14, fontWeight: '600', color: Colors.textPrimary },
  memberEmail: { fontSize: 12, color: Colors.textMuted },
  evtDate: { backgroundColor: Colors.red, borderRadius: 8, padding: 8, alignItems: 'center', minWidth: 44 },
  evtDay: { fontSize: 18, fontWeight: '700', color: '#fff' },
  evtMon: { fontSize: 9, color: 'rgba(255,255,255,0.8)', fontWeight: '700' },
  evtTitle: { fontSize: 14, fontWeight: '600', color: Colors.textPrimary },
  evtLoc: { fontSize: 12, color: Colors.textMuted, marginTop: 2 },
  payIcon: { width: 38, height: 38, borderRadius: 10, backgroundColor: '#f0fff4', alignItems: 'center', justifyContent: 'center' },
  payPhone: { fontSize: 14, fontWeight: '600', color: Colors.textPrimary },
  payPurpose: { fontSize: 12, color: Colors.textMuted },
  payAmount: { fontSize: 15, fontWeight: '700', color: Colors.textPrimary },
});
