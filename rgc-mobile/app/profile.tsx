import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Alert, TouchableOpacity, KeyboardAvoidingView, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { ENDPOINTS } from '../constants/Api';
import { Colors } from '../constants/Colors';
import { Input, Btn, Card } from '../components/UI';

export default function ProfileScreen() {
  const { user, token, refreshUser } = useAuth();
  const router = useRouter();
  const [first_name, setFirstName] = useState(user?.first_name || '');
  const [last_name, setLastName] = useState(user?.last_name || '');
  const [phone, setPhone] = useState(user?.phone || '');
  const [saving, setSaving] = useState(false);
  const [oldPass, setOldPass] = useState('');
  const [newPass, setNewPass] = useState('');
  const [changingPass, setChangingPass] = useState(false);

  async function saveProfile() {
    setSaving(true);
    try {
      const resp = await fetch(ENDPOINTS.PROFILE, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ first_name, last_name, phone }),
      });
      if (resp.ok) { await refreshUser(); Alert.alert('Saved', 'Profile updated successfully.'); }
      else { Alert.alert('Error', 'Could not save profile.'); }
    } catch (e) { Alert.alert('Error', 'Network error.'); }
    finally { setSaving(false); }
  }

  async function changePassword() {
    if (!oldPass || !newPass) { Alert.alert('Required', 'Enter current and new password.'); return; }
    if (newPass.length < 8) { Alert.alert('Error', 'New password must be at least 8 characters.'); return; }
    setChangingPass(true);
    try {
      const resp = await fetch(ENDPOINTS.CHANGE_PASSWORD, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ old_password: oldPass, new_password: newPass }),
      });
      const data = await resp.json();
      if (resp.ok) { Alert.alert('Password Changed', 'Your password has been updated.'); setOldPass(''); setNewPass(''); }
      else { Alert.alert('Error', data.error || 'Could not change password.'); }
    } catch (e) { Alert.alert('Error', 'Network error.'); }
    finally { setChangingPass(false); }
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
            <Ionicons name="arrow-back" size={22} color="#fff" />
          </TouchableOpacity>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>{(user?.first_name?.[0] || user?.username?.[0] || 'U').toUpperCase()}</Text>
          </View>
          <Text style={styles.name}>{user?.full_name || user?.username}</Text>
          <Text style={styles.email}>{user?.email}</Text>
          <View style={styles.badges}>
            <View style={[styles.badge, { backgroundColor: 'rgba(201,162,39,0.2)' }]}>
              <Ionicons name={user?.is_email_verified ? 'mail' : 'mail-outline'} size={12} color={user?.is_email_verified ? Colors.success : Colors.textMuted} />
              <Text style={[styles.badgeText, { color: user?.is_email_verified ? Colors.success : Colors.textMuted }]}>
                {user?.is_email_verified ? 'Email Verified' : 'Email Not Verified'}
              </Text>
            </View>
            <View style={[styles.badge, { backgroundColor: 'rgba(201,162,39,0.2)' }]}>
              <Ionicons name={user?.is_phone_verified ? 'call' : 'call-outline'} size={12} color={user?.is_phone_verified ? Colors.success : Colors.textMuted} />
              <Text style={[styles.badgeText, { color: user?.is_phone_verified ? Colors.success : Colors.textMuted }]}>
                {user?.is_phone_verified ? 'Phone Verified' : 'Phone Not Verified'}
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.body}>
          {/* Personal info */}
          <Card>
            <Text style={styles.sectionTitle}>Personal Information</Text>
            <View style={styles.row}>
              <Input label="First Name" value={first_name} onChangeText={setFirstName} containerStyle={{ flex: 1 }} />
              <View style={{ width: 10 }} />
              <Input label="Last Name" value={last_name} onChangeText={setLastName} containerStyle={{ flex: 1 }} />
            </View>
            <Input label="Phone (M-Pesa)" value={phone} onChangeText={setPhone} keyboardType="phone-pad" placeholder="0712 345 678" leftIcon={<Ionicons name="call-outline" size={16} color={Colors.textMuted} />} />
            <Btn title="Save Changes" onPress={saveProfile} loading={saving} size="md" style={{ width: '100%' }} />
          </Card>

          {/* Change password */}
          <Card>
            <Text style={styles.sectionTitle}>Change Password</Text>
            <Input label="Current Password" value={oldPass} onChangeText={setOldPass} secureTextEntry placeholder="Enter current password" leftIcon={<Ionicons name="lock-closed-outline" size={16} color={Colors.textMuted} />} />
            <Input label="New Password (min 8 chars)" value={newPass} onChangeText={setNewPass} secureTextEntry placeholder="Enter new password" leftIcon={<Ionicons name="lock-open-outline" size={16} color={Colors.textMuted} />} />
            <Btn title="Change Password" onPress={changePassword} loading={changingPass} variant="outline" size="md" style={{ width: '100%' }} />
          </Card>

          {/* Account info */}
          <Card>
            <Text style={styles.sectionTitle}>Account Details</Text>
            {[
              ['Username', user?.username],
              ['Role', user?.role],
              ['Member Since', user?.date_joined ? new Date(user.date_joined).toLocaleDateString('en-KE', { day: 'numeric', month: 'long', year: 'numeric' }) : ''],
            ].map(([label, value]) => (
              <View key={label} style={styles.infoRow}>
                <Text style={styles.infoLabel}>{label}</Text>
                <Text style={styles.infoValue}>{value}</Text>
              </View>
            ))}
          </Card>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  header: { backgroundColor: Colors.black, paddingTop: 56, paddingBottom: 24, paddingHorizontal: 20, alignItems: 'center' },
  backBtn: { position: 'absolute', top: 56, left: 20 },
  avatar: { width: 80, height: 80, borderRadius: 40, backgroundColor: Colors.red, alignItems: 'center', justifyContent: 'center', borderWidth: 3, borderColor: Colors.gold, marginBottom: 12 },
  avatarText: { fontSize: 32, fontWeight: '700', color: '#fff' },
  name: { fontSize: 22, fontWeight: '700', color: '#fff', marginBottom: 4 },
  email: { fontSize: 14, color: 'rgba(255,255,255,0.65)' },
  badges: { flexDirection: 'row', gap: 8, marginTop: 10, flexWrap: 'wrap', justifyContent: 'center' },
  badge: { flexDirection: 'row', alignItems: 'center', gap: 4, borderRadius: 20, paddingHorizontal: 10, paddingVertical: 4 },
  badgeText: { fontSize: 11, fontWeight: '600' },
  body: { padding: 16, paddingBottom: 40, gap: 12 },
  sectionTitle: { fontSize: 15, fontWeight: '700', color: Colors.red, marginBottom: 14 },
  row: { flexDirection: 'row' },
  infoRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: Colors.border },
  infoLabel: { fontSize: 13, color: Colors.textMuted },
  infoValue: { fontSize: 13, fontWeight: '600', color: Colors.textPrimary },
});
