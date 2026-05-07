import React, { useState } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  TextInput, ActivityIndicator, FlatList,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ENDPOINTS } from '../../constants/Api';
import { Colors } from '../../constants/Colors';
import { HeroBanner, Card, Btn } from '../../components/UI';

const QUICK_REFS = [
  'John 3:16', 'Psalms 23', 'Romans 8:28', 'Proverbs 3:5-6',
  'Philippians 4:13', 'Isaiah 40:31', 'Jeremiah 29:11', 'Matthew 6:33',
];

const BOOKS = {
  OT: ['Genesis','Exodus','Leviticus','Numbers','Deuteronomy','Joshua','Judges','Ruth','1 Samuel','2 Samuel','1 Kings','2 Kings','1 Chronicles','2 Chronicles','Ezra','Nehemiah','Esther','Job','Psalms','Proverbs','Ecclesiastes','Song of Solomon','Isaiah','Jeremiah','Lamentations','Ezekiel','Daniel','Hosea','Joel','Amos','Obadiah','Jonah','Micah','Nahum','Habakkuk','Zephaniah','Haggai','Zechariah','Malachi'],
  NT: ['Matthew','Mark','Luke','John','Acts','Romans','1 Corinthians','2 Corinthians','Galatians','Ephesians','Philippians','Colossians','1 Thessalonians','2 Thessalonians','1 Timothy','2 Timothy','Titus','Philemon','Hebrews','James','1 Peter','2 Peter','1 John','2 John','3 John','Jude','Revelation'],
};

