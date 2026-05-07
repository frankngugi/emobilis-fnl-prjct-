import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { Colors } from '../../constants/Colors';
import { ENDPOINTS } from '../../constants/Api';
import { Card } from '../../components/UI';

interface MenuItem { icon: any; label: string; desc: string; route?: string; action?: () => void; badge?: string; color?: string; }

export default function MoreScreen() {
  const { user, logout, isManager, isAdmin, token } = useAuth();
  const router = useRouter();
  const [groups, setGroups] = useState<any[]>([]);
  const [myGroup, setMyGroup] = useState<any>(null);

  useEffect(() => { fetchGroups(); }, [token]);

  async function fetchGroups() {
    try {
      const resp = await fetch(ENDPOINTS.GROUPS);
      if (resp.ok) { const d = await resp.json(); setGroups((d.results || d).slice(0, 6)); }
    } catch (e) {}
  }

  async function handleLogout() {
    Alert.alert('Logout', 'Are you sure you want to log out?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Logout', style: 'destructive', onPress: async () => { await logout(); } },
    ]);
  }

  const sections: { title: string; items: MenuItem[] }[] = [
    {
      title: 'Church Life',
      items: [
        { icon: 'images', label: 'Photo Gallery', desc: 'Browse church photos by category', route: '/gallery' },
        { icon: 'play-circle', label: 'Videos & Sermons', desc: 'Watch recorded services and sermons', route: '/videos' },
        { icon: 'megaphone', label: 'Announcements', desc: 'Latest church news and updates', route: '/announcements' },
        { icon: 'people', label: 'Groups & Ministries', desc: 'Join a ministry or fellowship', route: '/groups' },
      ],
    },
    {
      title: 'My Account',
      items: [
        { icon: 'person', label: 'My Profile', desc: 'Update your personal information', route: '/profile' },
        { icon: 'calendar-check', label: 'My Events', desc: 'Events you have registered for', route: '/my-events' },
        { icon: 'shield-checkmark', label: 'Request Role Upgrade', desc: 'Apply to become a manager or admin', route: '/request-role' },
      ],
    },
    ...(isManager ? [{
      title: 'Admin',
      items: [
        { icon: 'speedometer', label: 'Admin Dashboard', desc: 'Stats, members, events overview', route: '/admin', color: Colors.gold } as MenuItem,
        { icon: 'people-circle', label: 'Manage Users', desc: 'Change roles and permissions', route: '/admin/users', color: Colors.gold } as MenuItem,
      ],
    }] : []),
    {
      title: '',
      items: [
        { icon: 'log-out', label: 'Logout', desc: `Signed in as ${user?.username}`, action: handleLogout, color: Colors.error },
      ],
    },
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Profile Header */}
      <View style={styles.profileHeader}>
        <View style={styles.avatar}>
          {user?.profile_picture
            ? <Image source={{ uri: user.profile_picture }} style={styles.avatarImg} />
            : <Text style={styles.avatarInitial}>{(user?.first_name?.[0] || user?.username?.[0] || 'U').toUpperCase()}</Text>
          }
        </View>
        <View style={{ flex: 1 }}>
          <Text style={styles.userName}>{user?.full_name || user?.username}</Text>
          <Text style={styles.userEmail}>{user?.email}</Text>
          <View style={styles.roleBadge}>
            <Ionicons name={isAdmin ? 'shield' : isManager ? 'briefcase' : 'person'} size={12} color={isAdmin ? Colors.red : isManager ? Colors.gold : Colors.textMuted} />
            <Text style={[styles.roleText, { color: isAdmin ? Colors.red : isManager ? Colors.gold : Colors.textMuted }]}>
              {isAdmin ? 'Admin' : isManager ? 'Manager' : 'Member'}
            </Text>
          </View>
        </View>
        <TouchableOpacity onPress={() => router.push('/profile' as any)} style={styles.editBtn}>
          <Ionicons name="pencil" size={16} color={Colors.red} />
        </TouchableOpacity>
      </View>

      {/* Groups */}
      {groups.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Ministries & Groups</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.groupRow}>
            {groups.map(g => (
              <TouchableOpacity key={g.id} style={styles.groupChip} onPress={() => router.push('/groups' as any)}>
                <View style={styles.groupIcon}>
                  <Ionicons name="people" size={18} color={Colors.gold} />
                </View>
                <Text style={styles.groupName} numberOfLines={2}>{g.name}</Text>
                <Text style={styles.groupCount}>{g.member_count} members</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}

      {/* Menu sections */}
      {sections.map(section => (
        <View key={section.title} style={styles.section}>
          {section.title ? <Text style={styles.sectionTitle}>{section.title}</Text> : null}
          <Card style={{ padding: 0, overflow: 'hidden' }}>
            {section.items.map((item, idx) => (
              <TouchableOpacity
                key={item.label}
                style={[styles.menuItem, idx < section.items.length - 1 && styles.menuBorder]}
                onPress={item.action || (() => item.route && router.push(item.route as any))}
                activeOpacity={0.7}
              >
                <View style={[styles.menuIcon, { backgroundColor: `${item.color || Colors.red}15` }]}>
                  <Ionicons name={item.icon} size={20} color={item.color || Colors.red} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={[styles.menuLabel, item.color && { color: item.color }]}>{item.label}</Text>
                  <Text style={styles.menuDesc}>{item.desc}</Text>
                </View>
                {item.badge && <View style={styles.badge}><Text style={styles.badgeText}>{item.badge}</Text></View>}
                {!item.badge && <Ionicons name="chevron-forward" size={16} color={Colors.border} />}
              </TouchableOpacity>
            ))}
          </Card>
        </View>
      ))}

      {/* App info */}
      <Text style={styles.appInfo}>RGC Nyahururu v1.0 · Django 6 · Expo 52</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  profileHeader: { backgroundColor: Colors.black, paddingTop: 56, paddingBottom: 20, paddingHorizontal: 20, flexDirection: 'row', alignItems: 'center', gap: 14 },
  avatar: { width: 60, height: 60, borderRadius: 30, backgroundColor: Colors.red, alignItems: 'center', justifyContent: 'center', borderWidth: 2, borderColor: Colors.gold },
  avatarImg: { width: 60, height: 60, borderRadius: 30 },
  avatarInitial: { fontSize: 26, fontWeight: '700', color: '#fff' },
  userName: { fontSize: 18, fontWeight: '700', color: '#fff' },
  userEmail: { fontSize: 13, color: 'rgba(255,255,255,0.6)', marginTop: 2 },
  roleBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 5 },
  roleText: { fontSize: 12, fontWeight: '600' },
  editBtn: { padding: 8, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 20 },
  section: { paddingHorizontal: 16, paddingTop: 16 },
  sectionTitle: { fontSize: 12, fontWeight: '700', color: Colors.textMuted, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10 },
  groupRow: { gap: 10, paddingBottom: 4 },
  groupChip: { width: 110, backgroundColor: '#fff', borderRadius: 12, padding: 12, alignItems: 'center', gap: 6, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 4, elevation: 1 },
  groupIcon: { width: 40, height: 40, borderRadius: 10, backgroundColor: 'rgba(201,162,39,0.1)', alignItems: 'center', justifyContent: 'center' },
  groupName: { fontSize: 12, fontWeight: '600', color: Colors.textPrimary, textAlign: 'center' },
  groupCount: { fontSize: 10, color: Colors.textMuted },
  menuItem: { flexDirection: 'row', alignItems: 'center', padding: 14, gap: 12 },
  menuBorder: { borderBottomWidth: 1, borderBottomColor: Colors.background },
  menuIcon: { width: 38, height: 38, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  menuLabel: { fontSize: 15, fontWeight: '600', color: Colors.textPrimary },
  menuDesc: { fontSize: 12, color: Colors.textMuted, marginTop: 1 },
  badge: { backgroundColor: Colors.red, borderRadius: 20, paddingHorizontal: 8, paddingVertical: 3 },
  badgeText: { fontSize: 11, color: '#fff', fontWeight: '700' },
  appInfo: { textAlign: 'center', fontSize: 11, color: Colors.textMuted, padding: 20, paddingTop: 8 },
});
