import React, { useEffect, useState, useRef, useCallback } from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  TextInput, KeyboardAvoidingView, Platform, Linking,
  ActivityIndicator, ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { ENDPOINTS, CHURCH_WA_LINK } from '../../constants/Api';
import { Colors } from '../../constants/Colors';

interface ChatRoom { id: number; name: string; room_type: string; description: string; last_message?: any; }
interface Message { id: number; sender: string; avatar_letter: string; message: string; time: string; mine: boolean; }

const ROOM_ICONS: Record<string, any> = {
  general: 'chatbubbles', prayer: 'heart', group: 'people', announcements: 'megaphone',
};
const ROOM_COLORS: Record<string, string> = {
  general: '#1976d2', prayer: '#7b1fa2', group: '#388e3c', announcements: '#f57c00',
};

export default function ChatScreen() {
  const { token, user } = useAuth();
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [activeRoom, setActiveRoom] = useState<ChatRoom | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [loadingRooms, setLoadingRooms] = useState(true);
  const [loadingMsgs, setLoadingMsgs] = useState(false);
  const flatListRef = useRef<FlatList>(null);
  const lastMsgId = useRef(0);
  const pollTimer = useRef<ReturnType<typeof setInterval>>();

  // Load rooms
  useEffect(() => {
    if (!token) { setLoadingRooms(false); return; }
    fetch(ENDPOINTS.CHAT_ROOMS, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { setRooms(data); if (data.length > 0) openRoom(data[0]); })
      .catch(() => {})
      .finally(() => setLoadingRooms(false));
  }, [token]);

  const openRoom = useCallback(async (room: ChatRoom) => {
    setActiveRoom(room);
    setLoadingMsgs(true);
    setMessages([]);
    lastMsgId.current = 0;
    clearInterval(pollTimer.current);
    try {
      const resp = await fetch(ENDPOINTS.CHAT_MESSAGES(room.id), { headers: { Authorization: `Bearer ${token}` } });
      if (resp.ok) {
        const data = await resp.json();
        setMessages(data.messages || []);
        if (data.messages?.length > 0) lastMsgId.current = data.messages[data.messages.length - 1].id;
        setTimeout(() => flatListRef.current?.scrollToEnd({ animated: false }), 100);
      }
    } catch (e) {}
    setLoadingMsgs(false);
    // Poll for new messages
    pollTimer.current = setInterval(() => pollMessages(room.id), 4000);
  }, [token]);

  const pollMessages = async (roomId: number) => {
    try {
      const resp = await fetch(`${ENDPOINTS.CHAT_MESSAGES(roomId)}?since=${lastMsgId.current}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.messages?.length > 0) {
          setMessages(prev => [...prev, ...data.messages]);
          lastMsgId.current = data.messages[data.messages.length - 1].id;
          setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100);
        }
      }
    } catch (e) {}
  };

  useEffect(() => () => clearInterval(pollTimer.current), []);

  const sendMessage = async () => {
    if (!input.trim() || !activeRoom || !token) return;
    setSending(true);
    const text = input.trim();
    setInput('');
    try {
      const resp = await fetch(ENDPOINTS.CHAT_SEND(activeRoom.id), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message: text }),
      });
      if (resp.ok) {
        const msg = await resp.json();
        setMessages(prev => [...prev, msg]);
        lastMsgId.current = msg.id;
        setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100);
      }
    } catch (e) { setInput(text); }
    setSending(false);
  };

  if (!user) {
    return (
      <View style={styles.center}>
        <Ionicons name="lock-closed" size={48} color={Colors.border} />
        <Text style={styles.emptyText}>Login to join the community chat</Text>
        <TouchableOpacity style={styles.loginBtn} onPress={() => {}}>
          <Text style={styles.loginBtnText}>Login / Sign Up</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Room List */}
      <View style={styles.sidebar}>
        <View style={styles.sidebarHeader}>
          <Text style={styles.sidebarTitle}>Community</Text>
          <TouchableOpacity onPress={() => Linking.openURL(CHURCH_WA_LINK)} style={styles.waBtn}>
            <Ionicons name="logo-whatsapp" size={14} color="#fff" />
            <Text style={styles.waBtnText}>Church</Text>
          </TouchableOpacity>
        </View>
        {loadingRooms ? <ActivityIndicator style={{ margin: 20 }} color={Colors.red} /> : (
          <ScrollView showsVerticalScrollIndicator={false}>
            {rooms.map(room => (
              <TouchableOpacity key={room.id} style={[styles.roomItem, activeRoom?.id === room.id && styles.roomActive]} onPress={() => openRoom(room)}>
                <View style={[styles.roomIcon, { backgroundColor: `${ROOM_COLORS[room.room_type] || Colors.red}20` }]}>
                  <Ionicons name={ROOM_ICONS[room.room_type] || 'chatbubble'} size={18} color={ROOM_COLORS[room.room_type] || Colors.red} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={[styles.roomName, activeRoom?.id === room.id && { color: Colors.red }]} numberOfLines={1}>{room.name}</Text>
                  {room.last_message && <Text style={styles.roomPreview} numberOfLines={1}>{room.last_message.text}</Text>}
                </View>
              </TouchableOpacity>
            ))}
          </ScrollView>
        )}
      </View>

      {/* Chat Area */}
      <KeyboardAvoidingView style={styles.chatArea} behavior={Platform.OS === 'ios' ? 'padding' : undefined} keyboardVerticalOffset={90}>
        {/* Header */}
        <View style={styles.chatHeader}>
          <View style={{ flex: 1 }}>
            <Text style={styles.chatTitle}>{activeRoom?.name || 'Select a room'}</Text>
            {activeRoom && <Text style={styles.chatDesc}>{activeRoom.description}</Text>}
          </View>
          {activeRoom && (
            <TouchableOpacity
              onPress={() => Linking.openURL(`https://wa.me/254712760740?text=From%20RGC%20${encodeURIComponent(activeRoom.name)}:%20`)}
              style={styles.waShareBtn}
            >
              <Ionicons name="logo-whatsapp" size={16} color="#fff" />
              <Text style={styles.waShareText}>Share</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Messages */}
        {loadingMsgs ? <ActivityIndicator style={{ flex: 1 }} color={Colors.red} /> : (
          <FlatList
            ref={flatListRef}
            data={messages}
            keyExtractor={m => String(m.id)}
            contentContainerStyle={styles.messagesList}
            showsVerticalScrollIndicator={false}
            ListEmptyComponent={
              <View style={styles.emptyChat}>
                <Ionicons name="chatbubbles-outline" size={48} color={Colors.border} />
                <Text style={styles.emptyText}>No messages yet. Say hello!</Text>
              </View>
            }
            renderItem={({ item: m }) => (
              <View style={[styles.msgRow, m.mine && styles.msgRowMine]}>
                {!m.mine && (
                  <View style={styles.avatar}>
                    <Text style={styles.avatarText}>{m.avatar_letter}</Text>
                  </View>
                )}
                <View style={[styles.bubble, m.mine && styles.bubbleMine]}>
                  {!m.mine && <Text style={styles.senderName}>{m.sender}</Text>}
                  <Text style={[styles.msgText, m.mine && styles.msgTextMine]}>{m.message}</Text>
                  <Text style={[styles.msgTime, m.mine && styles.msgTimeMine]}>
                    {new Date(m.time).toLocaleTimeString('en-KE', { hour: '2-digit', minute: '2-digit' })}
                  </Text>
                </View>
                {m.mine && (
                  <View style={[styles.avatar, styles.avatarMine]}>
                    <Text style={styles.avatarText}>{m.avatar_letter}</Text>
                  </View>
                )}
              </View>
            )}
          />
        )}

        {/* Input */}
        {activeRoom && (
          <View style={styles.inputArea}>
            <TextInput
              style={styles.input}
              value={input}
              onChangeText={setInput}
              placeholder="Type a message..."
              placeholderTextColor={Colors.textMuted}
              multiline
              maxLength={1000}
              returnKeyType="send"
              onSubmitEditing={sendMessage}
            />
            <TouchableOpacity onPress={sendMessage} disabled={sending || !input.trim()} style={[styles.sendBtn, (!input.trim() || sending) && { opacity: 0.5 }]}>
              {sending ? <ActivityIndicator size="small" color="#fff" /> : <Ionicons name="send" size={18} color="#fff" />}
            </TouchableOpacity>
          </View>
        )}
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, flexDirection: 'row', backgroundColor: Colors.background },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 14, padding: 24 },
  sidebar: { width: 80, backgroundColor: '#fff', borderRightWidth: 1, borderRightColor: Colors.border },
  sidebarHeader: { backgroundColor: Colors.black, padding: 10, alignItems: 'center', gap: 6 },
  sidebarTitle: { color: Colors.gold, fontSize: 9, fontWeight: '700', textAlign: 'center' },
  waBtn: { backgroundColor: '#25D366', borderRadius: 10, padding: 4, flexDirection: 'row', alignItems: 'center', gap: 2 },
  waBtnText: { color: '#fff', fontSize: 9, fontWeight: '700' },
  roomItem: { padding: 10, alignItems: 'center', gap: 4, borderBottomWidth: 1, borderBottomColor: Colors.background },
  roomActive: { backgroundColor: '#fff5f5' },
  roomIcon: { width: 40, height: 40, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  roomName: { fontSize: 9, fontWeight: '700', color: Colors.textPrimary, textAlign: 'center' },
  roomPreview: { fontSize: 8, color: Colors.textMuted, textAlign: 'center' },
  chatArea: { flex: 1, flexDirection: 'column' },
  chatHeader: { backgroundColor: '#fff', padding: 12, flexDirection: 'row', alignItems: 'center', borderBottomWidth: 1, borderBottomColor: Colors.border },
  chatTitle: { fontSize: 15, fontWeight: '700', color: Colors.textPrimary },
  chatDesc: { fontSize: 11, color: Colors.textMuted, marginTop: 1 },
  waShareBtn: { backgroundColor: '#25D366', borderRadius: 20, paddingHorizontal: 12, paddingVertical: 6, flexDirection: 'row', alignItems: 'center', gap: 4 },
  waShareText: { color: '#fff', fontSize: 12, fontWeight: '700' },
  messagesList: { padding: 14, gap: 10, paddingBottom: 8 },
  emptyChat: { alignItems: 'center', paddingTop: 60, gap: 10 },
  emptyText: { color: Colors.textMuted, fontSize: 14, textAlign: 'center' },
  loginBtn: { backgroundColor: Colors.red, paddingHorizontal: 24, paddingVertical: 12, borderRadius: 10 },
  loginBtnText: { color: '#fff', fontWeight: '700' },
  msgRow: { flexDirection: 'row', gap: 8, alignItems: 'flex-end' },
  msgRowMine: { flexDirection: 'row-reverse' },
  avatar: { width: 30, height: 30, borderRadius: 15, backgroundColor: Colors.red, alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
  avatarMine: { backgroundColor: Colors.gold },
  avatarText: { fontSize: 12, fontWeight: '700', color: '#fff' },
  bubble: { maxWidth: '70%', backgroundColor: '#fff', borderRadius: 16, padding: 10, borderBottomLeftRadius: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 3, elevation: 1 },
  bubbleMine: { backgroundColor: Colors.red, borderBottomLeftRadius: 16, borderBottomRightRadius: 4 },
  senderName: { fontSize: 10, fontWeight: '700', color: Colors.red, marginBottom: 2 },
  msgText: { fontSize: 14, color: Colors.textPrimary, lineHeight: 20 },
  msgTextMine: { color: '#fff' },
  msgTime: { fontSize: 10, color: Colors.textMuted, marginTop: 3, textAlign: 'right' },
  msgTimeMine: { color: 'rgba(255,255,255,0.6)' },
  inputArea: { flexDirection: 'row', gap: 8, padding: 12, backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: Colors.border, alignItems: 'flex-end' },
  input: { flex: 1, borderWidth: 1.5, borderColor: Colors.border, borderRadius: 20, paddingHorizontal: 16, paddingVertical: 10, fontSize: 14, color: Colors.textPrimary, maxHeight: 120 },
  sendBtn: { width: 42, height: 42, borderRadius: 21, backgroundColor: Colors.red, alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
});
