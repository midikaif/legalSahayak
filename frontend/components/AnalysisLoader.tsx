import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const STEPS = [
  { label: 'Reading your case details...', icon: 'document-text' as const, duration: 3000 },
  { label: 'Analyzing legal provisions...', icon: 'search' as const, duration: 5000 },
  { label: 'Identifying strengths & weaknesses...', icon: 'analytics' as const, duration: 5000 },
  { label: 'Finding loopholes & precedents...', icon: 'bulb' as const, duration: 5000 },
  { label: 'Building your strategy...', icon: 'shield-checkmark' as const, duration: 5000 },
  { label: 'Preparing questions for lawyer...', icon: 'chatbubbles' as const, duration: 5000 },
];

interface Props {
  isVisible: boolean;
  estimatedTime?: number;
}

export default function AnalysisLoader({ isVisible, estimatedTime = 30 }: Props) {
  const [currentStep, setCurrentStep] = React.useState(0);
  const [elapsedTime, setElapsedTime] = React.useState(0);
  const pulseAnim = useRef(new Animated.Value(0.3)).current;
  const progressAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (!isVisible) {
      setCurrentStep(0);
      setElapsedTime(0);
      progressAnim.setValue(0);
      return;
    }

    // Pulse animation
    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1, duration: 800, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 0.3, duration: 800, useNativeDriver: true }),
      ])
    );
    pulse.start();

    // Progress animation
    Animated.timing(progressAnim, {
      toValue: 1,
      duration: estimatedTime * 1000,
      useNativeDriver: false,
    }).start();

    // Step cycling
    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % STEPS.length);
    }, 4000);

    // Timer
    const timerInterval = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);

    return () => {
      pulse.stop();
      clearInterval(stepInterval);
      clearInterval(timerInterval);
    };
  }, [isVisible]);

  if (!isVisible) return null;

  const remainingTime = Math.max(0, estimatedTime - elapsedTime);
  const step = STEPS[currentStep];

  const progressWidth = progressAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Animated.View style={[styles.iconPulse, { opacity: pulseAnim }]}>
          <View style={styles.iconCircle}>
            <Ionicons name={step.icon} size={32} color="#4F46E5" />
          </View>
        </Animated.View>

        <Text style={styles.stepLabel}>{step.label}</Text>

        <View style={styles.progressContainer}>
          <View style={styles.progressTrack}>
            <Animated.View style={[styles.progressFill, { width: progressWidth }]} />
          </View>
        </View>

        <View style={styles.timeContainer}>
          <Ionicons name="time-outline" size={16} color="#6B7280" />
          <Text style={styles.timeText}>
            {remainingTime > 0
              ? `~${remainingTime}s remaining`
              : 'Almost there...'}
          </Text>
        </View>

        <View style={styles.stepsIndicator}>
          {STEPS.map((_, idx) => (
            <View
              key={idx}
              style={[
                styles.stepDot,
                idx === currentStep && styles.stepDotActive,
                idx < currentStep && styles.stepDotCompleted,
              ]}
            />
          ))}
        </View>

        <Text style={styles.tipText}>
          Our AI is analyzing Indian legal provisions, precedents, and strategies for your case
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 100,
    padding: 24,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 32,
    alignItems: 'center',
    width: '100%',
    maxWidth: 340,
  },
  iconPulse: {
    marginBottom: 20,
  },
  iconCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  stepLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    textAlign: 'center',
    marginBottom: 24,
    minHeight: 24,
  },
  progressContainer: {
    width: '100%',
    marginBottom: 12,
  },
  progressTrack: {
    height: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4F46E5',
    borderRadius: 3,
  },
  timeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  timeText: {
    fontSize: 13,
    color: '#6B7280',
    marginLeft: 6,
  },
  stepsIndicator: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  stepDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E5E7EB',
    marginHorizontal: 3,
  },
  stepDotActive: {
    backgroundColor: '#4F46E5',
    width: 20,
  },
  stepDotCompleted: {
    backgroundColor: '#10B981',
  },
  tipText: {
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
    lineHeight: 18,
  },
});
