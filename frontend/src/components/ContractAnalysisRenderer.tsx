import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";

interface Props {
  rawAnalysis: string;
}

/** Parse **bold** markdown into Text components */
function renderFormattedText(text: string, baseStyle: any = {}) {
  if (!text || typeof text !== "string")
    return <Text style={baseStyle}>{String(text || "")}</Text>;

  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <Text style={baseStyle}>
      {parts.map((part, i) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return (
            <Text
              key={i}
              style={[baseStyle, { fontWeight: "700", color: "#1F2937" }]}
            >
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
    if (cleaned.startsWith("```json")) {
      cleaned = cleaned.replace(/^```json\s*/, "").replace(/```\s*$/, "");
    } else if (cleaned.startsWith("```")) {
      cleaned = cleaned.replace(/^```\s*/, "").replace(/```\s*$/, "");
    }
    return JSON.parse(cleaned);
  } catch {
    return null;
  }
}

function renderList(
  items: string[],
  color: string = "#4B5563",
  icon: string = "ellipse",
) {
  if (!items || !Array.isArray(items)) return null;
  return items.map((item, idx) => {
    const text = typeof item === "string" ? item : String(item);
    return (
      <View key={idx} style={styles.listItem}>
        <Ionicons
          name={icon as any}
          size={14}
          color={color}
          style={styles.listIcon}
        />
        <View style={{ flex: 1 }}>
          {renderFormattedText(text, styles.listText)}
        </View>
      </View>
    );
  });
}

function renderDictionary(items: Record<string, string>, color: string) {
  if (!items || typeof items !== "object") return null;
  return Object.entries(items).map(([term, explanation], idx) => (
    <View key={idx} style={styles.dictionaryItem}>
      <View style={styles.termHeader}>
        <Ionicons
          name="book-outline"
          size={16}
          color={color}
          style={{ marginRight: 6 }}
        />
        <Text style={[styles.termText, { color }]}>{term}</Text>
      </View>
      <Text style={styles.explanationText}>{explanation}</Text>
    </View>
  ));
}

function renderSection(
  title: string,
  icon: string,
  iconColor: string,
  bgColor: string,
  content: React.ReactNode,
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

/** Fallback renderer if the AI returns raw text instead of JSON */
function renderRichText(text: string) {
  if (!text) return null;

  const lines = text.split("\n");
  return (
    <View>
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <View key={idx} style={{ height: 8 }} />;

        if (trimmed.startsWith("# ")) {
          return (
            <Text key={idx} style={styles.richHeading}>
              {trimmed.replace(/^#+\s*/, "")}
            </Text>
          );
        }
        if (trimmed.startsWith("## ")) {
          return (
            <Text key={idx} style={styles.richSubHeading}>
              {trimmed.replace(/^#+\s*/, "")}
            </Text>
          );
        }
        if (
          trimmed.startsWith("- ") ||
          trimmed.startsWith("• ") ||
          trimmed.startsWith("* ")
        ) {
          return (
            <View key={idx} style={styles.listItem}>
              <Ionicons
                name="ellipse"
                size={10}
                color="#4F46E5"
                style={styles.listIcon}
              />
              <View style={{ flex: 1 }}>
                {renderFormattedText(trimmed.slice(2), styles.listText)}
              </View>
            </View>
          );
        }
        return (
          <View key={idx} style={{ marginBottom: 6 }}>
            {renderFormattedText(trimmed, styles.richParagraph)}
          </View>
        );
      })}
    </View>
  );
}

export default function ContractAnalysisRenderer({ rawAnalysis }: Props) {
  if (!rawAnalysis) return null;

  const parsed = tryParseJSON(rawAnalysis);

  if (!parsed) {
    return (
      <View style={styles.container}>
        <View style={styles.richTextCard}>{renderRichText(rawAnalysis)}</View>
      </View>
    );
  }

  const data = parsed;

  // Map fields from backend JSON structure
  const summary = data.simplified_text || "";
  const risks = data.risks || data.red_flags || [];
  const keyPoints = data.key_points || data.obligations || [];
  const legalTerms = data.legal_terms || data.jargon || null;

  return (
    <View style={styles.container}>
      {/* RED FLAGS / MALICIOUS CLAUSES (Prioritized at the top) */}
      {risks.length > 0 &&
        renderSection(
          "Red Flags & Hidden Risks",
          "warning",
          "#E11D48", // Rose/Red
          "#FFF1F2",
          renderList(risks, "#E11D48", "alert-circle"),
        )}

      {/* PLAIN ENGLISH SUMMARY */}
      {summary
        ? renderSection(
            "Plain English Summary",
            "document-text",
            "#2563EB", // Blue
            "#EFF6FF",
            renderRichText(
              typeof summary === "string" ? summary : JSON.stringify(summary),
            ),
          )
        : null}

      {/* KEY OBLIGATIONS & POINTS */}
      {keyPoints.length > 0 &&
        renderSection(
          "Key Terms & Obligations",
          "checkmark-circle",
          "#059669", // Emerald/Green
          "#ECFDF5",
          renderList(keyPoints, "#059669", "checkmark"),
        )}

      {/* LEGAL JARGON EXPLAINED */}
      {legalTerms &&
        Object.keys(legalTerms).length > 0 &&
        renderSection(
          "Legal Jargon Explained",
          "library",
          "#7C3AED", // Purple
          "#F5F3FF",
          renderDictionary(legalTerms, "#7C3AED"),
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
    borderLeftWidth: 4,
    borderRadius: 12,
    backgroundColor: "#fff",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
    overflow: "hidden",
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    padding: 14,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "800",
    marginLeft: 10,
  },
  sectionBody: {
    padding: 16,
    paddingTop: 12,
  },
  listItem: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: 12,
  },
  listIcon: {
    marginTop: 3,
    marginRight: 10,
  },
  listText: {
    fontSize: 14,
    color: "#374151",
    lineHeight: 22,
  },
  dictionaryItem: {
    backgroundColor: "#F9FAFB",
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#F3F4F6",
  },
  termHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 4,
  },
  termText: {
    fontSize: 15,
    fontWeight: "700",
  },
  explanationText: {
    fontSize: 14,
    color: "#4B5563",
    lineHeight: 20,
    paddingLeft: 22,
  },
  richTextCard: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
  },
  richHeading: {
    fontSize: 18,
    fontWeight: "800",
    color: "#1F2937",
    marginBottom: 10,
    marginTop: 4,
  },
  richSubHeading: {
    fontSize: 16,
    fontWeight: "700",
    color: "#374151",
    marginBottom: 8,
    marginTop: 4,
  },
  richParagraph: {
    fontSize: 14,
    color: "#374151",
    lineHeight: 24,
  },
});
