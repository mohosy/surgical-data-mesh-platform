package com.mohosy.queryservice;

import jakarta.validation.constraints.NotBlank;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@Validated
public class QueryController {

    private final QueryService queryService;

    public QueryController(QueryService queryService) {
        this.queryService = queryService;
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "ok", "service", "java-query-service");
    }

    @GetMapping("/search")
    public List<Map<String, Object>> search(@RequestParam @NotBlank String q) {
        return queryService.search(q);
    }

    @GetMapping("/patients/{patientId}/timeline")
    public List<Map<String, Object>> timeline(@PathVariable String patientId) {
        return queryService.timeline(patientId);
    }
}
