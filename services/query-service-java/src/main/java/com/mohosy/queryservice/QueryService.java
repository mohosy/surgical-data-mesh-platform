package com.mohosy.queryservice;

import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class QueryService {

    private final List<Map<String, Object>> fixtures = List.of(
            Map.of("eventId", "evt-1", "patientId", "pat-1", "step", "incision", "risk", "low", "latencyMs", 34, "forceNewtons", 12.0),
            Map.of("eventId", "evt-2", "patientId", "pat-1", "step", "dissection", "risk", "medium", "latencyMs", 86, "forceNewtons", 28.0),
            Map.of("eventId", "evt-3", "patientId", "pat-2", "step", "suturing", "risk", "high", "latencyMs", 158, "forceNewtons", 46.0),
            Map.of("eventId", "evt-4", "patientId", "pat-1", "step", "closure", "risk", "high", "latencyMs", 122, "forceNewtons", 42.0)
    );

    public List<Map<String, Object>> search(String q) {
        final String term = q.toLowerCase();
        return fixtures.stream()
                .filter(item -> item.get("step").toString().toLowerCase().contains(term)
                        || item.get("risk").toString().toLowerCase().contains(term))
                .collect(Collectors.toList());
    }

    public List<Map<String, Object>> timeline(String patientId) {
        return fixtures.stream()
                .filter(item -> item.get("patientId").equals(patientId))
                .collect(Collectors.toList());
    }

    public Map<String, Object> patientRiskSummary(String patientId) {
        List<Map<String, Object>> timeline = timeline(patientId);
        if (timeline.isEmpty()) {
            return Map.of(
                    "patientId", patientId,
                    "events", 0,
                    "highRiskEvents", 0,
                    "avgLatencyMs", 0.0,
                    "p95LatencyMs", 0.0,
                    "maxForceNewtons", 0.0
            );
        }

        List<Integer> latencies = timeline.stream()
                .map(item -> (Integer) item.get("latencyMs"))
                .sorted()
                .collect(Collectors.toList());
        List<Double> forces = timeline.stream()
                .map(item -> ((Number) item.get("forceNewtons")).doubleValue())
                .collect(Collectors.toList());
        long highRiskEvents = timeline.stream()
                .filter(item -> "high".equals(item.get("risk")) || "critical".equals(item.get("risk")))
                .count();

        double avgLatency = latencies.stream().mapToInt(Integer::intValue).average().orElse(0.0);
        int p95Index = (int) Math.round(0.95 * (latencies.size() - 1));
        double p95Latency = latencies.get(p95Index);
        double maxForce = forces.stream().mapToDouble(Double::doubleValue).max().orElse(0.0);

        return Map.of(
                "patientId", patientId,
                "events", timeline.size(),
                "highRiskEvents", highRiskEvents,
                "avgLatencyMs", round2(avgLatency),
                "p95LatencyMs", round2(p95Latency),
                "maxForceNewtons", round2(maxForce)
        );
    }

    public List<Map<String, Object>> topCriticalAlerts(int limit) {
        int bounded = Math.max(1, Math.min(50, limit));
        List<Map<String, Object>> ranked = new ArrayList<>(fixtures);
        ranked.sort(Comparator.comparingDouble(this::alertPriority).reversed());
        return ranked.stream().limit(bounded).collect(Collectors.toList());
    }

    private double alertPriority(Map<String, Object> item) {
        double force = ((Number) item.get("forceNewtons")).doubleValue();
        double latency = ((Number) item.get("latencyMs")).doubleValue();
        String risk = item.get("risk").toString().toLowerCase();
        double riskBoost = switch (risk) {
            case "critical" -> 45.0;
            case "high" -> 30.0;
            case "medium" -> 15.0;
            default -> 0.0;
        };
        return force * 0.8 + latency * 0.2 + riskBoost;
    }

    private double round2(double value) {
        return Math.round(value * 100.0) / 100.0;
    }
}
