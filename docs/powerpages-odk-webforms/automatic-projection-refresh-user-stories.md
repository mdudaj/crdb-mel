# Automatic Projection Refresh User Stories

## APR-US-01: New submission

As a monitoring user, I want a newly submitted record to appear in reporting automatically so that I do not depend on a developer rebuild.

## APR-US-02: Edited submission

As a monitoring user, I want an edit to replace the current projection for the same instance so that Data and exports show the latest version without duplicate roots.

## APR-US-03: Removed data

As a reporting analyst, I want answers and repeat rows removed by an edit to disappear from the current projection so that reports do not retain stale facts.

## APR-US-04: Submission isolation

As a field user, I want canonical submission to succeed even if reporting refresh fails so that analytics processing cannot lose field data.

## APR-US-05: Operations

As a platform administrator, I want correlation-safe traces, System Job failures, bounded retry, and a one-instance rebuild command so that I can diagnose and repair failures.

## APR-US-06: ALM and security

As a security/ALM owner, I want the plug-in and step solution-packaged and executed by a least-privilege user so that environments can be promoted without browser secrets or broad privileges.
