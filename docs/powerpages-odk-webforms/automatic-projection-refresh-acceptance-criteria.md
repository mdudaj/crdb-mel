# Automatic Projection Refresh Acceptance Criteria

| ID | Given / When / Then |
| --- | --- |
| APR-AC-01 | Given a valid new `SubmissionVersion`, when the async job completes, then one Ready root row and its expected answers/repeats reference that version. |
| APR-AC-02 | Given version N already projected, when version N+1 is created, then the same root alternate key points to N+1 and no second root exists. |
| APR-AC-03 | Given N+1 removes a root answer or repeat item, when refresh completes, then obsolete child rows from N are absent. |
| APR-AC-04 | Given the same event executes twice, when both jobs complete, then row counts and keys are unchanged after the first successful result. |
| APR-AC-05 | Given N+1 and N+2 jobs execute out of order, when both finish, then only N+2 is current and the N+1 job records a superseded no-op. |
| APR-AC-06 | Given malformed XML, when the job runs, then canonical rows remain committed, a Failed root is observable, and no XML/answers appear in traces. |
| APR-AC-07 | Given a transient Dataverse fault, when the plug-in classifies it as retryable, then async retry is bounded and the original submission remains committed. |
| APR-AC-08 | Given an unexpected failure exhausts retry, then a failed System Job contains correlation-safe diagnostics and the one-instance Python rebuild can repair the projection. |
| APR-AC-09 | Given Python and C# process the same root/repeat fixture, including a singleton nested repeat identified by metadata, then normalized keys, values, counts, parent relationships, and statuses match. |
| APR-AC-10 | Given an authenticated portal user submits or edits, then the browser makes no projection write and contains no projection credential. |
| APR-AC-11 | Deferred pending CRDB approval for `prvCreatePluginAssembly`. Until approval, CRDB-bound managed packages must exclude the plug-in assembly/type, step, and image; a later higher-version update will restore this criterion. |
| APR-AC-12 | Given the registered step, then it runs as the approved least-privilege user and succeeds without granting reporting writes to ordinary Power Pages users. |
| APR-AC-13 | Given a normal dev submission, then projection becomes visible within the two-minute acceptance window or a diagnosable System Job state exists. |
| APR-AC-14 | Given static analysis/tests, then the plug-in is stateless and uses neither parallel execution nor batch request message types. |
