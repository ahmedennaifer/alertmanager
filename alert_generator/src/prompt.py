prompt = """
You are a system monitoring service. Generate infrastructure alerts.

CRITICAL INSTRUCTIONS:
1. Generate EXACTLY {{ number }} infrastructure alerts
2. Respond with ONLY valid JSON - NO markdown, NO explanations, NO other text
3. Use double quotes ("") only, never single quotes ('')
4. Start response with { and end with }
5. Do not include ```json or any formatting

REQUIRED JSON OBJECT FORMAT:
{
  "alerts": [
    {
      "alert_id": ALT-SERVICE-TIMESTAMP-UNIQUEIDENTIFIER
      "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
      "service": "payments|auth|orders|search|inventory|notifications",
      "severity": "critical|high|medium|low",
      "status": "active|resolved",
      "response_time_ms": "number_50_to_5000",
      "error_count": "number_0_to_500",
      "total_requests": "number_100_to_10000",
      "resolution_minutes": "number_5_to_300_or_null_if_active"
    }
  ]
}

STRICT RULES:
- Use ONLY the exact values listed for service/severity/status
- If status="active" then resolution_minutes=null
- If status="resolved" then resolution_minutes=number
- error_count MUST be <= total_requests
- Higher severity correlates with higher error_count and response_time_ms
- Each alert must have ALL 8 fields
- No additional fields allowed

SEVERITY DISTRIBUTION:
- critical: 15% (status usually "active", high error rates)
- high: 25% (mix of active/resolved)
- medium: 45% (mostly resolved)
- low: 15% (all resolved)

VALID EXAMPLE OUTPUT:
{
  "alerts": [
    {
      "alert_id":  "ALT-AUTH-20250129-FTZ263
      "timestamp": "2025-01-29T14:23:45Z",
      "service": "payments",
      "severity": "critical",
      "status": "active",
      "response_time_ms": 3400,
      "error_count": 145,
      "total_requests": 1500,
      "resolution_minutes": null
    },
    {
      "alert_id":  "ALT-AUTH-20250129-XYZY33
      "timestamp": "2025-01-29T14:18:30Z",
      "service": "auth",
      "severity": "medium",
      "status": "resolved",
      "response_time_ms": 850,
      "error_count": 12,
      "total_requests": 2000,
      "resolution_minutes": 25
    }
  ]
}

RESPOND WITH ONLY THE JSON OBJECT FOR {{ number }} ALERTS:
"""
