using Microsoft.Xrm.Sdk;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.ServiceModel;

namespace Tacatdp.ReportingProjection.Plugin
{
    public sealed class ProjectionRefreshPlugin : PluginBase
    {
        public const string PostImageAlias = "SubmissionVersionImage";
        private const int PostOperationStage = 40;
        private const int AsynchronousMode = 1;
        private const int MaximumConvergencePasses = 3;

        private static readonly ISet<int> TransientFaultCodes = new HashSet<int>
        {
            unchecked((int)0x80072321),
            unchecked((int)0x80072322),
            unchecked((int)0x80072326),
        };

        public ProjectionRefreshPlugin()
            : base(typeof(ProjectionRefreshPlugin))
        {
        }

        public ProjectionRefreshPlugin(string unsecureConfiguration, string secureConfiguration)
            : this()
        {
        }

        protected override void ExecuteDataversePlugin(ILocalPluginContext localPluginContext)
        {
            if (localPluginContext == null)
            {
                throw new ArgumentNullException(nameof(localPluginContext));
            }

            var context = localPluginContext.PluginExecutionContext;
            ValidateRegistration(context);
            Entity image;
            if (!context.PostEntityImages.TryGetValue(PostImageAlias, out image) || image == null)
            {
                throw new InvalidPluginExecutionException("Projection refresh requires the registered SubmissionVersion post image.");
            }

            var instanceId = image.GetAttributeValue<string>("mp_instanceid") ?? string.Empty;
            if (instanceId.Length == 0)
            {
                throw new InvalidPluginExecutionException("SubmissionVersion is missing InstanceId.");
            }

            var triggerVersionId = image.Id == Guid.Empty ? context.PrimaryEntityId : image.Id;
            var repository = new DataverseProjectionRepository(localPluginContext.PluginUserService);
            var latestIdentity = repository.GetLatestVersionIdentity(instanceId);
            if (latestIdentity == null)
            {
                throw new InvalidPluginExecutionException("Latest SubmissionVersion was not found.");
            }
            if (!ProjectionCore.ShouldProcess(triggerVersionId, latestIdentity.Id))
            {
                localPluginContext.Trace($"Projection refresh skipped superseded trigger. correlation={context.CorrelationId} triggerVersion={triggerVersionId} latestVersion={latestIdentity.Id}");
                return;
            }

            try
            {
                var latest = repository.GetVersion(latestIdentity.Id);
                for (var pass = 1; pass <= MaximumConvergencePasses; pass++)
                {
                    var timer = Stopwatch.StartNew();
                    var source = repository.LoadSource(latest);
                    var projection = ProjectionCore.Build(source, DateTime.UtcNow);
                    var applied = repository.Apply(projection);
                    var latestAfterApply = repository.GetLatestVersionIdentity(instanceId);
                    timer.Stop();

                    localPluginContext.Trace(
                        $"Projection refresh pass completed. correlation={context.CorrelationId} version={source.SubmissionVersionId} " +
                        $"versionNumber={source.VersionNumber} status={projection.Report.ProjectionStatus} repeats={applied.RepeatCount} " +
                        $"answers={applied.AnswerCount} deletedRepeats={applied.DeletedRepeatCount} " +
                        $"deletedAnswers={applied.DeletedAnswerCount} elapsedMs={timer.ElapsedMilliseconds}");

                    if (latestAfterApply != null && latestAfterApply.Id == source.SubmissionVersionId)
                    {
                        return;
                    }
                    if (latestAfterApply == null)
                    {
                        throw new InvalidPluginExecutionException("Latest SubmissionVersion disappeared during projection refresh.");
                    }

                    latest = repository.GetVersion(latestAfterApply.Id);
                    localPluginContext.Trace($"Projection refresh converging to newer version. correlation={context.CorrelationId} nextVersion={latest.Id} pass={pass}");
                }

                throw CreateRetryException("Projection source changed repeatedly during refresh.");
            }
            catch (TimeoutException)
            {
                throw CreateRetryException("Projection refresh timed out during a Dataverse operation.");
            }
            catch (FaultException<OrganizationServiceFault> fault) when (TransientFaultCodes.Contains(fault.Detail.ErrorCode))
            {
                throw CreateRetryException("Projection refresh was throttled by Dataverse.");
            }
        }

        private static void ValidateRegistration(IPluginExecutionContext context)
        {
            if (!string.Equals(context.MessageName, "Create", StringComparison.OrdinalIgnoreCase)
                || !string.Equals(context.PrimaryEntityName, "mp_submissionversion", StringComparison.OrdinalIgnoreCase)
                || context.Stage != PostOperationStage
                || context.Mode != AsynchronousMode)
            {
                throw new InvalidPluginExecutionException("ProjectionRefreshPlugin registration does not match its Create/PostOperation/asynchronous contract.");
            }
        }

        private static InvalidPluginExecutionException CreateRetryException(string message)
        {
            return new InvalidPluginExecutionException(OperationStatus.Retry, 0, message);
        }
    }
}
