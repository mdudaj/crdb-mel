using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Web.Script.Serialization;
using Microsoft.Xrm.Sdk;
using Microsoft.Xrm.Sdk.Query;

namespace Tacatdp.IndicatorSeedPackage
{
    internal sealed class IndicatorSeedDeployer
    {
        internal const string SeedFileName = "indicator-evidence-seed.json";

        private static readonly Dictionary<string, int> IndicatorTypes = new Dictionary<string, int>
        {
            ["Financial"] = 100000000,
            ["Output"] = 100000001,
            ["Outcome"] = 100000002,
            ["ClimateImpactEstimate"] = 100000003,
            ["OperationalDataQuality"] = 100000004
        };

        private static readonly Dictionary<string, int> ResultLevels = new Dictionary<string, int>
        {
            ["Programme"] = 100000000,
            ["Component"] = 100000001,
            ["Outcome"] = 100000002,
            ["Output"] = 100000003,
            ["Activity"] = 100000004,
            ["Operational"] = 100000005
        };

        private static readonly Dictionary<string, int> ReportingFrequencies = new Dictionary<string, int>
        {
            ["OnDemand"] = 100000000,
            ["Weekly"] = 100000001,
            ["Monthly"] = 100000002,
            ["Quarterly"] = 100000003,
            ["Seasonal"] = 100000004,
            ["Annual"] = 100000005,
            ["Baseline"] = 100000006,
            ["Endline"] = 100000007
        };

        private static readonly Dictionary<string, int> DefinitionStatuses = new Dictionary<string, int>
        {
            ["Draft"] = 100000000,
            ["Active"] = 100000001,
            ["Retired"] = 100000002
        };

        private static readonly Dictionary<string, int> SourceTypes = new Dictionary<string, int>
        {
            ["XFormField"] = 100000000,
            ["ImportedFileColumn"] = 100000001,
            ["DataverseTable"] = 100000002,
            ["PowerAutomateFlow"] = 100000003,
            ["PowerBIModel"] = 100000004,
            ["ExternalIntegration"] = 100000005
        };

        private readonly IOrganizationService service;

        internal IndicatorSeedDeployer(IOrganizationService service)
        {
            this.service = service ?? throw new ArgumentNullException(nameof(service));
        }

        internal void Deploy(string seedPath)
        {
            if (!File.Exists(seedPath))
            {
                throw new FileNotFoundException("The indicator seed file was not found.", seedPath);
            }

            var serializer = new JavaScriptSerializer { MaxJsonLength = int.MaxValue, RecursionLimit = 256 };
            var seed = serializer.Deserialize<Dictionary<string, object>>(File.ReadAllText(seedPath, Encoding.UTF8));
            var projectCode = GetString(seed, "target_project_code");
            if (string.IsNullOrWhiteSpace(projectCode))
            {
                throw new InvalidDataException("Indicator seed target_project_code is required.");
            }

            var projectId = RequireId("mp_project", new ConditionExpression("mp_projectcode", ConditionOperator.Equal, projectCode));
            var definitions = seed.ContainsKey("indicator_definitions") ? seed["indicator_definitions"] as IEnumerable : null;
            if (definitions == null)
            {
                throw new InvalidDataException("Indicator seed has no indicator_definitions array.");
            }

            var definitionCount = 0;
            var mappingCount = 0;
            foreach (var item in definitions)
            {
                var definition = item as Dictionary<string, object>;
                if (definition == null)
                {
                    throw new InvalidDataException("Indicator seed contains an invalid indicator definition.");
                }

                var definitionId = UpsertDefinition(definition, projectId);
                definitionCount++;

                var mappings = definition.ContainsKey("mappings") ? definition["mappings"] as IEnumerable : null;
                if (mappings == null)
                {
                    throw new InvalidDataException("Indicator definition has no mappings array.");
                }

                foreach (var mappingItem in mappings)
                {
                    var mapping = mappingItem as Dictionary<string, object>;
                    if (mapping == null)
                    {
                        throw new InvalidDataException("Indicator seed contains an invalid data-source mapping.");
                    }
                    UpsertMapping(mapping, projectId, definitionId);
                    mappingCount++;
                }
            }

            VerifySeed(projectId, definitionCount, mappingCount);
            Trace.TraceInformation("TACATDP indicator seed rows upserted. Definitions: " + definitionCount + ", mappings: " + mappingCount + ".");
        }

        private Guid UpsertDefinition(Dictionary<string, object> definition, Guid projectId)
        {
            var code = RequireString(definition, "code");
            var entity = new Entity("mp_indicatordefinition")
            {
                ["mp_project"] = new EntityReference("mp_project", projectId),
                ["mp_code"] = code,
                ["mp_name"] = RequireString(definition, "name"),
                ["mp_description"] = GetString(definition, "description"),
                ["mp_indicatortype"] = new OptionSetValue(Choice(IndicatorTypes, RequireString(definition, "indicator_type"), "indicator_type")),
                ["mp_resultlevel"] = new OptionSetValue(Choice(ResultLevels, RequireString(definition, "result_level"), "result_level")),
                ["mp_unit"] = RequireString(definition, "unit"),
                ["mp_formula"] = GetString(definition, "formula"),
                ["mp_numerator"] = GetString(definition, "numerator"),
                ["mp_denominator"] = GetString(definition, "denominator"),
                ["mp_reportingfrequency"] = new OptionSetValue(Choice(ReportingFrequencies, RequireString(definition, "reporting_frequency"), "reporting_frequency")),
                ["mp_disaggregationjson"] = SerializeArray(definition, "disaggregation"),
                ["mp_datasourcemappingjson"] = SerializeArray(definition, "mappings"),
                ["mp_verificationmethod"] = GetString(definition, "verification_method"),
                ["mp_responsibleunit"] = GetString(definition, "responsible_unit"),
                ["mp_reportingframework"] = GetString(definition, "reporting_framework"),
                ["mp_status"] = new OptionSetValue(Choice(DefinitionStatuses, RequireString(definition, "status"), "status"))
            };

            return UpsertBy(
                entity,
                new ConditionExpression("mp_project", ConditionOperator.Equal, projectId),
                new ConditionExpression("mp_code", ConditionOperator.Equal, code));
        }

