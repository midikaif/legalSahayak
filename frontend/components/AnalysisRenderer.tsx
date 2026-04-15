import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Props {
  rawAnalysis: string;
}

/** Parse **bold** markdown into Text components */
function renderFormattedText(text: string, baseStyle: any = {}) {
  if (!text || typeof text !== 'string') return <Text style={baseStyle}>{String(text || '')}</Text>;
  
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <Text style={baseStyle}>
      {parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return (
            <Text key={i} style={[baseStyle, { fontWeight: '700', color: '#1F2937' }]}>
              {part.slice(2, -2)}
            </Text>
          );
        }
        return <Text key={i}>{part}</Text>;
      })}
    </Text>
  );
}

function tryParseJSON(text: string): any {
  try {
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
    const text = typeof item === 'string' ? item : String(item);
    return (
      <View key={idx} style={styles.listItem}>
        <View style={[styles.bullet, { backgroundColor: color }]} />
        <View style={{ flex: 1 }}>{renderFormattedText(text, styles.listText)}</View>
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

/** Render plain text with markdown-like formatting (bold, numbered lists, headings) */
function renderRichText(text: string) {
  if (!text) return null;
  
  const lines = text.split('\n');
  return (
    <View>
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <View key={idx} style={{ height: 8 }} />;
        
        // Heading-like lines (starts with # or all caps short line)
        if (trimmed.startsWith('# ')) {
          return (
            <Text key={idx} style={styles.richHeading}>
              {trimmed.replace(/^#+\s*/, '')}
            </Text>
          );
        }
        if (trimmed.startsWith('## ')) {
          return (
            <Text key={idx} style={styles.richSubHeading}>
              {trimmed.replace(/^#+\s*/, '')}
            </Text>
          );
        }
        
        // Numbered list items
        const numMatch = trimmed.match(/^(\d+)\.\s+(.+)/);
        if (numMatch) {
          return (
            <View key={idx} style={styles.numberedItem}>
              <View style={styles.numberCircle}>
                <Text style={styles.numberText}>{numMatch[1]}</Text>
              </View>
              <View style={{ flex: 1 }}>{renderFormattedText(numMatch[2], styles.numberedText)}</View>
            </View>
          );
        }
        
        // Bullet points
        if (trimmed.startsWith('- ') || trimmed.startsWith('• ') || trimmed.startsWith('* ')) {
          return (
            <View key={idx} style={styles.listItem}>
              <View style={[styles.bullet, { backgroundColor: '#4F46E5' }]} />
              <View style={{ flex: 1 }}>{renderFormattedText(trimmed.slice(2), styles.listText)}</View>
            </View>
          );
        }
        
        // Regular paragraph
        return (
          <View key={idx} style={{ marginBottom: 6 }}>
            {renderFormattedText(trimmed, styles.richParagraph)}
          </View>
        );
      })}
    </View>
  );
}

export default function AnalysisRenderer({ rawAnalysis }: Props) {
  if (!rawAnalysis) return null;

  const parsed = tryParseJSON(rawAnalysis);

  // If JSON parsing fails, render as rich formatted text
  if (!parsed) {
    return (
      <View style={styles.container}>
        <View style={styles.richTextCard}>
          {renderRichText(rawAnalysis)}
        </View>
      </View>
    );
  }

  // Extract fields - handle nested structures
  const data = parsed;
  const questionsForLawyer = data.questions_for_lawyer || [];
  const analysis = typeof data.analysis === 'object' 
    ? data.analysis?.description || data.analysis?.title || '' 
    : data.analysis || '';
  const strengths = data.strengths || [];
  const weaknesses = data.weaknesses || data.weaknesses_and_challenges || [];
  const strategy = data.strategy || [];
  const loopholes = data.potential_loopholes_or_legal_precedents_that_could_help || data.loopholes || null;
  
  // Procedure fields
  const steps = data.steps || [];
  const requiredDocs = data.required_documents || [];
  const courtHierarchy = data.court_hierarchy || [];
  const estimatedTimeline = data.estimated_timeline || '';

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
                <View style={{ flex: 1 }}>{renderFormattedText(typeof q === 'string' ? q : String(q), styles.questionText)}</View>
              </View>
            ))}
          </View>
        )}

      {questionsForLawyer.length > 0 && <View style={styles.divider} />}

      {/* CASE ANALYSIS */}
      {analysis ? renderSection(
        'Case Analysis',
        'document-text',
        '#2563EB',
        '#EFF6FF',
        renderRichText(typeof analysis === 'string' ? analysis : JSON.stringify(analysis, null, 2))
      ) : null}

      {/* Key concepts if available */}
      {data.analysis?.key_legal_concepts && 
        renderSection('Key Legal Concepts', 'book', '#0891B2', '#ECFEFF',
          renderList(data.analysis.key_legal_concepts, '#0891B2')
        )
      }

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
                <View style={{ flex: 1 }}>{renderFormattedText(typeof step === 'string' ? step : String(step), styles.strategyStepText)}</View>
              </View>
            ))}
          </View>
        )}

      {/* LOOPHOLES */}
      {loopholes && typeof loopholes === 'object' && !Array.isArray(loopholes) && (
        renderSection(
          'Loopholes & Legal Precedents',
          'bulb',
          '#7C3AED',
          '#F5F3FF',
          <View>
            {loopholes.loopholes_or_helpful_points && renderList(loopholes.loopholes_or_helpful_points, '#7C3AED')}
            {loopholes.relevant_precedents_principles && (
              <View style={{ marginTop: 12 }}>
                <Text style={styles.subHeadingText}>Relevant Precedents</Text>
                {renderList(loopholes.relevant_precedents_principles, '#7C3AED')}
              </View>
            )}
          </View>
        )
      )}
      {loopholes && Array.isArray(loopholes) && loopholes.length > 0 && (
        renderSection('Loopholes & Legal Precedents', 'bulb', '#7C3AED', '#F5F3FF', renderList(loopholes, '#7C3AED'))
      )}

      {/* PROCEDURE: Steps */}
      {steps.length > 0 &&
        renderSection('Step-by-Step Procedure', 'list', '#D97706', '#FFFBEB',
          <View>
            {steps.map((s: any, idx: number) => (
              <View key={idx} style={styles.procedureStep}>
                <View style={styles.procedureStepBadge}>
                  <Text style={styles.procedureStepBadgeText}>{s.step_number || idx + 1}</Text>
                </View>
                <View style={{ flex: 1 }}>
                  {renderFormattedText(s.description || s.title || String(s), styles.procedureStepDesc)}
                  {s.timeline && <Text style={styles.procedureTimeline}>{s.timeline}</Text>}
                </View>
              </View>
            ))}
          </View>
        )}

      {/* PROCEDURE: Required Documents */}
      {requiredDocs.length > 0 &&
        renderSection('Required Documents', 'folder-open', '#0891B2', '#ECFEFF', renderList(requiredDocs, '#0891B2'))}

      {/* PROCEDURE: Court Hierarchy */}
      {courtHierarchy.length > 0 &&
        renderSection('Court Hierarchy', 'business', '#6366F1', '#EEF2FF', renderList(courtHierarchy, '#6366F1'))}

      {/* PROCEDURE: Timeline */}
      {estimatedTimeline ? renderSection('Estimated Timeline', 'time', '#F59E0B', '#FFFBEB',
        renderRichText(estimatedTimeline)
      ) : null}
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
    fontSize: 14,
    color: '#374151',
    lineHeight: 22,
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
    fontSize: 14,
    color: '#374151',
    lineHeight: 22,
  },
  subHeadingText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#7C3AED',
    marginBottom: 8,
  },
  // Rich text styles
  richTextCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
  },
  richHeading: {
    fontSize: 18,
    fontWeight: '800',
    color: '#1F2937',
    marginBottom: 10,
    marginTop: 4,
  },
  richSubHeading: {
    fontSize: 16,
    fontWeight: '700',
    color: '#374151',
    marginBottom: 8,
    marginTop: 4,
  },
  richParagraph: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 24,
  },
  numberedItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  numberCircle: {
    width: 26,
    height: 26,
    borderRadius: 13,
    backgroundColor: '#4F46E5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    marginTop: 2,
  },
  numberText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '700',
  },
  numberedText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 22,
  },
  // Procedure styles
  procedureStep: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  procedureStepBadge: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#D97706',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
    marginTop: 2,
  },
  procedureStepBadgeText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '800',
  },
  procedureStepDesc: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 22,
  },
  procedureTimeline: {
    fontSize: 12,
    color: '#D97706',
    fontWeight: '600',
    marginTop: 4,
  },
});
