# Security notes

## Supported security controls
- Passwords are stored using Argon2 hashes through pwdlib; plaintext passwords are never persisted.
- Session JWTs are short-lived and held in HttpOnly cookies. The frontend does not read or store the token in localStorage/sessionStorage.
- Cookies use SameSite=Strict. Production must serve over HTTPS and set COOKIE_SECURE=true. State-changing browser requests with an Origin or Referer header are checked against configured CORS origins.
- Protected analysis and history routes require a valid active account.
- History queries are filtered by the authenticated user ID. Unowned legacy rows are not returned to any user.
- Redis rate limits apply to registration, login and analysis endpoints; a Redis failure causes a fail-closed 503.
- URL fetching rejects non-HTTP(S), embedded credentials, private/non-global DNS results, redirect chains beyond the configured hop limit, non-HTML content and bodies larger than 3 MB.
- The outbound connection uses the validated IP address directly while preserving the original hostname for TLS certificate validation and HTTP Host routing.
- Environment proxy variables are disabled for user-supplied URL fetches.

## Deployment requirements
1. Terminate HTTPS at a trusted reverse proxy and set COOKIE_SECURE=true.
2. Keep API and frontend on the same site when using SameSite=Strict cookies; otherwise design and test an explicit CSRF token and Origin validation strategy.
3. Set a unique JWT_SECRET_KEY of at least 32 random bytes. Never commit .env files or provider credentials.
4. Keep PostgreSQL and Redis private; do not publish their ports to the internet.
5. Configure a trusted reverse proxy and do not trust arbitrary X-Forwarded-For headers. Current rate limits use the direct ASGI client IP.
6. Apply outbound network egress policy as defense in depth, especially for metadata and private network ranges.
7. Rotate provider credentials and signing keys; use a managed secret store in deployed environments.
8. Back up PostgreSQL and test restoration.

## External data processing

When configured, candidate claim text and retrieved page excerpts are sent to Google Fact Check Tools, Tavily Search and/or Hugging Face Inference Providers. Do not submit confidential, regulated or sensitive material unless the deployment has reviewed the providers' terms, retention settings, data-processing agreements and applicable privacy requirements. Provider credentials remain server-side.

## Residual risks
- Email verification, password reset, account deletion, session revocation, account-based quotas and audit events are not implemented.
- SameSite cookies and the application Origin check reduce cross-site request exposure; deployments should still enforce trusted-origin/CSRF policy at the edge, especially when frontend and API are on different sites. Requests without Origin/Referer are allowed for non-browser API clients.
- IP-based limits can penalize users behind shared NAT and can be evaded by distributed clients.
- A URL can be safe at fetch time but contain untrusted or malicious page content. Treat all extracted text and third-party review metadata as untrusted data.
- Search snippets and publisher ratings are research material, not proof. No independent semantic evidence adjudicator or editorial review queue exists yet.
- This repository has not undergone an external penetration test or formal security audit.

## Reporting
Please do not publish exploitable vulnerabilities as public issues. Contact the repository maintainer privately with reproduction steps and affected commit.