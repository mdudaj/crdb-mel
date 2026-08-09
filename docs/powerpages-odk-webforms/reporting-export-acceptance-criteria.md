# Reporting, Export, and Power BI Acceptance Criteria

- A signed-in user can open a **Data** area from the Monitoring Tool.
- The Data area lists submitted records from Dataverse reporting projections.
- The list supports search, date range filter, submitter filter, review state filter, and form version filter.
- Data pagination does not send the unsupported Dataverse `$skip` query option;
  page navigation returns the requested FetchXML `count`/`page` result.
- A record detail view shows submission metadata and flattened answer values from the latest current version.
- The reporting projection can be rebuilt from canonical `SubmissionVersions` without requiring the original browser session.
- Add-new submit refreshes the root reporting row for the new submission.
- Edit submit refreshes the existing reporting row for the same canonical `instance_id` and does not create a duplicate root report row.
- Repeat group data is represented as child reporting rows with stable join keys to the root submission.
- Export settings can be named and reused.
- New export names and downloaded filenames follow
  `<Form_Name>_YYYYMMDD_HHMMSS`, with spaces replaced by underscores.
- CSV export returns the filtered root dataset.
- XLSX export returns root data plus separate repeat sheets when repeat data exists.
- Export output includes generated timestamp, export name, form id, form version, and applied filters.
- The Power BI panel lists the Dataverse reporting tables and required user permissions.
- Power BI Desktop can connect through the Dataverse connector using an organizational account with read permissions.
- Portal code uses Power Pages `/_api`; it does not contain Dataverse client secrets, bearer tokens, or raw OAuth credentials.
- Browser UI has loading, empty, error, and permission-denied states for data list and export generation.
- Phone/tablet/desktop layouts do not overlap controls or truncate critical actions.
