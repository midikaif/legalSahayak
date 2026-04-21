import React from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { useAuth } from "../../contexts/AuthContext";
import { Ionicons } from "@expo/vector-icons";

export default function HomeScreen() {
  const { user } = useAuth();
  const router = useRouter();

  const features = [
    {
      id: 1,
      title: "Contract Analysis",
      description: "Simplify legal documents and understand contracts",
      icon: "document-text",
      color: "#4F46E5",
      route: "/(tabs)/contract",
    },
    {
      id: 2,
      title: "Case Analysis",
      description: "Get insights and strategy for your legal case",
      icon: "briefcase",
      color: "#10B981",
      route: "/(tabs)/case",
    },
    {
      id: 3,
      title: "Legal Procedures",
      description: "Step-by-step guide for legal processes",
      icon: "list",
      color: "#F59E0B",
      route: "/(tabs)/case",
    },
    {
      id: 4,
      title: "Find Lawyers",
      description: "Connect with qualified legal professionals",
      icon: "people",
      color: "#EF4444",
      route: "/(tabs)/lawyers",
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Welcome back,</Text>
            <Text style={styles.userName}>{user?.full_name || "User"}</Text>
            <Text style={styles.userType}>
              {user?.user_type === "lawyer" ? "⚖️ Lawyer" : "👤 Common User"}
            </Text>
          </View>
          <View style={styles.iconContainer}>
            <Ionicons name="scale" size={40} color="#4F46E5" />
          </View>
        </View>

        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={24} color="#4F46E5" />
          <View style={styles.infoContent}>
            <Text style={styles.infoTitle}>
              Legal Assistance at Your Fingertips
            </Text>
            <Text style={styles.infoText}>
              LegalSahayak helps you understand complex legal matters, analyze
              cases, and connect with lawyers.
            </Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>Features</Text>

        <View style={styles.featuresGrid}>
          {features.map((feature) => (
            <TouchableOpacity
              key={feature.id}
              style={styles.featureCard}
              onPress={() => router.push(feature.route as any)}
            >
              <View
                style={[
                  styles.featureIcon,
                  { backgroundColor: feature.color + "20" },
                ]}
              >
                <Ionicons
                  name={feature.icon as any}
                  size={32}
                  color={feature.color}
                />
              </View>
              <Text style={styles.featureTitle}>{feature.title}</Text>
              <Text style={styles.featureDescription}>
                {feature.description}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.tipCard}>
          <Text style={styles.tipTitle}>💡 Quick Tip</Text>
          <Text style={styles.tipText}>
            Always document everything in writing. Keep copies of all legal
            documents, contracts, and correspondence for your records.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F9FAFB",
  },
  scrollContent: {
    padding: 20,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 24,
  },
  greeting: {
    fontSize: 16,
    color: "#6B7280",
  },
  userName: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#1F2937",
    marginTop: 4,
  },
  userType: {
    fontSize: 14,
    color: "#4F46E5",
    marginTop: 4,
  },
  iconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: "#EEF2FF",
    justifyContent: "center",
    alignItems: "center",
  },
  infoCard: {
    flexDirection: "row",
    backgroundColor: "#EEF2FF",
    borderRadius: 16,
    padding: 16,
    marginBottom: 24,
  },
  infoContent: {
    flex: 1,
    marginLeft: 12,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#1F2937",
    marginBottom: 4,
  },
  infoText: {
    fontSize: 14,
    color: "#4B5563",
    lineHeight: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#1F2937",
    marginBottom: 16,
  },
  featuresGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    marginBottom: 24,
  },
  featureCard: {
    width: "48%",
    backgroundColor: "#fff",
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  featureIcon: {
    width: 64,
    height: 64,
    borderRadius: 16,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#1F2937",
    marginBottom: 8,
  },
  featureDescription: {
    fontSize: 13,
    color: "#6B7280",
    lineHeight: 18,
  },
  tipCard: {
    backgroundColor: "#FEF3C7",
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
  },
  tipTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#92400E",
    marginBottom: 8,
  },
  tipText: {
    fontSize: 14,
    color: "#78350F",
    lineHeight: 20,
  },
});
