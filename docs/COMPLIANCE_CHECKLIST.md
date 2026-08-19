# PHFD Capital Live-Launch Compliance Checklist

This checklist is an operating gate, not legal advice. Colorado lending counsel and each contracted provider must approve the final structure.

## A. Product boundary

- [ ] Launch business-purpose financing only
- [ ] Remove all consumer/personal-loan marketing from MVP
- [ ] Define whether PHFD is a marketer, referral source, broker, service provider, lender, or program administrator in every route
- [ ] Confirm Colorado licensing implications for the actual activities and compensation structure
- [ ] Confirm provider state and product availability

## B. Partner agreement

- [ ] Identify legal lender/funder in every product
- [ ] Assign underwriting and final decision responsibility
- [ ] Assign disclosure responsibility
- [ ] Assign ECOA/Regulation B adverse-action responsibility
- [ ] Assign FCRA permissible-purpose and notice responsibility if reports are used
- [ ] Assign servicing, collections, complaints, fraud, and disputes
- [ ] Approve marketing language and brand presentation
- [ ] Define lead/referral compensation and clawbacks
- [ ] Execute data-processing agreement
- [ ] Execute security addendum and incident notification timeline

## C. Fair lending and underwriting

- [ ] No protected traits in the readiness score
- [ ] Review ZIP/geography and other proxy risks
- [ ] Document every score factor and weight
- [ ] Maintain model/version history
- [ ] Keep human review before partner referral
- [ ] Do not label readiness output as approval, denial, preapproval, rate, or offer
- [ ] Test reason codes for accuracy
- [ ] Create exception and override policy
- [ ] Monitor outcomes for unexplained disparities when enough data exists

## D. Consent and privacy

- [ ] Publish production privacy notice
- [ ] Capture affirmative partner-sharing consent
- [ ] Capture bank/payment-data connection consent separately
- [ ] Version and timestamp every consent
- [ ] Define retention and deletion periods
- [ ] Give users a process to access/correct data
- [ ] Limit internal access by role
- [ ] Complete Colorado Privacy Act applicability analysis
- [ ] Complete data-breach response plan
- [ ] Maintain vendor/subprocessor inventory

## E. Security

- [ ] Replace Basic Auth with OIDC/OAuth and MFA
- [ ] Replace SQLite with managed PostgreSQL
- [ ] Encrypt data in transit and at rest
- [ ] Use managed secrets storage
- [ ] Keep bank credentials inside provider-hosted components
- [ ] Encrypt documents with managed keys
- [ ] Add CSRF, rate limits, secure cookies, and security headers
- [ ] Add dependency and vulnerability scanning
- [ ] Add centralized logs without sensitive payloads
- [ ] Complete vendor SOC/security review
- [ ] Perform penetration test
- [ ] Define backup, recovery, and business-continuity plans

## F. Borrower communications

- [ ] Plain-language statement that PHFD profile is not a credit decision
- [ ] Identify actual provider before data transmission
- [ ] Show product type accurately, including advance vs. loan terminology
- [ ] Deliver required pricing and repayment disclosures through provider
- [ ] Preserve applicant communications and consent records
- [ ] Create complaint and escalation channel
- [ ] Prohibit promises of approval or guaranteed funding

## G. PHFD-owned microfund gate

- [ ] Obtain formal legal opinion on lending authority and licensing
- [ ] Approve credit policy
- [ ] Approve underwriting policy
- [ ] Form independent loan committee
- [ ] Approve conflicts-of-interest policy
- [ ] Secure lending capital and operating reserve
- [ ] Select origination/servicing system
- [ ] Approve loan documents and disclosures
- [ ] Establish accounting and reconciliation
- [ ] Establish delinquency, modification, collections, and charge-off policies
- [ ] Establish loss reserve methodology
- [ ] Obtain insurance
- [ ] Complete CDFI target-market and transaction-tracking design

## H. HFFI-specific program gate

- [ ] Keep Partnerships application centered on a multi-project Food Financing Program
- [ ] Lock a qualifying public entity in the partnership
- [ ] Lock a qualified lender before requesting Credit Enhancement
- [ ] Build current eligible-project pipeline
- [ ] Verify underserved-area methodology
- [ ] Verify SNAP requirements for direct retail
- [ ] Verify downstream SNAP-retailer requirements for supply-chain enterprises
- [ ] Separate free charitable food, pre-harvest agriculture, standalone kitchens, prepared-food-only models, and other ineligible primary activities
- [ ] Obtain signed partner commitment letters
- [ ] Map every capacity-building budget item to an eligible program function
