import React, { useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput,
  ActivityIndicator, Modal, FlatList, Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ENDPOINTS } from '../../constants/Api';
import { Colors } from '../../constants/Colors';
import { Btn } from '../../components/UI';

const { width, height } = Dimensions.get('window');

const BOOKS_OT = ['Genesis','Exodus','Leviticus','Numbers','Deuteronomy','Joshua','Judges','Ruth','1 Samuel','2 Samuel','1 Kings','2 Kings','1 Chronicles','2 Chronicles','Ezra','Nehemiah','Esther','Job','Psalms','Proverbs','Ecclesiastes','Song of Solomon','Isaiah','Jeremiah','Lamentations','Ezekiel','Daniel','Hosea','Joel','Amos','Obadiah','Jonah','Micah','Nahum','Habakkuk','Zephaniah','Haggai','Zechariah','Malachi'];
const BOOKS_NT = ['Matthew','Mark','Luke','John','Acts','Romans','1 Corinthians','2 Corinthians','Galatians','Ephesians','Philippians','Colossians','1 Thessalonians','2 Thessalonians','1 Timothy','2 Timothy','Titus','Philemon','Hebrews','James','1 Peter','2 Peter','1 John','2 John','3 John','Jude','Revelation'];
const ALL_BOOKS = [...BOOKS_OT, ...BOOKS_NT];

const CHAPTERS: Record<string, number> = {
  Genesis:50,Exodus:40,Leviticus:27,Numbers:36,Deuteronomy:34,Joshua:24,Judges:21,Ruth:4,'1 Samuel':31,'2 Samuel':24,'1 Kings':22,'2 Kings':25,'1 Chronicles':29,'2 Chronicles':36,Ezra:10,Nehemiah:13,Esther:10,Job:42,Psalms:150,Proverbs:31,Ecclesiastes:12,'Song of Solomon':8,Isaiah:66,Jeremiah:52,Lamentations:5,Ezekiel:48,Daniel:12,Hosea:14,Joel:3,Amos:9,Obadiah:1,Jonah:4,Micah:7,Nahum:3,Habakkuk:3,Zephaniah:3,Haggai:2,Zechariah:14,Malachi:4,Matthew:28,Mark:16,Luke:24,John:21,Acts:28,Romans:16,'1 Corinthians':16,'2 Corinthians':13,Galatians:6,Ephesians:6,Philippians:4,Colossians:4,'1 Thessalonians':5,'2 Thessalonians':3,'1 Timothy':6,'2 Timothy':4,Titus:3,Philemon:1,Hebrews:13,James:5,'1 Peter':5,'2 Peter':3,'1 John':5,'2 John':1,'3 John':1,Jude:1,Revelation:22,
};

const QUICK_REFS = ['John 3:16','Psalms 23','Romans 8:28','Proverbs 3:5-6','Philippians 4:13','Isaiah 40:31','Hebrews 11:1'];