export default function BibleScreen() {
  const [query, setQuery] = useState('');
  const [verseData, setVerseData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showBooks, setShowBooks] = useState(false);
  const [activeTab, setActiveTab] = useState<'OT' | 'NT'>('NT');

  async function search(ref?: string) {
    const r = (ref || query).trim();
    if (!r) return;
    setLoading(true);
    setError('');
    setVerseData(null);
    setShowBooks(false);
    try {
      const resp = await fetch(`${ENDPOINTS.BIBLE}?ref=${encodeURIComponent(r)}`);
      const data = await resp.json();
      if (!resp.ok || data.error) throw new Error(data.error || 'Not found');
      setVerseData(data);
      if (ref) setQuery(ref);
    } catch (e: any) {
      setError(e.message || 'Could not fetch verse.');
    } finally { setLoading(false); }
  }

  async function copyText() {
    if (!verseData) return;
    const text = `${verseData.reference}\n\n${verseData.text}`;
    // Clipboard.setStringAsync(text);  // Uncomment after installing expo-clipboard
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Hero */}
      <View style={styles.hero}>
        <Ionicons name="book" size={32} color={Colors.gold} />
        <Text style={styles.heroTitle}>Holy Bible</Text>
        <Text style={styles.heroSub}>Read & search God's Word · World English Bible</Text>

        {/* Search bar */}
        <View style={styles.searchBar}>
          <Ionicons name="search" size={18} color={Colors.textMuted} style={{ marginRight: 8 }} />
          <TextInput
            style={styles.searchInput}
            value={query}
            onChangeText={setQuery}
            placeholder="John 3:16 · Psalms 23 · Romans 8"
            placeholderTextColor={Colors.textMuted}
            returnKeyType="search"
            onSubmitEditing={() => search()}
          />
          {query.length > 0 && (
            <TouchableOpacity onPress={() => { setQuery(''); setVerseData(null); setError(''); }}>
              <Ionicons name="close-circle" size={18} color={Colors.textMuted} />
            </TouchableOpacity>
          )}
        </View>
        <Btn title="Search" onPress={() => search()} loading={loading} variant="gold" size="md" style={{ alignSelf: 'center', paddingHorizontal: 32, marginTop: 10 }} />
      </View>

      <View style={styles.body}>
        {/* Quick refs */}
        <Text style={styles.sectionLabel}>Quick Passages</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.quickRow}>
          {QUICK_REFS.map(ref => (
            <TouchableOpacity key={ref} onPress={() => search(ref)} style={styles.quickChip}>
              <Text style={styles.quickChipText}>{ref}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Loading */}
        {loading && <ActivityIndicator size="large" color={Colors.red} style={{ marginTop: 30 }} />}

        {/* Error */}
        {error ? (
          <View style={styles.errorBox}>
            <Ionicons name="alert-circle" size={18} color={Colors.error} />
            <Text style={styles.errorText}>{error}</Text>
          </View>
        ) : null}

        {/* Verse result */}
        {verseData && (
          <Card style={styles.verseCard}>
            <View style={styles.verseHeader}>
              <View>
                <Text style={styles.verseRef}>{verseData.reference}</Text>
                <Text style={styles.verseTrans}>{verseData.translation_name || 'World English Bible'}</Text>
              </View>
              <TouchableOpacity onPress={copyText} style={styles.copyBtn}>
                <Ionicons name="copy-outline" size={18} color={Colors.red} />
              </TouchableOpacity>
            </View>
            <View style={styles.verseAccent} />
            <Text style={styles.verseText}>
              {verseData.verses
                ? verseData.verses.map((v: any) => `${v.verse} ${v.text} `).join('')
                : verseData.text}
            </Text>
          </Card>
        )}

        {/* Books browser */}
        <TouchableOpacity style={styles.booksToggle} onPress={() => setShowBooks(!showBooks)}>
          <Ionicons name="library-outline" size={18} color={Colors.red} />
          <Text style={styles.booksToggleText}>Browse All 66 Books</Text>
          <Ionicons name={showBooks ? 'chevron-up' : 'chevron-down'} size={18} color={Colors.textMuted} />
        </TouchableOpacity>

        {showBooks && (
          <View style={styles.booksPanel}>
            <View style={styles.tabRow}>
              {(['OT', 'NT'] as const).map(t => (
                <TouchableOpacity key={t} style={[styles.tab, activeTab === t && styles.tabActive]} onPress={() => setActiveTab(t)}>
                  <Text style={[styles.tabText, activeTab === t && styles.tabTextActive]}>
                    {t === 'OT' ? 'Old Testament (39)' : 'New Testament (27)'}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
            <View style={styles.booksGrid}>
              {BOOKS[activeTab].map(book => (
                <TouchableOpacity key={book} style={styles.bookBtn} onPress={() => search(`${book} 1`)}>
                  <Text style={styles.bookBtnText} numberOfLines={1}>{book}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  hero: { backgroundColor: Colors.black, paddingTop: 56, paddingBottom: 24, paddingHorizontal: 20, alignItems: 'center', gap: 6 },
  heroTitle: { fontSize: 26, fontWeight: '700', color: Colors.gold },
  heroSub: { fontSize: 13, color: 'rgba(255,255,255,0.6)', textAlign: 'center' },
  searchBar: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: 12, paddingHorizontal: 14, marginTop: 14, width: '100%' },
  searchInput: { flex: 1, paddingVertical: 13, fontSize: 15, color: Colors.textPrimary },
  body: { padding: 16, paddingBottom: 40 },
  sectionLabel: { fontSize: 12, fontWeight: '700', color: Colors.textMuted, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10 },
  quickRow: { gap: 8, paddingBottom: 4 },
  quickChip: { backgroundColor: '#fff', borderRadius: 20, paddingHorizontal: 14, paddingVertical: 8, borderWidth: 1.5, borderColor: Colors.border },
  quickChipText: { fontSize: 13, color: Colors.red, fontWeight: '600' },
  errorBox: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: '#fff5f5', borderRadius: 10, padding: 14, marginVertical: 12, borderWidth: 1, borderColor: '#fcc' },
  errorText: { flex: 1, color: Colors.error, fontSize: 13 },
  verseCard: { marginTop: 16 },
  verseHeader: { flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 10 },
  verseRef: { fontSize: 17, fontWeight: '700', color: Colors.red },
  verseTrans: { fontSize: 12, color: Colors.textMuted, marginTop: 2 },
  copyBtn: { padding: 4 },
  verseAccent: { height: 3, backgroundColor: Colors.gold, borderRadius: 2, marginBottom: 14, width: 50 },
  verseText: { fontSize: 17, lineHeight: 30, color: Colors.textPrimary, fontStyle: 'italic' },
  booksToggle: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: '#fff', borderRadius: 10, padding: 14, marginTop: 16, borderWidth: 1.5, borderColor: Colors.border },
  booksToggleText: { flex: 1, fontWeight: '600', color: Colors.textPrimary, fontSize: 14 },
  booksPanel: { backgroundColor: '#fff', borderRadius: 12, padding: 14, marginTop: 8 },
  tabRow: { flexDirection: 'row', gap: 8, marginBottom: 14 },
  tab: { flex: 1, paddingVertical: 8, borderRadius: 8, backgroundColor: Colors.background, alignItems: 'center' },
  tabActive: { backgroundColor: Colors.red },
  tabText: { fontSize: 12, fontWeight: '600', color: Colors.textMuted },
  tabTextActive: { color: '#fff' },
  booksGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  bookBtn: { paddingHorizontal: 10, paddingVertical: 7, backgroundColor: Colors.background, borderRadius: 8, borderWidth: 1, borderColor: Colors.border },
  bookBtnText: { fontSize: 12, color: Colors.textPrimary, maxWidth: 90 },
});
