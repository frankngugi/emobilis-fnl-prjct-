import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Image, Modal, Dimensions, ScrollView, RefreshControl } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { ENDPOINTS } from '../constants/Api';
import { Colors } from '../constants/Colors';
import { Loader, Empty } from '../components/UI';

const { width } = Dimensions.get('window');
const IMG_SIZE = (width - 48) / 3;

export default function GalleryScreen() {
  const router = useRouter();
  const [images, setImages] = useState<any[]>([]);
  const [categories, setCategories] = useState<[string, string][]>([]);
  const [activeCat, setActiveCat] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selected, setSelected] = useState<any>(null);

  const fetch_ = async () => {
    try {
      const url = activeCat ? `${ENDPOINTS.GALLERY}?cat=${activeCat}` : ENDPOINTS.GALLERY;
      const resp = await fetch(url);
      if (resp.ok) {
        const d = await resp.json();
        setImages(d.results || d);
        if (d.categories) setCategories(d.categories);
      }
    } catch (e) {} finally { setLoading(false); setRefreshing(false); }
  };

  useEffect(() => { fetch_(); }, [activeCat]);

  if (loading) return <Loader message="Loading gallery..." />;

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 10 }}>
          <Ionicons name="arrow-back" size={22} color="#fff" />
        </TouchableOpacity>
        <Ionicons name="images" size={22} color={Colors.gold} />
        <Text style={styles.title}>Photo Gallery</Text>
        <Text style={styles.count}>{images.length} photos</Text>
      </View>

      {/* Filter */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filterRow}>
        <TouchableOpacity style={[styles.chip, !activeCat && styles.chipActive]} onPress={() => setActiveCat('')}>
          <Text style={[styles.chipText, !activeCat && styles.chipTextActive]}>All</Text>
        </TouchableOpacity>
        {categories.map(([val, label]) => (
          <TouchableOpacity key={val} style={[styles.chip, activeCat === val && styles.chipActive]} onPress={() => setActiveCat(val)}>
            <Text style={[styles.chipText, activeCat === val && styles.chipTextActive]}>{label}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Grid */}
      {images.length === 0 ? (
        <Empty title="No photos yet" subtitle={activeCat ? 'No photos in this category.' : 'Gallery is empty.'} />
      ) : (
        <FlatList
          data={images}
          numColumns={3}
          keyExtractor={i => String(i.id)}
          contentContainerStyle={{ padding: 14, gap: 4 }}
          columnWrapperStyle={{ gap: 4 }}
          showsVerticalScrollIndicator={false}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetch_(); }} tintColor={Colors.gold} />}
          renderItem={({ item }) => (
            <TouchableOpacity onPress={() => setSelected(item)} activeOpacity={0.85}>
              {item.image_url ? (
                <Image source={{ uri: item.image_url }} style={[styles.thumb, { width: IMG_SIZE, height: IMG_SIZE }]} />
              ) : (
                <View style={[styles.thumb, { width: IMG_SIZE, height: IMG_SIZE, backgroundColor: '#ddd', alignItems: 'center', justifyContent: 'center' }]}>
                  <Ionicons name="image-outline" size={28} color="#aaa" />
                </View>
              )}
            </TouchableOpacity>
          )}
        />
      )}

      {/* Full screen viewer */}
      <Modal visible={!!selected} transparent animationType="fade">
        <View style={styles.viewer}>
          <TouchableOpacity style={styles.closeViewer} onPress={() => setSelected(null)}>
            <Ionicons name="close" size={28} color="#fff" />
          </TouchableOpacity>
          {selected?.image_url && (
            <Image source={{ uri: selected.image_url }} style={styles.fullImg} resizeMode="contain" />
          )}
          <View style={styles.viewerInfo}>
            <Text style={styles.viewerTitle}>{selected?.title}</Text>
            <Text style={styles.viewerCat}>{selected?.category_display}</Text>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  header: { backgroundColor: Colors.black, paddingTop: 56, paddingBottom: 16, paddingHorizontal: 20, flexDirection: 'row', alignItems: 'center', gap: 10 },
  title: { fontSize: 20, fontWeight: '700', color: Colors.gold, flex: 1 },
  count: { fontSize: 12, color: 'rgba(255,255,255,0.5)' },
  filterRow: { paddingHorizontal: 14, paddingVertical: 10, gap: 8 },
  chip: { paddingHorizontal: 14, paddingVertical: 7, borderRadius: 20, borderWidth: 1.5, borderColor: Colors.border, backgroundColor: '#fff' },
  chipActive: { backgroundColor: Colors.red, borderColor: Colors.red },
  chipText: { fontSize: 12, fontWeight: '600', color: Colors.textMuted },
  chipTextActive: { color: '#fff' },
  thumb: { borderRadius: 6, backgroundColor: '#eee' },
  viewer: { flex: 1, backgroundColor: 'rgba(0,0,0,0.95)', alignItems: 'center', justifyContent: 'center' },
  closeViewer: { position: 'absolute', top: 56, right: 20, zIndex: 10 },
  fullImg: { width: '100%', height: '75%' },
  viewerInfo: { position: 'absolute', bottom: 40, left: 0, right: 0, alignItems: 'center', gap: 4 },
  viewerTitle: { fontSize: 16, fontWeight: '700', color: '#fff', textAlign: 'center' },
  viewerCat: { fontSize: 13, color: Colors.gold },
});
