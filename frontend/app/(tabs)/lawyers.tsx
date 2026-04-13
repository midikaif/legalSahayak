import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function LawyersScreen() {
  const [lawyers, setLawyers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchSpecialization, setSearchSpecialization] = useState('');
  const [searchLocation, setSearchLocation] = useState('');
  const [selectedLawyer, setSelectedLawyer] = useState<any>(null);

  const searchLawyers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchSpecialization) params.append('specialization', searchSpecialization);
      if (searchLocation) params.append('location', searchLocation);

      const response = await fetch(`${API_URL}/api/lawyers/search?${params.toString()}`);
      const data = await response.json();

      if (response.ok) {
        setLawyers(data);
      }
    } catch (error) {
      console.error('Error searching lawyers:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    searchLawyers();
  }, []);

  if (selectedLawyer) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => setSelectedLawyer(null)} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#1F2937" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Lawyer Profile</Text>
        </View>

        <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.profileCard}>
            <View style={styles.profileIcon}>
              <Ionicons name="person" size={48} color="#4F46E5" />
            </View>
            <Text style={styles.lawyerName}>{selectedLawyer.full_name}</Text>
            <Text style={styles.lawyerSpecialization}>{selectedLawyer.specialization}</Text>
            
            {selectedLawyer.rating > 0 && (
              <View style={styles.ratingContainer}>
                <Ionicons name="star" size={20} color="#F59E0B" />
                <Text style={styles.rating}>{selectedLawyer.rating.toFixed(1)}</Text>
              </View>
            )}
          </View>

          <View style={styles.detailsCard}>
            <View style={styles.detailRow}>
              <Ionicons name="briefcase" size={20} color="#6B7280" />
              <Text style={styles.detailLabel}>Experience:</Text>
              <Text style={styles.detailValue}>
                {selectedLawyer.years_of_experience || 0} years
              </Text>
            </View>

            <View style={styles.detailRow}>
              <Ionicons name="location" size={20} color="#6B7280" />
              <Text style={styles.detailLabel}>Location:</Text>
              <Text style={styles.detailValue}>{selectedLawyer.location || 'N/A'}</Text>
            </View>

            <View style={styles.detailRow}>
              <Ionicons name="card" size={20} color="#6B7280" />
              <Text style={styles.detailLabel}>Bar Council:</Text>
              <Text style={styles.detailValue}>
                {selectedLawyer.bar_council_number || 'N/A'}
              </Text>
            </View>

            <View style={styles.detailRow}>
              <Ionicons name="checkmark-circle" size={20} color="#6B7280" />
              <Text style={styles.detailLabel}>Cases Handled:</Text>
              <Text style={styles.detailValue}>{selectedLawyer.cases_handled || 0}</Text>
            </View>
          </View>

          {selectedLawyer.bio && (
            <View style={styles.bioCard}>
              <Text style={styles.bioTitle}>About</Text>
              <Text style={styles.bioText}>{selectedLawyer.bio}</Text>
            </View>
          )}

          <View style={styles.contactCard}>
            <Text style={styles.contactTitle}>Contact Information</Text>
            <View style={styles.contactRow}>
              <Ionicons name="mail" size={20} color="#4F46E5" />
              <Text style={styles.contactText}>{selectedLawyer.email}</Text>
            </View>
            {selectedLawyer.phone && (
              <View style={styles.contactRow}>
                <Ionicons name="call" size={20} color="#4F46E5" />
                <Text style={styles.contactText}>{selectedLawyer.phone}</Text>
              </View>
            )}
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Find Lawyers</Text>
        <Text style={styles.headerSubtitle}>Connect with legal professionals</Text>
      </View>

      <View style={styles.searchContainer}>
        <View style={styles.searchInputContainer}>
          <Ionicons name="search" size={20} color="#6B7280" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Specialization (e.g., Criminal)"
            value={searchSpecialization}
            onChangeText={setSearchSpecialization}
            placeholderTextColor="#9CA3AF"
          />
        </View>

        <View style={styles.searchInputContainer}>
          <Ionicons name="location" size={20} color="#6B7280" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Location (e.g., Mumbai)"
            value={searchLocation}
            onChangeText={setSearchLocation}
            placeholderTextColor="#9CA3AF"
          />
        </View>

        <TouchableOpacity style={styles.searchButton} onPress={searchLawyers}>
          <Ionicons name="search" size={20} color="#fff" />
          <Text style={styles.searchButtonText}>Search</Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {loading ? (
          <ActivityIndicator size="large" color="#4F46E5" style={{ marginTop: 40 }} />
        ) : lawyers.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="people-outline" size={64} color="#D1D5DB" />
            <Text style={styles.emptyStateText}>No lawyers found</Text>
            <Text style={styles.emptyStateSubtext}>Try adjusting your search criteria</Text>
          </View>
        ) : (
          lawyers.map((lawyer) => (
            <TouchableOpacity
              key={lawyer.id}
              style={styles.lawyerCard}
              onPress={() => setSelectedLawyer(lawyer)}
            >
              <View style={styles.lawyerIconContainer}>
                <Ionicons name="person" size={32} color="#4F46E5" />
              </View>
              <View style={styles.lawyerInfo}>
                <Text style={styles.lawyerCardName}>{lawyer.full_name}</Text>
                <Text style={styles.lawyerCardSpecialization}>{lawyer.specialization}</Text>
                <View style={styles.lawyerCardMeta}>
                  {lawyer.location && (
                    <View style={styles.metaItem}>
                      <Ionicons name="location" size={14} color="#6B7280" />
                      <Text style={styles.metaText}>{lawyer.location}</Text>
                    </View>
                  )}
                  {lawyer.years_of_experience > 0 && (
                    <View style={styles.metaItem}>
                      <Ionicons name="briefcase" size={14} color="#6B7280" />
                      <Text style={styles.metaText}>{lawyer.years_of_experience}y exp</Text>
                    </View>
                  )}
                  {lawyer.rating > 0 && (
                    <View style={styles.metaItem}>
                      <Ionicons name="star" size={14} color="#F59E0B" />
                      <Text style={styles.metaText}>{lawyer.rating.toFixed(1)}</Text>
                    </View>
                  )}
                </View>
              </View>
              <Ionicons name="chevron-forward" size={24} color="#D1D5DB" />
            </TouchableOpacity>
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  backButton: {
    marginBottom: 12,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  searchContainer: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  searchInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    marginBottom: 12,
    paddingHorizontal: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  searchIcon: {
    marginRight: 12,
  },
  searchInput: {
    flex: 1,
    height: 48,
    fontSize: 16,
    color: '#1F2937',
  },
  searchButton: {
    flexDirection: 'row',
    backgroundColor: '#4F46E5',
    borderRadius: 12,
    padding: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchButtonText: {
    marginLeft: 8,
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  content: {
    padding: 20,
  },
  emptyState: {
    alignItems: 'center',
    marginTop: 60,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 16,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 8,
  },
  lawyerCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  lawyerIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  lawyerInfo: {
    flex: 1,
  },
  lawyerCardName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
  lawyerCardSpecialization: {
    fontSize: 14,
    color: '#4F46E5',
    marginTop: 2,
  },
  lawyerCardMeta: {
    flexDirection: 'row',
    marginTop: 8,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 12,
  },
  metaText: {
    fontSize: 12,
    color: '#6B7280',
    marginLeft: 4,
  },
  profileCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  profileIcon: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  lawyerName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  lawyerSpecialization: {
    fontSize: 16,
    color: '#4F46E5',
    marginTop: 4,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
  },
  rating: {
    marginLeft: 4,
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
  detailsCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  detailLabel: {
    flex: 1,
    marginLeft: 12,
    fontSize: 14,
    color: '#6B7280',
  },
  detailValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  bioCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  bioTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  bioText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 22,
  },
  contactCard: {
    backgroundColor: '#EEF2FF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
  },
  contactTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12,
  },
  contactRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  contactText: {
    marginLeft: 12,
    fontSize: 14,
    color: '#4F46E5',
  },
});