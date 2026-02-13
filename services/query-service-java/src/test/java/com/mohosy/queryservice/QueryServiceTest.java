package com.mohosy.queryservice;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class QueryServiceTest {

    private final QueryService queryService = new QueryService();

    @Test
    void searchFiltersByStep() {
        assertEquals(1, queryService.search("sutur").size());
    }

    @Test
    void timelineFiltersByPatient() {
        assertEquals(3, queryService.timeline("pat-1").size());
    }

    @Test
    void summaryComputesRiskStats() {
        var summary = queryService.patientRiskSummary("pat-1");
        assertEquals(3, summary.get("events"));
        assertTrue(((Number) summary.get("maxForceNewtons")).doubleValue() >= 40.0);
        assertTrue(((Number) summary.get("highRiskEvents")).longValue() >= 1);
    }

    @Test
    void topAlertsReturnsBoundedList() {
        var alerts = queryService.topCriticalAlerts(2);
        assertEquals(2, alerts.size());
    }
}
