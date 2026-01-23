# Security Policy

## Supported Versions

The following versions of NewsDigest are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@newsdigest.dev**

Include the following information in your report:

- Type of vulnerability (e.g., injection, XSS, authentication bypass)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue and how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 48 hours.
- **Initial Assessment**: Within 7 days, we will provide an initial assessment of the report.
- **Updates**: We will keep you informed of our progress toward resolving the issue.
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days.
- **Credit**: We will credit you in our security advisories (unless you prefer to remain anonymous).

### Safe Harbor

We consider security research conducted in accordance with this policy to be:

- Authorized concerning any applicable anti-hacking laws
- Authorized concerning any relevant anti-circumvention laws
- Exempt from restrictions in our Terms of Service that would interfere with conducting security research

We will not pursue civil action or initiate a complaint to law enforcement for accidental, good-faith violations of this policy.

## Security Best Practices

When using NewsDigest, we recommend:

### API Keys and Secrets

- Never commit API keys or secrets to version control
- Use environment variables or a secrets manager
- Rotate API keys periodically
- Use the `.env.example` file as a template and create your own `.env` file

### Self-Hosted Deployments

- Keep NewsDigest updated to the latest version
- Use HTTPS for all API communications
- Implement proper firewall rules
- Enable rate limiting in production
- Review and restrict API key permissions

### Dependencies

- Regularly update dependencies using `pip install --upgrade`
- Review dependency security advisories
- Use `pip audit` or similar tools to check for known vulnerabilities

## Security Features

NewsDigest includes several security features:

- **Rate Limiting**: API endpoints include rate limiting to prevent abuse
- **Input Validation**: All user inputs are validated using Pydantic models
- **No Credential Storage**: NewsDigest does not store user credentials
- **HTTPS**: All external API communications use HTTPS
- **Dependency Scanning**: Automated dependency updates via Dependabot

## Known Security Considerations

- **URL Fetching**: NewsDigest fetches URLs provided by users. Ensure you trust the sources you analyze.
- **HTML Parsing**: While we sanitize HTML input, be cautious with untrusted content.
- **External APIs**: Third-party API integrations (NewsAPI, Twitter, etc.) are subject to their own security policies.

## Contact

For non-security-related issues, please use [GitHub Issues](https://github.com/kase1111-hash/NewsDigest/issues).

For security concerns, contact: **security@newsdigest.dev**
