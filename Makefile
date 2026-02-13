.PHONY: test test-python test-java format

test: test-python test-java

test-python:
	cd services/ingest-service && python3 -m pytest -q
	cd services/indexer-service && python3 -m pytest -q
	cd jobs && python3 -m pytest -q

test-java:
	cd services/query-service-java && mvn -q test
