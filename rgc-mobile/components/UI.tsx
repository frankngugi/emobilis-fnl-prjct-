import React from 'react';
import {
  View, Text, TouchableOpacity, ActivityIndicator, StyleSheet,
  ViewStyle, TextStyle, ImageBackground
} from 'react-native';
import { Colors } from '../constants/Colors';

// ── Button ────────────────────────────────────────────────────────────────────

interface BtnProps {
  title: string;
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
  variant?: 'primary' | 'gold' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  style?: ViewStyle;
}

export function Btn({ title, onPress, loading, disabled, variant = 'primary', size = 'md', icon, style }: BtnProps) {
  const bgMap = {
    primary: Colors.red,
    gold: Colors.gold,
    outline: 'transparent',
    ghost: 'transparent',
    danger: '#e74c3c',
  };
  const txtMap = {
    primary: '#fff',
    gold: '#1a1a1a',
    outline: Colors.red,
    ghost: Colors.textSecondary,
    danger: '#fff',
  };
  const sizeMap = { sm: 10, md: 14, lg: 18 };
  const padMap = { sm: [8, 16], md: [13, 20], lg: [17, 28] };
  const pad = padMap[size];

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      style={[
        styles.btn,
        {
          backgroundColor: bgMap[variant],
          paddingVertical: pad[0],
          paddingHorizontal: pad[1],
          borderWidth: variant === 'outline' ? 2 : 0,
          borderColor: Colors.red,
          opacity: disabled || loading ? 0.6 : 1,
        },
        style,
      ]}
      activeOpacity={0.8}
    >
      {loading ? (
        <ActivityIndicator color={txtMap[variant]} size="small" />
      ) : (
        <View style={styles.btnRow}>
          {icon && <View style={{ marginRight: 7 }}>{icon}</View>}
          <Text style={[styles.btnText, { color: txtMap[variant], fontSize: sizeMap[size] }]}>
            {title}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

// ── Card ─────────────────────────────────────────────────────────────────────

interface CardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  onPress?: () => void;
}

export function Card({ children, style, onPress }: CardProps) {
  if (onPress) {
    return (
      <TouchableOpacity onPress={onPress} activeOpacity={0.85} style={[styles.card, style]}>
        {children}
      </TouchableOpacity>
    );
  }
  return <View style={[styles.card, style]}>{children}</View>;
}

// ── Badge ─────────────────────────────────────────────────────────────────────

interface BadgeProps {
  label: string;
  color?: string;
  textColor?: string;
  size?: 'sm' | 'md';
}

export function Badge({ label, color = Colors.red, textColor = '#fff', size = 'sm' }: BadgeProps) {
  return (
    <View style={[styles.badge, { backgroundColor: color }]}>
      <Text style={[styles.badgeText, { color: textColor, fontSize: size === 'sm' ? 10 : 12 }]}>
        {label}
      </Text>
    </View>
  );
}

// ── Section Header ────────────────────────────────────────────────────────────

interface SectionProps {
  title: string;
  action?: { label: string; onPress: () => void };
  style?: ViewStyle;
}

export function SectionHeader({ title, action, style }: SectionProps) {
  return (
    <View style={[styles.sectionHeader, style]}>
      <View style={styles.sectionTitleRow}>
        <View style={styles.sectionAccent} />
        <Text style={styles.sectionTitle}>{title}</Text>
      </View>
      {action && (
        <TouchableOpacity onPress={action.onPress}>
          <Text style={styles.sectionAction}>{action.label}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

// ── Empty State ───────────────────────────────────────────────────────────────

interface EmptyProps {
  icon?: string;
  title: string;
  subtitle?: string;
  action?: { label: string; onPress: () => void };
}

export function Empty({ title, subtitle, action }: EmptyProps) {
  return (
    <View style={styles.empty}>
      <Text style={styles.emptyTitle}>{title}</Text>
      {subtitle && <Text style={styles.emptySub}>{subtitle}</Text>}
      {action && (
        <Btn title={action.label} onPress={action.onPress} variant="outline" size="sm" style={{ marginTop: 16 }} />
      )}
    </View>
  );
}

// ── Loader ────────────────────────────────────────────────────────────────────

export function Loader({ message }: { message?: string }) {
  return (
    <View style={styles.loader}>
      <ActivityIndicator size="large" color={Colors.red} />
      {message && <Text style={styles.loaderText}>{message}</Text>}
    </View>
  );
}

// ── Input ─────────────────────────────────────────────────────────────────────

import { TextInput, TextInputProps } from 'react-native';

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  containerStyle?: ViewStyle;
}

export function Input({ label, error, leftIcon, containerStyle, style, ...rest }: InputProps) {
  return (
    <View style={[{ marginBottom: 14 }, containerStyle]}>
      {label && <Text style={styles.inputLabel}>{label}</Text>}
      <View style={[styles.inputWrap, error ? { borderColor: Colors.error } : {}]}>
        {leftIcon && <View style={styles.inputIcon}>{leftIcon}</View>}
        <TextInput
          style={[styles.input, leftIcon ? { paddingLeft: 0 } : {}, style]}
          placeholderTextColor={Colors.textMuted}
          {...rest}
        />
      </View>
      {error && <Text style={styles.inputError}>{error}</Text>}
    </View>
  );
}

// ── Hero Banner ───────────────────────────────────────────────────────────────

interface HeroProps {
  title: string;
  subtitle?: string;
  children?: React.ReactNode;
  compact?: boolean;
}

export function HeroBanner({ title, subtitle, children, compact }: HeroProps) {
  return (
    <View style={[styles.hero, compact && { paddingVertical: 24 }]}>
      <Text style={styles.heroTitle}>{title}</Text>
      {subtitle && <Text style={styles.heroSubtitle}>{subtitle}</Text>}
      {children}
    </View>
  );
}

// ── Divider ───────────────────────────────────────────────────────────────────

export function Divider({ style }: { style?: ViewStyle }) {
  return <View style={[styles.divider, style]} />;
}

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  btn: { borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  btnRow: { flexDirection: 'row', alignItems: 'center' },
  btnText: { fontWeight: '700', letterSpacing: 0.3 },

  card: {
    backgroundColor: Colors.surface,
    borderRadius: 14,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
    marginBottom: 12,
  },

  badge: { borderRadius: 20, paddingHorizontal: 8, paddingVertical: 3 },
  badgeText: { fontWeight: '700' },

  sectionHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12, marginTop: 4 },
  sectionTitleRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  sectionAccent: { width: 4, height: 20, backgroundColor: Colors.red, borderRadius: 2 },
  sectionTitle: { fontSize: 17, fontWeight: '700', color: Colors.textPrimary },
  sectionAction: { fontSize: 13, color: Colors.red, fontWeight: '600' },

  empty: { alignItems: 'center', paddingVertical: 48, paddingHorizontal: 24 },
  emptyTitle: { fontSize: 16, fontWeight: '700', color: Colors.textSecondary, textAlign: 'center', marginTop: 12 },
  emptySub: { fontSize: 13, color: Colors.textMuted, textAlign: 'center', marginTop: 6 },

  loader: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 40 },
  loaderText: { marginTop: 12, color: Colors.textSecondary, fontSize: 14 },

  inputLabel: { fontSize: 13, fontWeight: '600', color: Colors.textPrimary, marginBottom: 6 },
  inputWrap: {
    flexDirection: 'row', alignItems: 'center',
    borderWidth: 1.5, borderColor: Colors.border,
    borderRadius: 10, backgroundColor: '#fff',
    paddingHorizontal: 14,
  },
  inputIcon: { marginRight: 8 },
  input: { flex: 1, paddingVertical: 13, fontSize: 15, color: Colors.textPrimary },
  inputError: { color: Colors.error, fontSize: 12, marginTop: 4 },

  hero: {
    backgroundColor: Colors.black,
    paddingHorizontal: 20,
    paddingVertical: 36,
    paddingTop: 60,
    alignItems: 'center',
  },
  heroTitle: { fontSize: 26, fontWeight: '700', color: Colors.gold, textAlign: 'center' },
  heroSubtitle: { fontSize: 14, color: 'rgba(255,255,255,0.8)', textAlign: 'center', marginTop: 6 },

  divider: { height: 1, backgroundColor: Colors.border, marginVertical: 12 },
});
