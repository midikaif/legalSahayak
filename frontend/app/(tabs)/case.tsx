import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { Picker } from '@react-native-picker/picker';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

const CASE_TYPES = [
  'Civil',
  'Criminal',
  'Family',
  'Property',
  'Consumer',
  'Labor',
  'Tax',
  'Corporate',
  'Other',
];

export default function CaseScreen() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'analyze' | 'history' | 'procedure'>('analyze');
  const [caseTitle, setCaseTitle] = useState('');
  const [caseType, setCaseType] = useState('Civil');
  const [caseDescription, setCaseDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [procedure, setProcedure] = useState<any>(null);

  const analyzeCase = async () => {
    if (!caseTitle || !caseDescription) {
      Alert.alert('Error', 'Please fill all fields');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('user_id', user?.id || '');
      formData.append('case_title', caseTitle);
      formData.append('case_type', caseType);
      formData.append('case_description', caseDescription);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 90000);

      const response = await fetch(`${API_URL}/api/case/analyze`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      const data = await response.json();

      if (response.ok) {
        setAnalysis(data);
        Alert.alert('Success', 'Case analyzed successfully');
        setCaseTitle('');
        setCaseDescription('');
      } else {
        Alert.alert('Error', data.detail || 'Analysis failed. Please try again.');
      }
    } catch (error: any) {
      console.error('Error analyzing case:', error);
      if (error.name === 'AbortError') {
        Alert.alert('Timeout', 'Analysis is taking too long. Please try again with a shorter description.');
      } else {
        Alert.alert('Error', 'Network error. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    if (!user?.id) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/case/history/${user.id}`);
      const data = await response.json();

      if (response.ok) {
        setHistory(data);
      }
    } catch (error) {
      console.error('Error loading history:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadProcedure = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/procedure/${caseType}`);
      const data = await response.json();

      if (response.ok) {
        setProcedure(data);
      }
    } catch (error) {
      console.error('Error loading procedure:', error);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (activeTab === 'history') {
      loadHistory();
    } else if (activeTab === 'procedure') {
      loadProcedure();
    }
  }, [activeTab]);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Case Analysis</Text>
        <Text style={styles.headerSubtitle}>Get insights and strategy</Text>
      </View>

      <View style={styles.tabs}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'analyze' && styles.activeTab]}
          onPress={() => setActiveTab('analyze')}
        >
          <Text style={[styles.tabText, activeTab === 'analyze' && styles.activeTabText]}>
            Analyze
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'procedure' && styles.activeTab]}
          onPress={() => setActiveTab('procedure')}
        >
          <Text style={[styles.tabText, activeTab === 'procedure' && styles.activeTabText]}>
            Procedure
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'history' && styles.activeTab]}
          onPress={() => setActiveTab('history')}
        >
          <Text style={[styles.tabText, activeTab === 'history' && styles.activeTabText]}>
            History
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {activeTab === 'analyze' ? (
          <View>
            <View style={styles.inputContainer}>
              <Text style={styles.label}>Case Title *</Text>
              <TextInput
                style={styles.input}
                placeholder="e.g., Property Dispute"
                value={caseTitle}
                onChangeText={setCaseTitle}
                placeholderTextColor="#9CA3AF"
              />
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.label}>Case Type *</Text>
              <View style={styles.pickerWrapper}>
                <Picker
                  selectedValue={caseType}
                  onValueChange={setCaseType}
                  style={styles.picker}
                >
                  {CASE_TYPES.map((type) => (
                    <Picker.Item key={type} label={type} value={type} />
                  ))}
                </Picker>
              </View>
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.label}>Case Description *</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                placeholder="Describe your case in detail..."
                value={caseDescription}
                onChangeText={setCaseDescription}
                multiline
                numberOfLines={8}
                placeholderTextColor="#9CA3AF"
              />
            </View>

            <TouchableOpacity
              style={styles.analyzeButton}
              onPress={analyzeCase}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <Ionicons name="analytics" size={20} color="#fff" />
                  <Text style={styles.analyzeButtonText}>Analyze Case</Text>
                </>
              )}
            </TouchableOpacity>

            {analysis && (
              <View style={styles.analysisCard}>
                <Text style={styles.analysisTitle}>Case Analysis</Text>
                <View style={styles.analysisContent}>
                  <Text style={styles.analysisLabel}>AI Analysis:</Text>
                  <Text style={styles.analysisText}>{analysis.analysis}</Text>
                </View>

                <View style={styles.tipBox}>
                  <Ionicons name="bulb" size={20} color="#F59E0B" />
                  <Text style={styles.tipText}>
                    Use this analysis to prepare questions for your lawyer consultation
                  </Text>
                </View>
              </View>
            )}
          </View>
        ) : activeTab === 'procedure' ? (
          <View>
            <View style={styles.inputContainer}>
              <Text style={styles.label}>Select Case Type</Text>
              <View style={styles.pickerWrapper}>
                <Picker
                  selectedValue={caseType}
                  onValueChange={setCaseType}
                  style={styles.picker}
                >
                  {CASE_TYPES.map((type) => (
                    <Picker.Item key={type} label={type} value={type} />
                  ))}
                </Picker>
              </View>
            </View>

            <TouchableOpacity
              style={styles.loadButton}
              onPress={loadProcedure}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <Ionicons name="list" size={20} color="#fff" />
                  <Text style={styles.loadButtonText}>Load Procedure</Text>
                </>
              )}
            </TouchableOpacity>

            {procedure && (
              <View style={styles.procedureCard}>
                <Text style={styles.procedureTitle}>{caseType} Case Procedure</Text>
                <View style={styles.procedureContent}>
                  <Text style={styles.procedureText}>{procedure.procedure}</Text>
                </View>
              </View>
            )}
          </View>
        ) : (
          <View>
            {loading ? (
              <ActivityIndicator size="large" color="#4F46E5" style={{ marginTop: 40 }} />
            ) : history.length === 0 ? (
              <View style={styles.emptyState}>
                <Ionicons name="briefcase-outline" size={64} color="#D1D5DB" />
                <Text style={styles.emptyStateText}>No case analysis history</Text>
              </View>
            ) : (
              history.map((item) => (
                <TouchableOpacity
                  key={item.id}
                  style={styles.historyCard}
                  onPress={() => setAnalysis(item)}
                >
                  <View style={styles.historyHeader}>
                    <Ionicons name="briefcase" size={24} color="#10B981" />
                    <View style={styles.historyInfo}>
                      <Text style={styles.historyTitle}>{item.case_title}</Text>
                      <Text style={styles.historyType}>{item.case_type}</Text>
                      <Text style={styles.historyDate}>
                        {new Date(item.created_at).toLocaleDateString()}
                      </Text>
                    </View>
                  </View>
                </TouchableOpacity>
              ))
            )}
          </View>
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
  tabs: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  tab: {
    flex: 1,
    paddingVertical: 16,
    alignItems: 'center',
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: '#10B981',
  },
  tabText: {
    fontSize: 14,
    color: '#6B7280',
  },
  activeTabText: {
    color: '#10B981',
    fontWeight: '600',
  },
  content: {
    padding: 20,
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#1F2937',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  textArea: {
    height: 160,
    textAlignVertical: 'top',
  },
  pickerWrapper: {
    backgroundColor: '#fff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    overflow: 'hidden',
  },
  picker: {
    height: 52,
  },
  analyzeButton: {
    flexDirection: 'row',
    backgroundColor: '#10B981',
    borderRadius: 12,
    padding: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  analyzeButtonText: {
    marginLeft: 8,
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  loadButton: {
    flexDirection: 'row',
    backgroundColor: '#F59E0B',
    borderRadius: 12,
    padding: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  loadButtonText: {
    marginLeft: 8,
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  analysisCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  analysisTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 16,
  },
  analysisContent: {
    marginBottom: 16,
  },
  analysisLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#10B981',
    marginBottom: 8,
  },
  analysisText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 22,
  },
  tipBox: {
    flexDirection: 'row',
    backgroundColor: '#FEF3C7',
    borderRadius: 12,
    padding: 12,
    marginTop: 8,
  },
  tipText: {
    flex: 1,
    marginLeft: 8,
    fontSize: 13,
    color: '#78350F',
    lineHeight: 18,
  },
  procedureCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  procedureTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 16,
  },
  procedureContent: {
    marginBottom: 8,
  },
  procedureText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 22,
  },
  emptyState: {
    alignItems: 'center',
    marginTop: 60,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#9CA3AF',
    marginTop: 16,
  },
  historyCard: {
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
  historyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  historyInfo: {
    marginLeft: 12,
    flex: 1,
  },
  historyTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
  historyType: {
    fontSize: 14,
    color: '#10B981',
    marginTop: 2,
  },
  historyDate: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
});