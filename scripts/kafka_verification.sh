#!/bin/bash
# OSIN-SVP-1 // Kafka Low-Level Verification Script

echo "---------------------------------------------------"
echo "🛰️ OSIN KAFKA VERIFICATION PROTOCOL (SVP-1)"
echo "---------------------------------------------------"

KAFKA_BROKER=${1:-"kafka:29092"}

# 1. Broker Readiness
echo "[1/4] CHECKING BROKER STATUS..."
# Using kafkacat (kcat) or native tools if available. Assuming native tools for now.
kafka-broker-api-versions --bootstrap-server "$KAFKA_BROKER" &> /dev/null
if [ $? -eq 0 ]; then
    echo "✅ BROKER REACHABLE: $KAFKA_BROKER"
else
    echo "❌ BROKER UNREACHABLE: $KAFKA_BROKER"
    exit 1
fi

# 2. Topic Audit
echo "[2/4] AUDITING OSIN INTELLIGENCE TOPICS..."
REQUIRED_TOPICS=(
    "osin.raw.satellite"
    "osin.raw.social"
    "osin.processed.nlp"
    "osin.processed.cv"
    "osin.alerts.high_priority"
    "osin.intelligence.events"
    "osin.health.check"
)

EXISTING_TOPICS=$(kafka-topics --list --bootstrap-server "$KAFKA_BROKER")

MISSING=0
for topic in "${REQUIRED_TOPICS[@]}"; do
    if echo "$EXISTING_TOPICS" | grep -q "$topic"; then
        echo "✅ TOPIC_OK: $topic"
    else
        echo "❌ TOPIC_MISSING: $topic"
        MISSING=$((MISSING + 1))
    fi
done

# 3. Flow Verification (Synthetic Inject)
echo "[3/4] TESTING MESSAGE PROPAGATION..."
TEST_ID="SVP1_VFY_$(date +%s)"
TEST_MSG='{"id":"'$TEST_ID'","type":"health_check","timestamp":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'","status":"VERIFYING"}'

echo "$TEST_MSG" | kafka-console-producer --bootstrap-server "$KAFKA_BROKER" --topic osin.health.check
if [ $? -eq 0 ]; then
    echo "✅ PRODUCTION_OK: Intelligence injected successfully."
else
    echo "❌ PRODUCTION_FAIL: Failed to inject telemetry."
    exit 1
fi

# 4. Consumption Baseline
echo "[4/4] VERIFYING CONSUMPTION PIPELINE..."
# Try to consume the message we just produced
CONSUME_RESULT=$(kafka-console-consumer --bootstrap-server "$KAFKA_BROKER" --topic osin.health.check --from-beginning --max-messages 1 --timeout-ms 5000 2>/dev/null)

if [[ "$CONSUME_RESULT" == *"$TEST_ID"* ]]; then
    echo "✅ CONSUMPTION_OK: Telemetry loopback confirmed."
else
    echo "❌ CONSUMPTION_FAIL: Message loopback timed out or ID mismatch."
    exit 1
fi

echo "---------------------------------------------------"
echo "📊 VERIFICATION STATUS: COMPLETE ($MISSING MISSING TOPICS)"
echo "---------------------------------------------------"
exit $MISSING
