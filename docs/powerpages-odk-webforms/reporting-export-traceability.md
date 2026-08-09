# Reporting, Export, and Power BI Traceability

| Requirement | Source Evidence | Planned Artifact | Verification |
| --- | --- | --- | --- |
| Keep canonical submissions separate from reporting data | ODK Central submission and OData docs | `Submissions`, `SubmissionVersions`, reporting projection tables | Rebuild projection from latest current versions |
| Root and repeat data must be relational | ODK Central OData repeat-table model; Kobo XLSX repeat sheets | root report rows plus repeat rows | XLSX includes root and repeat sheets; Power BI relationships work |
| Named export settings | Kobo synchronous export workflow | `ExportSettings` table or equivalent | User can save and rerun export configuration |
| Power BI primary path through governed tables | Microsoft Dataverse connector docs | Power BI panel and Dataverse reporting tables | Power BI connects with organizational account and read permissions |
| CSV/XLSX portal downloads | Kobo downloads and synchronous export pattern | portal export UX | CSV root export and XLSX multi-sheet export download |
| Security through Microsoft identity and Dataverse permissions | Power Pages and Dataverse project rules | table permissions, no anonymous export links | Source scan plus authenticated browser test |
| Edit submit updates projection without duplicate records | Existing TACATDP edit semantics | projection upsert keys | Edit creates version n+1 and updates one root reporting row |
