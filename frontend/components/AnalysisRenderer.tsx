import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Props {
  rawAnalysis: string;
}

function tryParseJSON(text: string): any {
  try {
    // Remove markdown code blocks if present
    let cleaned = text.trim();
    if (cleaned.startsWith('```json')) {
      cleaned = cleaned.replace(/^```json\s*/, '').replace(/```\s*$/, '');
    } else if (cleaned.startsWith('```')) {
      cleaned = cleaned.replace(/^```\s*/, '').replace(/```\s*$/, '');
    }
    return JSON.parse(cleaned);
  } catch {
    return null;
  }
}

function renderList(items: string[], color: string = '#4B5563') {
  if (!items || !Array.isArray(items)) return null;
  return items.map((item, idx) => {
    const cleanItem = typeof item === 'string' ? item.replace(/^\*\*|\*\*$/g, '').replace(/^\*\*\d+\.\s*/, '') : String(item);
    return (
      <View key={idx} style={styles.listItem}>
        <View style={[styles.bullet, { backgroundColor: color }]} />
        <Text style={styles.listText}>{cleanItem}</Text>
      </View>
    );
  });
}

function renderSection(
  title: string,
  icon: string,
  iconColor: string,
  bgColor: string,
  content: React.ReactNode
) {
  return (
    <View style={[styles.section, { borderLeftColor: iconColor }]}>
      <View style={[styles.sectionHeader, { backgroundColor: bgColor }]}>
        <Ionicons name={icon as any} size={22} color={iconColor} />
        <Text style={[styles.sectionTitle, { color: iconColor }]}>{title}</Text>
      </View>
      <View style={styles.sectionBody}>{content}</View>
    </View>
  );
}

export default function AnalysisRenderer({ rawAnalysis }: Props) {
  if (!rawAnalysis) return null;

  const parsed = tryParseJSON(rawAnalysis);

  // If we can't parse JSON, render as formatted text
  if (!parsed) {
    return (
      <View style={styles.container}>
        <View style={styles.plainTextCard}>
          <Text style={styles.plainText}>{rawAnalysis}</Text>
        </View>
      </View>
    );
  }

  // Extract fields - handle nested structure
  const data = parsed.analysis && typeof parsed.analysis === 'object' ? parsed : parsed;
  
  const questionsForLawyer = data.questions_for_lawyer || parsed.questions_for_lawyer || [];
  const analysis = typeof data.analysis === 'object' ? data.analysis?.description || JSON.stringify(data.analysis) : data.analysis || '';
  const strengths = data.strengths || [];
  const weaknesses = data.weaknesses || data.weaknesses_and_challenges || [];
  const strategy = data.strategy || [];
  const loopholes = data.potential_loopholes_or_legal_precedents_that_could_help || data.loopholes || null;

  return (
    <View style={styles.container}>
      {/* QUESTIONS FOR LAWYER - FIRST */}
      {questionsForLawyer.length > 0 &&
        renderSection(
          'Questions to Ask Your Lawyer',
          'chatbubbles',
          '#7C3AED',
          '#F5F3FF',
          <View>
            {questionsForLawyer.map((q: string, idx: number) => (
              <View key={idx} style={styles.questionItem}>
                <View style={styles.questionNumber}>
                  <Text style={styles.questionNumberText}>{idx + 1}</Text>
                </View>
                <Text style={styles.questionText}>
                  {typeof q === 'string' ? q.replace(/^\*\*|\*\*$/g, '') : String(q)}
                </Text>
              </View>
            ))}
          </View>
        )}

      <View style={styles.divider} />

      {/* CASE ANALYSIS */}
      {analysis &&
        renderSection(
          'Case Analysis',
          'document-text',
          '#2563EB',
          '#EFF6FF',
          <Text style={styles.analysisText}>{typeof analysis === 'string' ? analysis : JSON.stringify(analysis, null, 2)}</Text>
        )}

      {/* STRENGTHS */}
      {strengths.length > 0 &&
        renderSection('Strengths', 'checkmark-circle', '#059669', '#ECFDF5', renderList(strengths, '#059669'))}

      {/* WEAKNESSES */}
      {weaknesses.length > 0 &&
        renderSection('Weaknesses & Challenges', 'alert-circle', '#DC2626', '#FEF2F2', renderList(weaknesses, '#DC2626'))}

      {/* STRATEGY */}
      {strategy.length > 0 &&
        renderSection(
          'Recommended Strategy',
          'shield-checkmark',
          '#D97706',
          '#FFFBEB',
          <View>
            {strategy.map((step: string, idx: number) => (
              <View key={idx} style={styles.strategyStep}>
                <View style={styles.strategyStepNum}>
                  <Text style={styles.strategyStepNumText}>{idx + 1}</Text>
                </View>
                <Text style={styles.strategyStepText}>
                  {typeof step === 'string' ? step.replace(/^\*\*|\*\*$/g, '') : String(step)}
                </Text>
              </View>
            ))}
          </View>
        )}

      {/* LOOPHOLES */}
      {loopholes && (
        renderSection(
          'Loopholes & Legal Precedents',
          'bulb',
          '#7C3AED',
          '#F5F3FF',
          <View>
            {loopholes.loopholes_or_helpful_points && renderList(loopholes.loopholes_or_helpful_points, '#7C3AED')}
            {loopholes.relevant_precedents_principles && (
              <View style={{ marginTop: 12 }}>
                <Text style={[styles.subHeading, { color: '#7C3AED' }]}>Relevant Precedents</Text>
                {renderList(loopholes.relevant_precedents_principles, '#7C3AED')}
              </View>
            )}
            {typeof loopholes === 'string' && <Text style={styles.analysisText}>{loopholes}</Text>}
          </View>
        )
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: 8,
  },
  section: {
    marginBottom: 20,
    borderLeftWidth: 3,
    borderRadius: 12,
    backgroundColor: '#fff',
    overflow: 'hidden',
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginLeft: 10,
  },
  sectionBody: {
    padding: 16,
    paddingTop: 8,
  },
  divider: {
    height: 1,
    backgroundColor: '#E5E7EB',
    marginVertical: 8,
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  bullet: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginTop: 7,
    marginRight: 12,
  },
  listText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    lineHeight: 22,
  },
  analysisText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 24,
  },
  questionItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 14,
  },
  questionNumber: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#7C3AED',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    marginTop: 2,
  },
  questionNumberText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '700',
  },
  questionText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    lineHeight: 22,
  },
  strategyStep: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 14,
  },
  strategyStepNum: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#D97706',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    marginTop: 2,
  },
  strategyStepNumText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '700',
  },
  strategyStepText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    lineHeight: 22,
  },
  subHeading: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  plainTextCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
  },
  plainText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 24,
  },
});