        private void UpsertMapping(Dictionary<string, object> mapping, Guid projectId, Guid definitionId)
        {
            var mappingKey = RequireString(mapping, "mapping_key");
            var entity = new Entity("mp_datasourcemapping")
            {
                ["mp_mappingkey"] = mappingKey,
                ["mp_project"] = new EntityReference("mp_project", projectId),
                ["mp_indicatordefinition"] = new EntityReference("mp_indicatordefinition", definitionId),
                ["mp_sourcetype"] = new OptionSetValue(Choice(SourceTypes, RequireString(mapping, "source_type"), "source_type")),
                ["mp_sourcetable"] = GetString(mapping, "source_table"),
                ["mp_sourcecolumn"] = GetString(mapping, "source_column"),
                ["mp_sourcepath"] = GetString(mapping, "source_path"),
                ["mp_transformrule"] = GetString(mapping, "transform_rule"),
                ["mp_required"] = ToYesNo(mapping, "required"),
                ["mp_active"] = ToYesNo(mapping, "active"),
                ["mp_notes"] = GetString(mapping, "notes")
            };

            UpsertBy(entity, new ConditionExpression("mp_mappingkey", ConditionOperator.Equal, mappingKey));
        }

        private Guid UpsertBy(Entity entity, params ConditionExpression[] conditions)
        {
            var id = FindId(entity.LogicalName, conditions);
            if (id.HasValue)
            {
                entity.Id = id.Value;
                service.Update(entity);
                return id.Value;
            }

            return service.Create(entity);
        }

        private Guid RequireId(string logicalName, params ConditionExpression[] conditions)
        {
            var id = FindId(logicalName, conditions);
            if (!id.HasValue)
            {
                throw new InvalidOperationException("Required Dataverse row not found: " + logicalName);
            }

            return id.Value;
        }

        private Guid? FindId(string logicalName, params ConditionExpression[] conditions)
        {
            var query = new QueryExpression(logicalName)
            {
                ColumnSet = new ColumnSet(false),
                TopCount = 1
            };
            foreach (var condition in conditions)
            {
                query.Criteria.AddCondition(condition);
            }

            var rows = service.RetrieveMultiple(query).Entities;
            return rows.Count == 0 ? (Guid?)null : rows[0].Id;
        }

        private int Count(string logicalName, params ConditionExpression[] conditions)
        {
            var query = new QueryExpression(logicalName)
            {
                ColumnSet = new ColumnSet(false)
            };
            foreach (var condition in conditions)
            {
                query.Criteria.AddCondition(condition);
            }
            return service.RetrieveMultiple(query).Entities.Count;
        }

        private void VerifySeed(Guid projectId, int expectedDefinitions, int expectedMappings)
        {
            var actualDefinitions = Count("mp_indicatordefinition", new ConditionExpression("mp_project", ConditionOperator.Equal, projectId));
            if (actualDefinitions < expectedDefinitions)
            {
                throw new InvalidOperationException("Indicator definition seed verification failed.");
            }

            var actualMappings = Count("mp_datasourcemapping", new ConditionExpression("mp_project", ConditionOperator.Equal, projectId));
            if (actualMappings < expectedMappings)
            {
                throw new InvalidOperationException("Data source mapping seed verification failed.");
            }
        }

        private static string RequireString(Dictionary<string, object> source, string key)
        {
            var value = GetString(source, key);
            if (string.IsNullOrWhiteSpace(value))
            {
                throw new InvalidDataException("Required seed value missing: " + key);
            }
            return value;
        }

        private static string GetString(Dictionary<string, object> source, string key)
        {
            if (!source.ContainsKey(key) || source[key] == null)
            {
                return string.Empty;
            }
            return Convert.ToString(source[key]) ?? string.Empty;
        }

        private static string SerializeArray(Dictionary<string, object> source, string key)
        {
            if (!source.ContainsKey(key) || source[key] == null)
            {
                return "[]";
            }
            return new JavaScriptSerializer { MaxJsonLength = int.MaxValue }.Serialize(source[key]);
        }

        private static int Choice(Dictionary<string, int> choices, string value, string field)
        {
            if (!choices.ContainsKey(value))
            {
                throw new InvalidDataException("Invalid seed choice for " + field + ": " + value);
            }
            return choices[value];
        }

        private static OptionSetValue ToYesNo(Dictionary<string, object> source, string key)
        {
            if (!source.ContainsKey(key))
            {
                throw new InvalidDataException("Required boolean seed value missing: " + key);
            }
            return new OptionSetValue(Convert.ToBoolean(source[key]) ? 100000001 : 100000000);
        }
    }
}
