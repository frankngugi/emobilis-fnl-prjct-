import React, { useState } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  KeyboardAvoidingView, Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { Colors } from '../../constants/Colors';
import { Btn, Input } from '../../components/UI';

export default function RegisterScreen() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({
    first_name: '', last_name: '', username: '',
    email: '', phone: '', password: '', confirm_password: '',
  });
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  function set(key: string) { return (v: string) => setForm(f => ({ ...f, [key]: v })); }

  // Password strength
  const strength = (() => {
    const p = form.password;
    let s = 0;
    if (p.length >= 8) s++;
    if (/[A-Z]/.test(p)) s++;
    if (/[0-9]/.test(p)) s++;
    if (/[^A-Za-z0-9]/.test(p)) s++;
    return s;
  })();
  const strengthColors = ['#e74c3c', '#e67e22', '#f1c40f', '#27ae60'];
  const strengthLabels = ['Weak', 'Fair', 'Good', 'Strong'];

  async function handleRegister() {
    if (!form.first_name || !form.username || !form.email || !form.password) {
      setError('Please fill in all required fields.');
      return;
    }
    if (form.password !== form.confirm_password) {
      setError('Passwords do not match.');
      return;
    }
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await register(form);
    } catch (e: any) {
      setError(e.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
            <Ionicons name="arrow-back" size={22} color="#fff" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Join RGC Nyahururu</Text>
          <Text style={styles.headerSub}>Create your church account</Text>
        </View>

        <View style={styles.card}>
          {error ? (
            <View style={styles.errorBox}>
              <Ionicons name="alert-circle" size={16} color={Colors.error} />
              <Text style={styles.errorText}>{error}</Text>
            </View>
          ) : null}

          <View style={styles.row}>
            <Input label="First Name *" value={form.first_name} onChangeText={set('first_name')} placeholder="First name" containerStyle={{ flex: 1 }} />
            <View style={{ width: 10 }} />
            <Input label="Last Name" value={form.last_name} onChangeText={set('last_name')} placeholder="Last name" containerStyle={{ flex: 1 }} />
          </View>

          <Input
            label="Username *"
            value={form.username}
            onChangeText={set('username')}
            autoCapitalize="none"
            autoCorrect={false}
            placeholder="Choose a username (min 4 chars)"
            leftIcon={<Ionicons name="person-outline" size={18} color={Colors.textMuted} />}
          />

          <Input
            label="Email Address *"
            value={form.email}
            onChangeText={set('email')}
            keyboardType="email-address"
            autoCapitalize="none"
            placeholder="your@email.com"
            leftIcon={<Ionicons name="mail-outline" size={18} color={Colors.textMuted} />}
          />

          <Input
            label="Phone (for M-Pesa & OTP)"
            value={form.phone}
            onChangeText={set('phone')}
            keyboardType="phone-pad"
            placeholder="0712 345 678"
            leftIcon={<Ionicons name="call-outline" size={18} color={Colors.textMuted} />}
          />

          <Input
            label="Password *"
            value={form.password}
            onChangeText={set('password')}
            secureTextEntry={!showPass}
            placeholder="Minimum 8 characters"
            leftIcon={<Ionicons name="lock-closed-outline" size={18} color={Colors.textMuted} />}
          />

          {/* Password strength bar */}
          {form.password.length > 0 && (
            <View style={{ marginTop: -8, marginBottom: 14 }}>
              <View style={styles.strengthBar}>
                {[0, 1, 2, 3].map(i => (
                  <View key={i} style={[styles.strengthSeg, { backgroundColor: i < strength ? strengthColors[strength - 1] : Colors.border }]} />
                ))}
              </View>
              <Text style={[styles.strengthLabel, { color: strengthColors[strength - 1] }]}>
                {strength > 0 ? strengthLabels[strength - 1] : ''}
              </Text>
            </View>
          )}

          <Input
            label="Confirm Password *"
            value={form.confirm_password}
            onChangeText={set('confirm_password')}
            secureTextEntry={!showPass}
            placeholder="Repeat password"
            leftIcon={<Ionicons name="lock-closed-outline" size={18} color={Colors.textMuted} />}
          />

          <TouchableOpacity onPress={() => setShowPass(!showPass)} style={styles.showPass}>
            <Ionicons name={showPass ? 'eye-off' : 'eye'} size={16} color={Colors.textMuted} />
            <Text style={styles.showPassText}>{showPass ? 'Hide' : 'Show'} passwords</Text>
          </TouchableOpacity>

          <View style={styles.benefits}>
            {['Access Bible, Hymns & Resources', 'Join Groups & Ministries', 'Register for Events', 'Give via M-Pesa'].map(b => (
              <View key={b} style={styles.benefit}>
                <Ionicons name="checkmark-circle" size={15} color={Colors.success} />
                <Text style={styles.benefitText}>{b}</Text>
              </View>
            ))}
          </View>

          <Btn title="Create Account" onPress={handleRegister} loading={loading} size="lg" style={{ width: '100%', marginTop: 8 }} />

          <TouchableOpacity onPress={() => router.back()} style={styles.loginLink}>
            <Text style={styles.loginText}>Already have an account? <Text style={{ color: Colors.red, fontWeight: '700' }}>Sign In</Text></Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.black },
  content: { paddingBottom: 40 },
  header: { paddingTop: 60, paddingBottom: 30, paddingHorizontal: 20 },
  backBtn: { marginBottom: 16 },
  headerTitle: { fontSize: 26, fontWeight: '700', color: Colors.gold },
  headerSub: { fontSize: 14, color: 'rgba(255,255,255,0.65)', marginTop: 4 },
  card: { backgroundColor: '#fff', borderRadius: 20, marginHorizontal: 16, padding: 22, shadowColor: '#000', shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.2, shadowRadius: 20, elevation: 8 },
  row: { flexDirection: 'row' },
  errorBox: { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: '#fff5f5', borderRadius: 8, padding: 10, marginBottom: 14, borderWidth: 1, borderColor: '#fcc' },
  errorText: { flex: 1, fontSize: 13, color: Colors.error },
  strengthBar: { flexDirection: 'row', gap: 4, marginBottom: 4 },
  strengthSeg: { flex: 1, height: 4, borderRadius: 2 },
  strengthLabel: { fontSize: 11, fontWeight: '600' },
  showPass: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: -4, marginBottom: 16 },
  showPassText: { fontSize: 13, color: Colors.textMuted },
  benefits: { backgroundColor: '#f9f9f9', borderRadius: 10, padding: 14, marginBottom: 16, gap: 6 },
  benefit: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  benefitText: { fontSize: 13, color: Colors.textSecondary },
  loginLink: { marginTop: 16, alignItems: 'center' },
  loginText: { fontSize: 13, color: Colors.textSecondary },
});
