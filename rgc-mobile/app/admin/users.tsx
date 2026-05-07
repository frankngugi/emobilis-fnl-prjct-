import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { ENDPOINTS, API_URL } from '../../constants/Api';
import { Colors } from '../../constants/Colors';
import { Badge, Card } from '../../components/UI';

const ROLES = ['member', 'manager', 'admin'];

export default function AdminUsersScreen() {
  const { token, user: me, isAdmin } = useAuth();
  const router = useRouter();
  const [users, setUsers] = useState<any[]>([]);
  const [filtered, setFiltered] = useState<any[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<number | null>(null);

  useEffect(() => { fetchUsers(); }, []);
  useEffect(() => {
    if (!query) { setFiltered(users); return; }
    const q = query.toLowerCase();
    setFiltered(users.filter(u => u.username.toLowerCase().includes(q) || u.email.toLowerCase().includes(q) || (u.full_name || '').toLowerCase().includes(q)));
  }, [query, users]);

  async function fetchUsers() {
    try {
      const resp = await fetch(ENDPOINTS.ALL_MEMBERS, { headers: { Authorization: `Bearer ${token}` } });
      if (resp.ok) {
        const data = await resp.json();
        setUsers(data.results || data);
        setFiltered(data.results || data);
      }
    } catch (e) {} finally { setLoading(false); }
  }

  async function changeRole(userId: number, username: string, newRole: string) {
    if (userId === me?.id && newRole !== 'admin') { Alert.alert('Error', "You can't remove your own admin role."); return; }
    Alert.alert('Confirm', `Change ${username}'s role to ${newRole}?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Confirm', style: 'default',
        onPress: async () => {
          setUpdating(userId);
          try {
            const resp = await fetch(`${API_URL}/admin/members/${userId}/role/`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
              body: JSON.stringify({ role: newRole }),
            });
            const data = await resp.json();
            if (resp.ok) { Alert.alert('Updated', data.message); fetchUsers(); }
            else Alert.alert('Error', data.error || 'Failed to update.');
          } catch (e) { Alert.alert('Error', 'Network error.'); }
          finally { setUpdating(null); }
        },
      },
    ]);
  }

  const roleColor: Record<string, string> = { admin: Colors.red, manager: Colors.gold, member: Colors.border };
  const roleTextColor: Record<string, string> = { admin: '#fff', manager: '#1a1a1a', member: Colors.textPrimary };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Manage Users</Text>
        <Text style={styles.headerSub}>{users.length} total members</Text>
      </View>

      <View style={styles.searchWrap}>
        <Ionicons name="search" size={18} color={Colors.textMuted} style={{ marginRight: 8 }} />
        <TextInput style={styles.searchInput} value={query} onChangeText={setQuery} placeholder="Search by name, email, username..." placeholderTextColor={Colors.textMuted} />
        {query.length > 0 && <TouchableOpacity onPress={() => setQuery('')}><Ionicons name="close-circle" size={18} color={Colors.textMuted} /></TouchableOpacity>}
      </View>

      {loading ? <ActivityIndicator size="large" color={Colors.red} style={{ marginTop: 40 }} /> : (
        <FlatList
          data={filtered}
          keyExtractor={u => String(u.id)}
          contentContainerStyle={{ padding: 14, gap: 10, paddingBottom: 30 }}
          showsVerticalScrollIndicator={false}
          renderItem={({ item: u }) => (
            <Card style={{ gap: 0 }}>
              <View style={styles.userRow}>
                <View style={styles.avatar}>
                  <Text style={styles.avatarText}>{(u.first_name?.[0] || u.username?.[0] || '?').toUpperCase()}</Text>
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.userName}>{u.full_name || u.username}</Text>
                  <Text style={styles.userEmail}>{u.email}</Text>
                  {u.phone && <Text style={styles.userPhone}><Ionicons name="call-outline" size={11} /> {u.phone}</Text>}
                </View>
                <View style={{ alignItems: 'flex-end', gap: 4 }}>
                  <Badge label={u.role} color={roleColor[u.role] || Colors.border} textColor={roleTextColor[u.role]} />
                  {u.is_superuser && <Badge label="Superadmin" color={Colors.black} textColor="#fff" size="sm" />}
                </View>
              </View>

              {/* Role change buttons (only for admins, not self) */}
              {isAdmin && (
                <View style={styles.roleButtons}>
                  <Text style={styles.changeRoleLabel}>Change role:</Text>
                  {ROLES.map(role => (
                    <TouchableOpacity
                      key={role}
                      style={[styles.roleBtn, u.role === role && styles.roleBtnActive]}
                      onPress={() => u.role !== role && changeRole(u.id, u.username, role)}
                      disabled={u.role === role || updating === u.id}
                    >
                      {updating === u.id ? <ActivityIndicator size="small" color={Colors.red} /> : (
                        <Text style={[styles.roleBtnText, u.role === role && styles.roleBtnTextActive]}>{role}</Text>
                      )}
                    </TouchableOpacity>
                  ))}
                </View>
              )}
            </Card>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  header: { backgroundColor: Colors.black, paddingTop: 56, paddingBottom: 16, paddingHorizontal: 20 },
  backBtn: { marginBottom: 10 },
  headerTitle: { fontSize: 22, fontWeight: '700', color: Colors.gold },
  headerSub: { fontSize: 12, color: 'rgba(255,255,255,0.5)', marginTop: 2 },
  searchWrap: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', margin: 14, borderRadius: 12, paddingHorizontal: 14, borderWidth: 1.5, borderColor: Colors.border },
  searchInput: { flex: 1, paddingVertical: 13, fontSize: 15, color: Colors.textPrimary },
  userRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 12, marginBottom: 10 },
  avatar: { width: 44, height: 44, borderRadius: 22, backgroundColor: Colors.red, alignItems: 'center', justifyContent: 'center' },
  avatarText: { fontSize: 18, fontWeight: '700', color: '#fff' },
  userName: { fontSize: 15, fontWeight: '700', color: Colors.textPrimary },
  userEmail: { fontSize: 12, color: Colors.textMuted, marginTop: 1 },
  userPhone: { fontSize: 12, color: Colors.textMuted, marginTop: 2 },
  roleButtons: { flexDirection: 'row', alignItems: 'center', gap: 6, flexWrap: 'wrap', paddingTop: 10, borderTopWidth: 1, borderTopColor: Colors.background },
  changeRoleLabel: { fontSize: 11, color: Colors.textMuted, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.5 },
  roleBtn: { paddingHorizontal: 12, paddingVertical: 5, borderRadius: 20, borderWidth: 1.5, borderColor: Colors.border, backgroundColor: '#fff' },
  roleBtnActive: { borderColor: Colors.red, backgroundColor: Colors.red },
  roleBtnText: { fontSize: 12, fontWeight: '600', color: Colors.textMuted },
  roleBtnTextActive: { color: '#fff' },
});