export default function BibleScreen() {
  const [query, setQuery] = useState('');
  const [verseData, setVerseData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentBook, setCurrentBook] = useState('');
  const [currentChapter, setCurrentChapter] = useState(1);

  // BCV selector state
  const [showBookPicker, setShowBookPicker] = useState(false);
  const [showChapPicker, setShowChapPicker] = useState(false);
  const [selBook, setSelBook] = useState('');
  const [selChap, setSelChap] = useState(0);
  const [activeTab, setActiveTab] = useState<'OT'|'NT'>('NT');

  // Projector mode
  const [projector, setProjector] = useState(false);
  const [projLight, setProjLight] = useState(false);
  const [projSize, setProjSize] = useState(26);

  async function fetchVerse(ref: string) {
    setLoading(true); setError(''); setVerseData(null);
    const parts = ref.match(/^(.+?)\s+(\d+)/);
    if (parts) { setCurrentBook(parts[1]); setCurrentChapter(parseInt(parts[2])); }
    try {
      const resp = await fetch(`${ENDPOINTS.BIBLE}?ref=${encodeURIComponent(ref)}`);
      const data = await resp.json();
      if (!resp.ok || data.error) throw new Error(data.error || 'Not found');
      setVerseData(data);
    } catch (e: any) {
      setError(e.message || 'Could not fetch verse.');
    } finally { setLoading(false); }
  }

  function selectBook(book: string) {
    setSelBook(book); setSelChap(0);
    setShowBookPicker(false);
    setTimeout(() => setShowChapPicker(true), 300);
  }

  function selectChap(chap: number) {
    setSelChap(chap); setShowChapPicker(false);
    fetchVerse(`${selBook} ${chap}`);
    setQuery(`${selBook} ${chap}`);
  }

  function navigate(delta: number) {
    if (!currentBook) return;
    const newChap = currentChapter + delta;
    const max = CHAPTERS[currentBook] || 1;
    if (newChap < 1 || newChap > max) return;
    fetchVerse(`${currentBook} ${newChap}`);
  }

  const verseText = verseData
    ? (verseData.verses ? verseData.verses.map((v: any) => v.text).join(' ') : verseData.text || '')
    : '';

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="book" size={22} color={Colors.gold} />
        <Text style={styles.headerTitle}>Holy Bible</Text>
        {verseData && (
          <TouchableOpacity onPress={() => setProjector(true)} style={styles.projBtn}>
            <Ionicons name="tv" size={16} color="#fff" />
            <Text style={styles.projBtnText}>Project</Text>
          </TouchableOpacity>
        )}
      </View>

      <ScrollView showsVerticalScrollIndicator={false}>
        {/* BCV Selectors */}
        <View style={styles.bcvRow}>
          <TouchableOpacity style={[styles.bcvBtn, {flex:2}]} onPress={() => setShowBookPicker(true)}>
            <Text style={styles.bcvText} numberOfLines={1}>{selBook || 'Select Book'}</Text>
            <Ionicons name="chevron-down" size={14} color={Colors.textMuted} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.bcvBtn} onPress={() => selBook && setShowChapPicker(true)} disabled={!selBook}>
            <Text style={[styles.bcvText, !selBook && {color:Colors.textMuted}]}>{selChap || 'Ch.'}</Text>
            <Ionicons name="chevron-down" size={14} color={Colors.textMuted} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.readBtn} onPress={() => selBook && selChap && fetchVerse(`${selBook} ${selChap}`)}>
            <Text style={styles.readBtnText}>Read</Text>
          </TouchableOpacity>
        </View>

        {/* Text search */}
        <View style={styles.searchRow}>
          <TextInput style={styles.searchInput} value={query} onChangeText={setQuery}
            placeholder="John 3:16 · Psalms 23 · Romans 8:28" placeholderTextColor={Colors.textMuted}
            returnKeyType="search" onSubmitEditing={() => query.trim() && fetchVerse(query.trim())} />
          <TouchableOpacity style={styles.searchBtn} onPress={() => query.trim() && fetchVerse(query.trim())}>
            <Ionicons name="search" size={18} color="#fff" />
          </TouchableOpacity>
        </View>

        {/* Quick refs */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.quickRow}>
          {QUICK_REFS.map(r => (
            <TouchableOpacity key={r} style={styles.quickChip} onPress={() => { setQuery(r); fetchVerse(r); }}>
              <Text style={styles.quickText}>{r}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Loading */}
        {loading && <ActivityIndicator size="large" color={Colors.red} style={{margin:24}} />}
        {!!error && <View style={styles.errorBox}><Text style={styles.errorText}>{error}</Text></View>}

        {/* Verse result */}
        {verseData && (
          <View style={styles.verseCard}>
            <View style={styles.verseHeaderRow}>
              <View>
                <Text style={styles.verseRef}>{verseData.reference}</Text>
                <Text style={styles.verseTrans}>{verseData.translation_name || 'World English Bible'}</Text>
              </View>
              <TouchableOpacity onPress={() => setProjector(true)} style={styles.projIconBtn}>
                <Ionicons name="tv-outline" size={20} color={Colors.red} />
              </TouchableOpacity>
            </View>
            <View style={styles.verseAccent} />
            <Text style={styles.verseText}>
              {verseData.verses
                ? verseData.verses.map((v: any) => `${v.verse} ${v.text} `).join('')
                : verseData.text}
            </Text>
            {/* Chapter navigation */}
            <View style={styles.navRow}>
              <TouchableOpacity style={styles.navBtn} onPress={() => navigate(-1)}>
                <Ionicons name="chevron-back" size={16} color={Colors.red} />
                <Text style={styles.navText}>Prev Ch.</Text>
              </TouchableOpacity>
              <Text style={styles.navLabel}>{currentBook} {currentChapter}</Text>
              <TouchableOpacity style={styles.navBtn} onPress={() => navigate(1)}>
                <Text style={styles.navText}>Next Ch.</Text>
                <Ionicons name="chevron-forward" size={16} color={Colors.red} />
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* Books browser */}
        <View style={styles.booksSection}>
          <Text style={styles.booksSectionTitle}>Browse All 66 Books</Text>
          <View style={styles.tabRow}>
            {(['OT','NT'] as const).map(t => (
              <TouchableOpacity key={t} style={[styles.tab, activeTab===t && styles.tabActive]} onPress={() => setActiveTab(t)}>
                <Text style={[styles.tabText, activeTab===t && styles.tabTextActive]}>
                  {t==='OT' ? 'Old Testament' : 'New Testament'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          <View style={styles.booksGrid}>
            {(activeTab==='OT' ? BOOKS_OT : BOOKS_NT).map(b => (
              <TouchableOpacity key={b} style={[styles.bookChip, activeTab==='NT' && styles.bookChipNT]}
                onPress={() => { fetchVerse(`${b} 1`); setQuery(`${b} 1`); setCurrentBook(b); setCurrentChapter(1); }}>
                <Text style={styles.bookChipText} numberOfLines={1}>{b}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </ScrollView>

      {/* ── Book Picker Modal ── */}
      <Modal visible={showBookPicker} animationType="slide" presentationStyle="pageSheet">
        <View style={styles.modal}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Select Book</Text>
            <TouchableOpacity onPress={() => setShowBookPicker(false)}>
              <Ionicons name="close" size={24} color={Colors.textPrimary} />
            </TouchableOpacity>
          </View>
          <View style={styles.tabRow}>
            {(['OT','NT'] as const).map(t => (
              <TouchableOpacity key={t} style={[styles.tab, activeTab===t && styles.tabActive]} onPress={() => setActiveTab(t)}>
                <Text style={[styles.tabText, activeTab===t && styles.tabTextActive]}>{t==='OT'?'Old Testament (39)':'New Testament (27)'}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <FlatList
            data={activeTab==='OT' ? BOOKS_OT : BOOKS_NT}
            keyExtractor={b => b}
            renderItem={({item:b}) => (
              <TouchableOpacity style={[styles.bookRow, selBook===b && styles.bookRowActive]} onPress={() => selectBook(b)}>
                <Text style={[styles.bookRowText, selBook===b && {color:Colors.red, fontWeight:'700'}]}>{b}</Text>
                {selBook===b && <Ionicons name="checkmark" size={18} color={Colors.red} />}
              </TouchableOpacity>
            )}
          />
        </View>
      </Modal>

      {/* ── Chapter Picker Modal ── */}
      <Modal visible={showChapPicker} animationType="slide" presentationStyle="pageSheet">
        <View style={styles.modal}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>{selBook} — Select Chapter</Text>
            <TouchableOpacity onPress={() => setShowChapPicker(false)}>
              <Ionicons name="close" size={24} color={Colors.textPrimary} />
            </TouchableOpacity>
          </View>
          <FlatList
            data={Array.from({length: CHAPTERS[selBook] || 1}, (_,i) => i+1)}
            keyExtractor={n => String(n)}
            numColumns={5}
            contentContainerStyle={{padding:16, gap:8}}
            columnWrapperStyle={{gap:8}}
            renderItem={({item:n}) => (
              <TouchableOpacity style={[styles.chapBtn, selChap===n && styles.chapBtnActive]}
                onPress={() => selectChap(n)}>
                <Text style={[styles.chapBtnText, selChap===n && {color:'#fff'}]}>{n}</Text>
              </TouchableOpacity>
            )}
          />
        </View>
      </Modal>

      {/* ── PROJECTOR MODE ── */}
      <Modal visible={projector} animationType="fade" statusBarTranslucent>
        <View style={[styles.projOverlay, projLight && styles.projLight]}>
          {/* Controls */}
          <View style={styles.projControls}>
            <TouchableOpacity style={styles.projCtrlBtn} onPress={() => setProjSize(s => Math.min(50, s+3))}>
              <Text style={[styles.projCtrlText, projLight && {color:'#333'}]}>A+</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.projCtrlBtn} onPress={() => setProjSize(s => Math.max(14, s-3))}>
              <Text style={[styles.projCtrlText, projLight && {color:'#333'}]}>A-</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.projCtrlBtn} onPress={() => setProjLight(v => !v)}>
              <Ionicons name={projLight ? 'moon' : 'sunny'} size={18} color={projLight ? '#333' : '#fff'} />
            </TouchableOpacity>
            <TouchableOpacity style={[styles.projCtrlBtn, {backgroundColor:'rgba(139,0,0,.6)'}]} onPress={() => setProjector(false)}>
              <Text style={styles.projCtrlText}>✕ Exit</Text>
            </TouchableOpacity>
          </View>

          {/* Content */}
          <ScrollView contentContainerStyle={styles.projContent}>
            <Text style={[styles.projRef, projLight && {color:'#8b0000'}]}>
              {verseData?.reference}
            </Text>
            <Text style={[styles.projText, {fontSize: projSize}, projLight && {color:'#1a1a1a'}]}>
              "{verseText}"
            </Text>
          </ScrollView>

          {/* Chapter nav */}
          <View style={styles.projNav}>
            <TouchableOpacity style={styles.projNavBtn} onPress={() => { navigate(-1); }}>
              <Ionicons name="chevron-back" size={28} color="#fff" />
            </TouchableOpacity>
            <Text style={[styles.projNavLabel, projLight && {color:'#333'}]}>
              {currentBook} {currentChapter}
            </Text>
            <TouchableOpacity style={styles.projNavBtn} onPress={() => { navigate(1); }}>
              <Ionicons name="chevron-forward" size={28} color="#fff" />
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {flex:1, backgroundColor:Colors.background},
  header: {backgroundColor:Colors.black, paddingTop:56, paddingBottom:14, paddingHorizontal:20, flexDirection:'row', alignItems:'center', gap:10},
  headerTitle: {fontSize:20, fontWeight:'700', color:Colors.gold, flex:1},
  projBtn: {flexDirection:'row', alignItems:'center', gap:4, backgroundColor:'rgba(201,162,39,.25)', borderRadius:20, paddingHorizontal:12, paddingVertical:6, borderWidth:1, borderColor:Colors.gold},
  projBtnText: {color:Colors.gold, fontSize:12, fontWeight:'700'},
  bcvRow: {flexDirection:'row', gap:8, padding:14, backgroundColor:'#fff', borderBottomWidth:1, borderBottomColor:Colors.border},
  bcvBtn: {flex:1, flexDirection:'row', alignItems:'center', justifyContent:'space-between', borderWidth:1.5, borderColor:Colors.border, borderRadius:10, paddingHorizontal:12, paddingVertical:10},
  bcvText: {fontSize:13, color:Colors.textPrimary, fontWeight:'600', flex:1},
  readBtn: {backgroundColor:Colors.red, borderRadius:10, paddingHorizontal:16, paddingVertical:10, justifyContent:'center'},
  readBtnText: {color:'#fff', fontWeight:'700', fontSize:13},
  searchRow: {flexDirection:'row', gap:8, paddingHorizontal:14, paddingBottom:10, paddingTop:6, backgroundColor:'#fff'},
  searchInput: {flex:1, borderWidth:1.5, borderColor:Colors.border, borderRadius:10, paddingHorizontal:14, paddingVertical:10, fontSize:14, color:Colors.textPrimary},
  searchBtn: {backgroundColor:Colors.red, borderRadius:10, paddingHorizontal:14, alignItems:'center', justifyContent:'center'},
  quickRow: {paddingHorizontal:14, paddingVertical:10, gap:8},
  quickChip: {paddingHorizontal:12, paddingVertical:7, backgroundColor:'#fff', borderRadius:20, borderWidth:1.5, borderColor:Colors.border},
  quickText: {fontSize:12, fontWeight:'600', color:Colors.red},
  errorBox: {backgroundColor:'#fff5f5', borderRadius:10, padding:14, margin:14, borderWidth:1, borderColor:'#fcc'},
  errorText: {color:Colors.error, fontSize:13},
  verseCard: {backgroundColor:'#fff', borderRadius:14, margin:14, padding:20, shadowColor:'#000', shadowOffset:{width:0,height:3}, shadowOpacity:.08, shadowRadius:10, elevation:3, borderLeftWidth:5, borderLeftColor:Colors.gold},
  verseHeaderRow: {flexDirection:'row', alignItems:'flex-start', justifyContent:'space-between', marginBottom:10},
  verseRef: {fontSize:17, fontWeight:'700', color:Colors.red},
  verseTrans: {fontSize:11, color:Colors.textMuted, marginTop:2},
  projIconBtn: {padding:4},
  verseAccent: {height:3, backgroundColor:Colors.gold, borderRadius:2, width:50, marginBottom:14},
  verseText: {fontSize:17, lineHeight:30, color:Colors.textPrimary, fontStyle:'italic'},
  navRow: {flexDirection:'row', alignItems:'center', justifyContent:'space-between', marginTop:16, paddingTop:12, borderTopWidth:1, borderTopColor:Colors.border},
  navBtn: {flexDirection:'row', alignItems:'center', gap:4, paddingVertical:6, paddingHorizontal:10},
  navText: {fontSize:12, color:Colors.red, fontWeight:'600'},
  navLabel: {fontSize:12, color:Colors.textMuted, fontWeight:'600'},
  booksSection: {padding:14},
  booksSectionTitle: {fontSize:14, fontWeight:'700', color:Colors.textPrimary, marginBottom:10},
  tabRow: {flexDirection:'row', gap:8, marginBottom:12, paddingHorizontal:14},
  tab: {flex:1, backgroundColor:Colors.background, borderRadius:8, paddingVertical:8, alignItems:'center'},
  tabActive: {backgroundColor:Colors.red},
  tabText: {fontSize:12, fontWeight:'600', color:Colors.textMuted},
  tabTextActive: {color:'#fff'},
  booksGrid: {flexDirection:'row', flexWrap:'wrap', gap:6},
  bookChip: {paddingHorizontal:10, paddingVertical:7, backgroundColor:'#fff', borderRadius:8, borderWidth:1, borderColor:Colors.border, maxWidth:110},
  bookChipNT: {borderColor:Colors.gold},
  bookChipText: {fontSize:11, color:Colors.textPrimary},
  modal: {flex:1, backgroundColor:'#fff'},
  modalHeader: {flexDirection:'row', alignItems:'center', justifyContent:'space-between', padding:18, borderBottomWidth:1, borderBottomColor:Colors.border, paddingTop:24},
  modalTitle: {fontSize:18, fontWeight:'700', color:Colors.textPrimary},
  bookRow: {flexDirection:'row', alignItems:'center', justifyContent:'space-between', padding:16, borderBottomWidth:1, borderBottomColor:Colors.background},
  bookRowActive: {backgroundColor:'#fff5f5'},
  bookRowText: {fontSize:15, color:Colors.textPrimary},
  chapBtn: {flex:1, aspectRatio:1, backgroundColor:Colors.background, borderRadius:10, alignItems:'center', justifyContent:'center', margin:2},
  chapBtnActive: {backgroundColor:Colors.red},
  chapBtnText: {fontSize:14, fontWeight:'700', color:Colors.textPrimary},
  // Projector
  projOverlay: {flex:1, backgroundColor:'#1a1a1a', paddingTop:50},
  projLight: {backgroundColor:'#ffffff'},
  projControls: {flexDirection:'row', gap:8, justifyContent:'flex-end', paddingHorizontal:16, paddingBottom:16},
  projCtrlBtn: {backgroundColor:'rgba(255,255,255,.12)', borderRadius:8, paddingHorizontal:12, paddingVertical:7},
  projCtrlText: {color:'#fff', fontSize:13, fontWeight:'700'},
  projContent: {flexGrow:1, alignItems:'center', justifyContent:'center', paddingHorizontal:30, paddingVertical:20},
  projRef: {fontSize:18, fontWeight:'700', color:Colors.gold, marginBottom:20, textAlign:'center', letterSpacing:.05},
  projText: {color:'rgba(255,255,255,.95)', lineHeight:1.7*26, textAlign:'center', fontStyle:'italic'},
  projNav: {flexDirection:'row', alignItems:'center', justifyContent:'space-between', paddingHorizontal:30, paddingBottom:40, paddingTop:16},
  projNavBtn: {width:56, height:56, borderRadius:28, backgroundColor:'rgba(201,162,39,.2)', borderWidth:2, borderColor:Colors.gold, alignItems:'center', justifyContent:'center'},
  projNavLabel: {fontSize:14, color:'rgba(255,255,255,.7)', fontWeight:'600'},
});
