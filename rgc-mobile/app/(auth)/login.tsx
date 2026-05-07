import React, { useState } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  KeyboardAvoidingView, Platform, Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { Colors } from '../../constants/Colors';
import { Btn, Input } from '../../components/UI';

type Portal = 'member' | 'manager' | 'admin';

const PORTALS: { key: Portal; label: string; icon: any; desc: string; color: string }[] = [
  { key: 'member', label: 'Member', icon: 'person', desc: 'Church member access', color: Colors.success },
  { key: 'manager', label: 'Manager', icon: 'briefcase', desc: 'Staff dashboard', color: Colors.gold },
  { key: 'admin', label: 'Admin', icon: 'shield', desc: 'Full system access', color: Colors.red },
];

export default function LoginScreen() {
  const { login } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [portal, setPortal] = useState<Portal>('member');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleLogin() {
    if (!username.trim() || !password) {
      setError('Please enter username and password.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await login(username.trim(), password);
      // auth redirect handled by root layout
    } catch (e: any) {
      setError(e.message || 'Login failed. Check your credentials.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>

        {/* Brand Header */}
        <View style={styles.brand}>
          <View style={styles.logoCircle}>
            <Ionicons name="leaf" size={36} color={Colors.gold} />
          </View>
          <Text style={styles.churchName}>Redeemed Gospel Church</Text>
          <Text style={styles.churchSub}>Nyahururu, Laikipia County</Text>
          <Text style={styles.churchTagline}>"Where everybody is somebody"</Text>
        </View>

        {/* Form Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Welcome Back</Text>
          <Text style={styles.cardSub}>Select your portal and sign in</Text>

          {/* Portal Selector */}
          <View style={styles.portalRow}>
            {PORTALS.map(p => (
              <TouchableOpacity
                key={p.key}
                style={[styles.portalBtn, portal === p.key && { borderColor: p.color, backgroundColor: `${p.color}15` }]}
                onPress={() => setPortal(p.key)}
                activeOpacity={0.8}
              >
                <Ionicons name={p.icon as any} size={20} color={portal === p.key ? p.color : Colors.textMuted} />
                <Text style={[styles.portalLabel, portal === p.key && { color: p.color }]}>{p.label}</Text>
                <Text style={styles.portalDesc}>{p.desc}</Text>
              </TouchableOpacity>
            ))}
          </View>

          {error ? (
            <View style={styles.errorBox}>
              <Ionicons name="alert-circle" size={16} color={Colors.error} />
              <Text style={styles.errorText}>{error}</Text>
            </View>
          ) : null}

          <Input
            label="Username"
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            autoCorrect={false}
            returnKeyType="next"
            leftIcon={<Ionicons name="person-outline" size={18} color={Colors.textMuted} />}
          />

          <View style={{ marginBottom: 20 }}>
            <Text style={styles.inputLabel}>Password</Text>
            <View style={styles.passWrap}>
              <Ionicons name="lock-closed-outline" size={18} color={Colors.textMuted} style={{ marginRight: 8 }} />
              <Input
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPass}
                returnKeyType="done"
                onSubmitEditing={handleLogin}
                containerStyle={{ flex: 1, marginBottom: 0 }}
                style={{ paddingLeft: 0 }}
              />
              <TouchableOpacity onPress={() => setShowPass(!showPass)} style={{ padding: 4 }}>
                <Ionicons name={showPass ? 'eye-off' : 'eye'} size={20} color={Colors.textMuted} />
              </TouchableOpacity>
            </View>
          </View>

          <Btn
            title={`Sign In as ${PORTALS.find(p => p.key === portal)?.label}`}
            onPress={handleLogin}
            loading={loading}
            size="lg"
            style={{ width: '100%' }}
          />

          <TouchableOpacity onPress={() => router.push('/(auth)/register')} style={styles.regLink}>
            <Text style={styles.regText}>Don't have an account? <Text style={{ color: Colors.red, fontWeight: '700' }}>Register here</Text></Text>
          </TouchableOpacity>
        </View>

        {/* Service times */}
        <View style={styles.times}>
          <Ionicons name="time-outline" size={14} color={Colors.gold} />
          <Text style={styles.timesText}>Sunday 9 AM · Wed Bible Study 6 PM · Fri Prayer 6 PM</Text>
        </View>

      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.black },
  content: { paddingBottom: 40 },
  brand: { alignItems: 'center', paddingTop: 70, paddingBottom: 30, paddingHorizontal: 20 },
  logoCircle: {
    width: 80, height: 80, borderRadius: 40,
    backgroundColor: 'rgba(201,162,39,0.15)',
    borderWidth: 2, borderColor: Colors.gold,
    alignItems: 'center', justifyContent: 'center', marginBottom: 14,
  },
  churchName: { fontSize: 22, fontWeight: '700', color: '#fff', textAlign: 'center' },
  churchSub: { fontSize: 13, color: 'rgba(255,255,255,0.65)', marginTop: 2 },
  churchTagline: { fontSize: 12, color: Colors.gold, fontStyle: 'italic', marginTop: 6 },
  card: { backgroundColor: '#fff', borderRadius: 20, marginHorizontal: 16, padding: 22, shadowColor: '#000', shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.2, shadowRadius: 20, elevation: 8 },
  cardTitle: { fontSize: 22, fontWeight: '700', color: Colors.black, marginBottom: 2 },
  cardSub: { fontSize: 13, color: Colors.textMuted, marginBottom: 18 },
  portalRow: { flexDirection: 'row', gap: 8, marginBottom: 18 },
  portalBtn: { flex: 1, borderWidth: 2, borderColor: Colors.border, borderRadius: 10, padding: 10, alignItems: 'center', gap: 3 },
  portalLabel: { fontSize: 12, fontWeight: '700', color: Colors.textMuted },
  portalDesc: { fontSize: 9, color: Colors.textMuted, textAlign: 'center' },
  errorBox: { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: '#fff5f5', borderRadius: 8, padding: 10, marginBottom: 14, borderWidth: 1, borderColor: '#fcc' },
  errorText: { flex: 1, fontSize: 13, color: Colors.error },
  inputLabel: { fontSize: 13, fontWeight: '600', color: Colors.textPrimary, marginBottom: 6 },
  passWrap: { flexDirection: 'row', alignItems: 'center', borderWidth: 1.5, borderColor: Colors.border, borderRadius: 10, paddingHorizontal: 14 },
  regLink: { marginTop: 18, alignItems: 'center' },
  regText: { fontSize: 13, color: Colors.textSecondary },
  times: { flexDirection: 'row', alignItems: 'center', gap: 6, justifyContent: 'center', marginTop: 20, paddingHorizontal: 20 },
  timesText: { fontSize: 12, color: 'rgba(255,255,255,0.5)', textAlign: 'center', flex: 1 },
});
