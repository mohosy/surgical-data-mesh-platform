package com.mohosy.queryservice;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class QueryServiceTest {

    private final QueryService queryService = new QueryService();

    @Test
    void searchFiltersByStep() {
        assertEquals(1, queryService.search("sutur").size());
    }

    @Test
    void timelineFiltersByPatient() {
        assertEquals(2, queryService.timeline("pat-1").size());
    }
}
