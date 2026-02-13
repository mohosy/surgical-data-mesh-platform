package com.mohosy.queryservice;

import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class QueryService {

    private final List<Map<String, Object>> fixtures = List.of(
            Map.of("eventId", "evt-1", "patientId", "pat-1", "step", "incision", "risk", "low"),
            Map.of("eventId", "evt-2", "patientId", "pat-1", "step", "dissection", "risk", "medium"),
            Map.of("eventId", "evt-3", "patientId", "pat-2", "step", "suturing", "risk", "high")
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
}
