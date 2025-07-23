prompt = """
          You are a system monitoring service that generates realistic infrastructure alerts.
          Generate {{ number }} different system alerts that could occur in a production environment.

          Alert Types: system failures, security incidents, performance issues, infrastructure problems, database issues, network problems, application errors.

          IMPORTANT: Return ONLY a valid JSON array. Do not include any other text, markdown formatting, or explanations. And always use double-quotes instead of single quotes => "" and not ''.

          Structure:
          Return a JSON array with alert objects. Each alert must have these fields:
          - alert_id: unique identifier
          - severity: "CRITICAL", "HIGH", "MEDIUM", "LOW"
          - alert_type: type of alert
          - system_component: affected system/service
          - description: detailed description of the issue
          - timestamp: ISO format timestamp
          - metrics: relevant performance data or error codes
          - affected_users: estimated number of affected users

          Examples:
          [
            {
              "alert_id": "ALT-20250122-001",
              "severity": "CRITICAL",
              "alert_type": "database_failure",
              "system_component": "user_database_cluster_03",
              "description": "Primary database node unresponsive, automatic failover initiated but queries timing out",
              "timestamp": "2025-01-22T14:23:17Z",
              "metrics": {"response_time_ms": 8500, "error_rate": 0.87, "connection_pool_usage": 0.98},
              "affected_users": 2400
            },
            {
              "alert_id": "ALT-20250122-002",
              "severity": "HIGH",
              "alert_type": "security_incident",
              "system_component": "api_gateway",
              "description": "Unusual spike in failed authentication attempts from multiple IP ranges, potential brute force attack",
              "timestamp": "2025-01-22T14:18:42Z",
              "metrics": {"failed_attempts_per_minute": 1200, "unique_ips": 47, "success_rate": 0.02},
              "affected_users": 0
            }
          ]

          Your Task:
          Generate {{ number }} realistic system alerts in the same JSON format:
          """
