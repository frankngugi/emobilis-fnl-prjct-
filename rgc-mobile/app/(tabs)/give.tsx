import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  Alert, FlatList, KeyboardAvoidingView, Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { ENDPOINTS } from '../../constants/Api';
import { Colors } from '../../constants/Colors';
import { Input, Btn, Card, SectionHeader, Badge } from '../../components/UI';

const PURPOSES = [
  { key: 'tithe', label: 'Tithe', icon: 'hand-right', desc: '10% of your income' },
  { key: 'offering', label: 'Offering', icon: 'gift', desc: 'Free-will offering' },
  { key: 'project', label: 'Project/Harambee', icon: 'construct', desc: 'Church development' },
  { key: 'other', label: 'Other', icon: 'ellipsis-horizontal', desc: 'Other giving' },
];

const PRESETS = [100, 500, 1000, 2000, 5000];

export default function GiveScreen() {
  const { user, token } = useAuth();
  const [phone, setPhone] = useState(user?.phone || '');
  const [amount, setAmount] = useState('');
  const [purpose, setPurpose] = useState('offering');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    if (token) fetchHistory();
  }, [token]);

  async function fetchHistory() {
    try {
      const resp = await fetch(ENDPOINTS.PAYMENTS, { headers: { Authorization: `Bearer ${token}` } });
      if (resp.ok) {
        const data = await resp.json();
        setHistory((data.results || data).slice(0, 10));
      }
    } catch (e) {}
  }

  async function handleGive() {
    if (!phone.trim()) { Alert.alert('Required', 'Please enter your M-Pesa phone number.'); return; }
    if (!amount || parseFloat(amount) < 10) { Alert.alert('Required', 'Please enter an amount of at least KES 10.'); return; }
    setLoading(true);
    try {
      const resp = await fetch(ENDPOINTS.PAY, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({ phone_number: phone.trim(), amount: parseFloat(amount), purpose }),
      });
      const data = await resp.json();
      if (resp.ok) {
        Alert.alert('STK Push Sent', data.message || 'Check your phone to complete the payment.', [{ text: 'OK', onPress: () => { setAmount(''); fetchHistory(); } }]);
      } else {
        Alert.alert('Payment Failed', data.message || 'Please try again.');
      }
    } catch (e) {
      Alert.alert('Error', 'Network error. Please check your connection.');
    } finally { setLoading(false); }
  }

  const statusColor: Record<string, string> = {
    completed: Colors.success,
    pending: Colors.warning,
    failed: Colors.error,
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
        {/* Hero */}
        <View style={styles.hero}>
          <Ionicons name="heart" size={30} color={Colors.gold} />
          <Text style={styles.heroTitle}>Give & Contribute</Text>
          <Text style={styles.heroSub}>Support God's work at RGC Nyahururu</Text>
          <Text style={styles.scripture}>"Each of you should give what you have decided in your heart to give, not reluctantly or under compulsion, for God loves a cheerful giver." — 2 Cor 9:7</Text>
        </View>

        <View style={styles.body}>
          {/* Form */}
          <Card>
            <View style={styles.cardHeader}>
              <Text style={styles.mpesaM}>M</Text>
              <Text style={styles.cardTitle}>Pay via M-Pesa STK Push</Text>
            </View>
            <Text style={styles.cardSub}>You'll receive a prompt on your phone to confirm payment</Text>

            {/* Phone */}
            <Input
              label="M-Pesa Phone Number"
              value={phone}
              onChangeText={setPhone}
              keyboardType="phone-pad"
              placeholder="e.g. 0712 345 678"
              leftIcon={<Ionicons name="call-outline" size={18} color={Colors.textMuted} />}
            />

            {/* Amount presets */}
            <Text style={styles.fieldLabel}>Amount (KES)</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.presets}>
              {PRESETS.map(p => (
                <TouchableOpacity key={p} style={[styles.preset, amount === String(p) && styles.presetActive]} onPress={() => setAmount(String(p))}>
                  <Text style={[styles.presetText, amount === String(p) && styles.presetTextActive]}>{p.toLocaleString()}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
            <Input
              value={amount}
              onChangeText={setAmount}
              keyboardType="numeric"
              placeholder="Or enter custom amount"
              containerStyle={{ marginTop: 8 }}
              leftIcon={<Ionicons name="cash-outline" size={18} color={Colors.textMuted} />}
            />

            {/* Purpose */}
            <Text style={styles.fieldLabel}>Type of Giving</Text>
            <View style={styles.purposeGrid}>
              {PURPOSES.map(p => (
                <TouchableOpacity
                  key={p.key}
                  style={[styles.purposeBtn, purpose === p.key && styles.purposeActive]}
                  onPress={() => setPurpose(p.key)}
                  activeOpacity={0.8}
                >
                  <Ionicons name={p.icon as any} size={22} color={purpose === p.key ? Colors.red : Colors.textMuted} />
                  <Text style={[styles.purposeLabel, purpose === p.key && { color: Colors.red }]}>{p.label}</Text>
                  <Text style={styles.purposeDesc}>{p.desc}</Text>
                </TouchableOpacity>
              ))}
            </View>

            <Btn
              title="Send STK Push to My Phone"
              onPress={handleGive}
              loading={loading}
              size="lg"
              style={{ width: '100%', marginTop: 12 }}
              icon={<Ionicons name="phone-portrait" size={18} color="#fff" />}
            />
            <Text style={styles.secureNote}>
              <Ionicons name="shield-checkmark" size={12} color={Colors.success} /> Secure payment via Safaricom Daraja API
            </Text>
          </Card>

          {/* Bank Transfer */}
          <Card style={{ marginTop: 4 }}>
            <Text style={styles.bankTitle}><Ionicons name="business" size={16} color={Colors.textPrimary} /> Bank Transfer</Text>
            {[
              ['Bank', 'Co-operative Bank'],
              ['Account Name', 'Redeemed Gospel Church'],
              ['Account No.', '01129xxxxxxx'],
              ['Branch', 'Nyahururu Branch'],
            ].map(([label, value]) => (
              <View key={label} style={styles.bankRow}>
                <Text style={styles.bankLabel}>{label}</Text>
                <Text style={styles.bankValue}>{value}</Text>
              </View>
            ))}
          </Card>

          {/* Payment history */}
          {history.length > 0 && (
            <>
              <SectionHeader title="My Contributions" style={{ marginTop: 8 }} />
              {history.map(p => (
                <View key={p.id} style={styles.histRow}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.histPurpose}>{p.purpose_display}</Text>
                    <Text style={styles.histPhone}>{p.phone_number}</Text>
                  </View>
                  <View style={{ alignItems: 'flex-end' }}>
                    <Text style={styles.histAmount}>KES {p.amount}</Text>
                    <Badge label={p.status} color={statusColor[p.status] || Colors.border} size="sm" />
                  </View>
                </View>
              ))}
            </>
          )}
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  hero: { backgroundColor: Colors.black, paddingTop: 56, paddingBottom: 24, paddingHorizontal: 20, alignItems: 'center', gap: 8 },
  heroTitle: { fontSize: 24, fontWeight: '700', color: Colors.gold },
  heroSub: { fontSize: 13, color: 'rgba(255,255,255,0.65)' },
  scripture: { fontSize: 12, color: 'rgba(255,255,255,0.5)', fontStyle: 'italic', textAlign: 'center', marginTop: 4 },
  body: { padding: 16, paddingBottom: 40 },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 4 },
  mpesaM: { fontSize: 22, fontWeight: '700', color: Colors.success, backgroundColor: '#f0fff4', width: 36, height: 36, borderRadius: 8, textAlign: 'center', lineHeight: 36 },
  cardTitle: { fontSize: 16, fontWeight: '700', color: Colors.textPrimary },
  cardSub: { fontSize: 13, color: Colors.textMuted, marginBottom: 16 },
  fieldLabel: { fontSize: 13, fontWeight: '600', color: Colors.textPrimary, marginBottom: 8 },
  presets: { gap: 8, paddingBottom: 4 },
  preset: { paddingHorizontal: 16, paddingVertical: 9, borderRadius: 20, borderWidth: 2, borderColor: Colors.border, backgroundColor: '#fff' },
  presetActive: { borderColor: Colors.red, backgroundColor: '#fff5f5' },
  presetText: { fontSize: 13, fontWeight: '700', color: Colors.textMuted },
  presetTextActive: { color: Colors.red },
  purposeGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 8 },
  purposeBtn: { width: '48%', borderWidth: 2, borderColor: Colors.border, borderRadius: 10, padding: 12, alignItems: 'center', gap: 4, backgroundColor: '#fff' },
  purposeActive: { borderColor: Colors.red, backgroundColor: '#fff5f5' },
  purposeLabel: { fontSize: 13, fontWeight: '700', color: Colors.textMuted },
  purposeDesc: { fontSize: 10, color: Colors.textMuted, textAlign: 'center' },
  secureNote: { textAlign: 'center', fontSize: 12, color: Colors.textMuted, marginTop: 10 },
  bankTitle: { fontSize: 15, fontWeight: '700', color: Colors.textPrimary, marginBottom: 12 },
  bankRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: Colors.border },
  bankLabel: { fontSize: 13, color: Colors.textMuted },
  bankValue: { fontSize: 13, fontWeight: '600', color: Colors.textPrimary },
  histRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: 10, padding: 14, marginBottom: 8 },
  histPurpose: { fontSize: 14, fontWeight: '600', color: Colors.textPrimary },
  histPhone: { fontSize: 12, color: Colors.textMuted, marginTop: 2 },
  histAmount: { fontSize: 15, fontWeight: '700', color: Colors.textPrimary, marginBottom: 4 },
});
