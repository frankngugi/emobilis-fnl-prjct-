import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  TextInput, Modal, ScrollView, ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ENDPOINTS } from '../../constants/Api';
import { Colors } from '../../constants/Colors';

export default function HymnsScreen() {
  const [hymns, setHymns] = useState<any[]>([]);
  const [filtered, setFiltered] = useState<any[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<any>(null);
  const [fontSize, setFontSize] = useState(17);

  const fetchHymns = useCallback(async () => {
    try {
      const resp = await fetch(ENDPOINTS.HYMNS);
      if (resp.ok) {
        const data = await resp.json();
        const list = data.results || data;
        setHymns(list);
        setFiltered(list);
      }
    } catch (e) {} finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchHymns(); }, [fetchHymns]);

  useEffect(() => {
    if (!query) { setFiltered(hymns); return; }
    const q = query.toLowerCase();
    setFiltered(hymns.filter(h =>
      h.title.toLowerCase().includes(q) ||
      (h.author || '').toLowerCase().includes(q) ||
      String(h.number).includes(q)
    ));
  }, [query, hymns]);

  async function openHymn(hymn: any) {
    if (hymn.lyrics) { setSelected(hymn); return; }
    try {
      const resp = await fetch(`${ENDPOINTS.HYMNS}${hymn.id}/`);
      if (resp.ok) {
        const full = await resp.json();
        setSelected(full);
      }
    } catch (e) { setSelected(hymn); }
  }

  if (loading) {
    return <View style={styles.center}><ActivityIndicator size="large" color={Colors.red} /></View>;
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="musical-notes" size={26} color={Colors.gold} />
        <Text style={styles.headerTitle}>Hymns & Songs</Text>
        <Text style={styles.headerSub}>{hymns.length} hymns</Text>
      </View>

      {/* Search */}
      <View style={styles.searchWrap}>
        <Ionicons name="search" size={18} color={Colors.textMuted} style={{ marginRight: 8 }} />
        <TextInput
          style={styles.searchInput}
          value={query}
          onChangeText={setQuery}
          placeholder="Search by title, author, or number..."
          placeholderTextColor={Colors.textMuted}
        />
        {query.length > 0 && (
          <TouchableOpacity onPress={() => setQuery('')}>
            <Ionicons name="close-circle" size={18} color={Colors.textMuted} />
          </TouchableOpacity>
        )}
      </View>

      {/* List */}
      <FlatList
        data={filtered}
        keyExtractor={item => String(item.id)}
        contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 20 }}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.center}>
            <Ionicons name="musical-notes-outline" size={48} color={Colors.border} />
            <Text style={styles.emptyText}>No hymns found</Text>
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.hymnRow} onPress={() => openHymn(item)} activeOpacity={0.7}>
            <View style={styles.hymnNum}>
              <Text style={styles.hymnNumText}>#{item.number}</Text>
            </View>
            <View style={styles.hymnInfo}>
              <Text style={styles.hymnTitle}>{item.title}</Text>
              {item.author && <Text style={styles.hymnAuthor}>{item.author}</Text>}
            </View>
            <Ionicons name="chevron-forward" size={18} color={Colors.border} />
          </TouchableOpacity>
        )}
      />

      {/* Lyrics Modal */}
      <Modal visible={!!selected} animationType="slide" presentationStyle="pageSheet">
        <View style={styles.modal}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setSelected(null)} style={styles.closeBtn}>
              <Ionicons name="arrow-down" size={22} color={Colors.textPrimary} />
            </TouchableOpacity>
            <View style={{ flex: 1, marginHorizontal: 12 }}>
              <Text style={styles.modalNum}>Hymn #{selected?.number}</Text>
              <Text style={styles.modalTitle} numberOfLines={1}>{selected?.title}</Text>
            </View>
            <View style={styles.fontBtns}>
              <TouchableOpacity onPress={() => setFontSize(f => Math.max(12, f - 2))} style={styles.fontBtn}>
                <Text style={styles.fontBtnText}>A-</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={() => setFontSize(f => Math.min(26, f + 2))} style={styles.fontBtn}>
                <Text style={styles.fontBtnText}>A+</Text>
              </TouchableOpacity>
            </View>
          </View>
          {selected?.author && (
            <View style={styles.authorRow}>
              <Ionicons name="person-outline" size={14} color={Colors.textMuted} />
              <Text style={styles.authorText}>{selected.author}</Text>
            </View>
          )}
          <ScrollView style={styles.lyricsScroll} showsVerticalScrollIndicator={false}>
            <Text style={[styles.lyrics, { fontSize }]}>
              {selected?.lyrics || 'Lyrics not available.'}
            </Text>
          </ScrollView>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingTop: 40 },
  header: { backgroundColor: Colors.black, paddingTop: 56, paddingBottom: 18, paddingHorizontal: 20, flexDirection: 'row', alignItems: 'center', gap: 10 },
  headerTitle: { fontSize: 22, fontWeight: '700', color: Colors.gold, flex: 1 },
  headerSub: { fontSize: 12, color: 'rgba(255,255,255,0.5)' },
  searchWrap: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', margin: 14, borderRadius: 12, paddingHorizontal: 14, borderWidth: 1.5, borderColor: Colors.border },
  searchInput: { flex: 1, paddingVertical: 13, fontSize: 15, color: Colors.textPrimary },
  hymnRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 8, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 4, elevation: 1 },
  hymnNum: { backgroundColor: Colors.red, borderRadius: 8, paddingHorizontal: 10, paddingVertical: 6, marginRight: 12 },
  hymnNumText: { color: '#fff', fontWeight: '700', fontSize: 13 },
  hymnInfo: { flex: 1 },
  hymnTitle: { fontSize: 15, fontWeight: '600', color: Colors.textPrimary },
  hymnAuthor: { fontSize: 12, color: Colors.textMuted, marginTop: 2 },
  emptyText: { fontSize: 15, color: Colors.textMuted, marginTop: 10 },
  modal: { flex: 1, backgroundColor: '#fff' },
  modalHeader: { flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: Colors.border, paddingTop: 20 },
  closeBtn: { padding: 4 },
  modalNum: { fontSize: 11, color: Colors.red, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 1 },
  modalTitle: { fontSize: 18, fontWeight: '700', color: Colors.textPrimary },
  fontBtns: { flexDirection: 'row', gap: 6 },
  fontBtn: { borderWidth: 1, borderColor: Colors.border, borderRadius: 6, paddingHorizontal: 8, paddingVertical: 4 },
  fontBtnText: { fontSize: 13, color: Colors.textPrimary, fontWeight: '600' },
  authorRow: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 20, paddingVertical: 10, backgroundColor: '#f9f9f9', borderBottomWidth: 1, borderBottomColor: Colors.border },
  authorText: { fontSize: 13, color: Colors.textMuted },
  lyricsScroll: { flex: 1 },
  lyrics: { padding: 20, lineHeight: 34, color: Colors.textPrimary },
});
