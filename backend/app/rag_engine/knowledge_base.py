"""
OWASP & Security Knowledge Base for RAG retrieval.

Contains structured security knowledge about attack patterns,
OWASP Top 10, and common log anomaly signatures.
"""

SECURITY_KNOWLEDGE_BASE = [
    # ─── OWASP Top 10 ────────────────────────────────────────────────────────
    {
        "id": "owasp-a01",
        "title": "OWASP A01: Broken Access Control",
        "content": (
            "Broken Access Control occurs when restrictions on authenticated users are not properly enforced. "
            "Attackers can exploit these flaws to access unauthorized functionality or data, such as accessing "
            "other users' accounts, viewing sensitive files, or modifying other users' data. "
            "Log indicators: repeated 403 errors followed by 200 responses, access to /admin from non-admin IPs, "
            "horizontal privilege escalation (user accessing other user IDs), directory traversal patterns (../), "
            "abnormal off-hours access to sensitive endpoints."
        ),
        "category": "OWASP",
        "severity": "Critical",
        "fix": "Implement server-side access control checks, deny by default, log access control failures.",
    },
    {
        "id": "owasp-a02",
        "title": "OWASP A02: Cryptographic Failures",
        "content": (
            "Cryptographic failures expose sensitive data due to weak or missing encryption. "
            "Formerly known as Sensitive Data Exposure. "
            "Log indicators: HTTP (non-HTTPS) transmission of sensitive fields, use of deprecated ciphers (RC4, MD5, SHA1), "
            "plaintext passwords in logs, unencrypted database connections, cleartext API keys in request parameters."
        ),
        "category": "OWASP",
        "severity": "High",
        "fix": "Use TLS 1.2+, encrypt sensitive data at rest, avoid storing cleartext credentials, use strong hashing (Argon2, bcrypt).",
    },
    {
        "id": "owasp-a03",
        "title": "OWASP A03: Injection",
        "content": (
            "Injection flaws (SQL, NoSQL, OS, LDAP) occur when untrusted data is sent to an interpreter as part of a command or query. "
            "Log indicators: SQL keywords in request parameters (SELECT, UNION, DROP, INSERT), "
            "unusual characters in input (', --, ;, OR 1=1), "
            "error messages exposing database structure, elevated query execution time spikes, "
            "command injection patterns (;ls, |whoami, &&cat /etc/passwd)."
        ),
        "category": "OWASP",
        "severity": "Critical",
        "fix": "Use parameterized queries/prepared statements, input validation, least-privilege DB accounts.",
    },
    {
        "id": "owasp-a04",
        "title": "OWASP A04: Insecure Design",
        "content": (
            "Insecure design refers to missing or ineffective control design, distinct from implementation bugs. "
            "Log indicators: bypassing business logic flows, excessive API calls outside normal user flows, "
            "repeated access to rate-limiting endpoints without triggering limits."
        ),
        "category": "OWASP",
        "severity": "High",
        "fix": "Threat modeling, secure design patterns, reference architectures, limit resource consumption per user.",
    },
    {
        "id": "owasp-a05",
        "title": "OWASP A05: Security Misconfiguration",
        "content": (
            "Security misconfiguration is the most commonly seen issue. "
            "Log indicators: default credentials used, unnecessary features enabled (debug endpoints, stack traces), "
            "directory listing enabled, default admin pages accessible, verbose error messages with system info, "
            "unnecessary open ports, missing security headers (X-Frame-Options, CSP, HSTS)."
        ),
        "category": "OWASP",
        "severity": "High",
        "fix": "Hardened configuration baselines, remove defaults, disable debug features in production.",
    },
    {
        "id": "owasp-a07",
        "title": "OWASP A07: Identification and Authentication Failures",
        "content": (
            "Authentication failures enable attackers to compromise accounts. "
            "Log indicators: brute force patterns (many failed logins from same IP), "
            "credential stuffing (many accounts from one IP), "
            "unusual geographic login (new country/city), "
            "session token reuse after logout, "
            "password reset abuse, "
            "weak password acceptance, "
            "missing MFA bypass attempts."
        ),
        "category": "OWASP",
        "severity": "Critical",
        "fix": "Implement MFA, rate limiting on login, account lockout, strong password policy, monitor anomalous logins.",
    },
    # ─── Common Attack Patterns ───────────────────────────────────────────────
    {
        "id": "attack-brute-force",
        "title": "Brute Force Attack",
        "content": (
            "A brute force attack attempts many password combinations to gain unauthorized access. "
            "Log indicators: high rate of failed authentication attempts (>10/min) from one source IP, "
            "sequential username enumeration, repeated 401/403 responses, "
            "automated timing patterns (equal intervals between requests), "
            "high volume of authentication requests at unusual hours."
        ),
        "category": "Attack Pattern",
        "severity": "High",
        "fix": "Implement account lockout, CAPTCHA, rate limiting, IP-based throttling, MFA enforcement.",
    },
    {
        "id": "attack-dos",
        "title": "Denial of Service (DoS / DDoS)",
        "content": (
            "DoS attacks overwhelm systems with traffic to disrupt service. "
            "Log indicators: extreme spike in request rate from one or many IPs, "
            "repeated requests to resource-intensive endpoints, "
            "SYN flood patterns (many half-open connections), "
            "HTTP flood (same URL hammered repeatedly), "
            "unusually large request payloads, dramatic latency increase."
        ),
        "category": "Attack Pattern",
        "severity": "Critical",
        "fix": "Web Application Firewall (WAF), rate limiting, CDN with DDoS protection, auto-scaling, CAPTCHA.",
    },
    {
        "id": "attack-port-scan",
        "title": "Port Scanning / Network Reconnaissance",
        "content": (
            "Attackers scan networks to discover open services and vulnerabilities. "
            "Log indicators: sequential connection attempts across many ports from one source, "
            "ICMP sweeps, SYN packets without completing handshake, "
            "connection attempts to closed ports, network scanner user-agent strings (nmap, masscan)."
        ),
        "category": "Attack Pattern",
        "severity": "Medium",
        "fix": "Firewall rules, IDS/IPS, network segmentation, port knocking, hide sensitive services.",
    },
    {
        "id": "attack-data-exfil",
        "title": "Data Exfiltration",
        "content": (
            "Data exfiltration is the unauthorized transfer of data from a system. "
            "Log indicators: unusually large outbound data transfers, "
            "high volume of database queries in short time, "
            "DNS tunneling patterns (very long DNS queries), "
            "access to sensitive files followed by external connections, "
            "off-hours bulk downloads, "
            "access to data by user with no business need."
        ),
        "category": "Attack Pattern",
        "severity": "Critical",
        "fix": "DLP solutions, egress filtering, data access monitoring, network anomaly detection.",
    },
    {
        "id": "attack-xss",
        "title": "Cross-Site Scripting (XSS)",
        "content": (
            "XSS attacks inject malicious scripts into web pages viewed by other users. "
            "Log indicators: script tags in request parameters (<script>, javascript:, onerror=), "
            "encoded payloads (%3Cscript%3E), event handlers in parameters, "
            "unusual characters in URL or form fields."
        ),
        "category": "Attack Pattern",
        "severity": "High",
        "fix": "Content Security Policy headers, output encoding, input validation, HTTPOnly cookies.",
    },
    {
        "id": "attack-privilege-escalation",
        "title": "Privilege Escalation",
        "content": (
            "Privilege escalation is gaining higher access rights than intended. "
            "Log indicators: sudo commands from unexpected users, "
            "role or permission changes outside change management windows, "
            "accessing admin APIs without admin role, "
            "SUID/SGID binary execution, kernel exploit attempts."
        ),
        "category": "Attack Pattern",
        "severity": "Critical",
        "fix": "Principle of least privilege, PAM controls, sudo auditing, privileged access management (PAM).",
    },
    {
        "id": "anomaly-traffic-spike",
        "title": "Abnormal Traffic Volume",
        "content": (
            "Sudden spikes in network or application traffic can indicate attacks or system compromise. "
            "Statistical anomalies in request counts, response sizes, or error rates should be investigated. "
            "A system with normally stable 100 req/min baseline spiking to 10000 req/min warrants immediate review."
        ),
        "category": "Anomaly Pattern",
        "severity": "Medium",
        "fix": "Baseline traffic modeling, auto-alerting on z-score deviations, rate limiting.",
    },
    {
        "id": "anomaly-off-hours",
        "title": "Off-Hours System Activity",
        "content": (
            "Legitimate system activity follows predictable business-hours patterns. "
            "Anomalous logins, data access, or configuration changes at unusual times (nights, weekends) "
            "may indicate insider threats, compromised credentials, or automated attacker activity. "
            "Log indicators: access outside business hours, logins from new locations, admin activity without scheduled maintenance."
        ),
        "category": "Anomaly Pattern",
        "severity": "Medium",
        "fix": "Time-based access controls, anomaly alerting, privileged session recording.",
    },
]
