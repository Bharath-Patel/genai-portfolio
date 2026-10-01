#!/usr/bin/env bash
# cost_check.sh - "where is the money going?" for the SageMaker monitor lab.
#
# READ-ONLY: every command here only lists / describes / reads cost data.
# Usage:   bash cost_check.sh [endpoint-name]
#
# An "AccessDenied" line means "this user isn't allowed to look here",
# NOT "nothing there" - check that spot in the console or as root instead.
#
# Cost Explorer API calls are billed (about $0.01 each). Sections 4 and 5 make
# 2 calls per day shown, so DAYS=3 costs roughly $0.08 per run.

export AWS_PAGER=""        # stop the CLI opening a pager (looks like a freeze)
REGION=us-east-1
DAYS=3                     # days back to show in sections 4 and 5
ENDPOINT="${1:-}"          # optional: an endpoint name to inspect in section 1

TAB="$(printf '\t')"
section() { printf '\n\n=== %s ===\n' "$1"; }
day()     { python3 -c "import datetime as d; print(d.date.today() - d.timedelta(days=$1))"; }

# ---------------------------------------------------------------- 1
section "1. SageMaker endpoints (billed per hour for as long as they exist)"
aws sagemaker list-endpoints --region $REGION \
  --query "Endpoints[].[EndpointName,EndpointStatus,CreationTime]" --output table

if [ -n "$ENDPOINT" ]; then
  echo; echo "-- details for $ENDPOINT"
  aws sagemaker describe-endpoint --endpoint-name "$ENDPOINT" --region $REGION \
    --query "{Name:EndpointName,Status:EndpointStatus,Created:CreationTime,Config:EndpointConfigName}" --output table
  CFG=$(aws sagemaker describe-endpoint --endpoint-name "$ENDPOINT" --region $REGION \
    --query EndpointConfigName --output text)
  aws sagemaker describe-endpoint-config --endpoint-config-name "$CFG" --region $REGION \
    --query "ProductionVariants[].{Variant:VariantName,InstanceType:InstanceType,Count:InitialInstanceCount}" --output table
fi

# ---------------------------------------------------------------- 2
section "2. Other SageMaker things that bill while they run"
echo "-- monitoring schedules"
aws sagemaker list-monitoring-schedules --region $REGION \
  --query "MonitoringScheduleSummaries[].[MonitoringScheduleName,MonitoringScheduleStatus,EndpointName]" --output table
echo "-- processing jobs in progress"
aws sagemaker list-processing-jobs --status-equals InProgress --region $REGION \
  --query "ProcessingJobSummaries[].[ProcessingJobName,CreationTime]" --output table
echo "-- training jobs in progress"
aws sagemaker list-training-jobs --status-equals InProgress --region $REGION \
  --query "TrainingJobSummaries[].[TrainingJobName,CreationTime]" --output table
echo "-- notebook instances"
aws sagemaker list-notebook-instances --region $REGION \
  --query "NotebookInstances[].[NotebookInstanceName,NotebookInstanceStatus,InstanceType]" --output table
echo "-- Studio domains"
aws sagemaker list-domains --region $REGION \
  --query "Domains[].[DomainId,Status]" --output table
echo "-- Studio apps still running"
aws sagemaker list-apps --region $REGION \
  --query "Apps[?Status=='InService'].[DomainId,SpaceName,AppType,ResourceSpec.InstanceType]" --output table

# ---------------------------------------------------------------- 3
for r in us-east-1 us-east-2; do
  section "3. Leftovers sweep in $r (from earlier labs: EKS, OpenSearch, EC2, load balancers)"
  echo "-- SageMaker endpoints"
  aws sagemaker list-endpoints --region $r --query "Endpoints[].[EndpointName,EndpointStatus]" --output text
  echo "-- EKS clusters"
  aws eks list-clusters --region $r --query "clusters" --output text
  echo "-- OpenSearch Serverless collections"
  aws opensearchserverless list-collections --region $r --query "collectionSummaries[].[name,status]" --output text
  echo "-- running EC2 instances"
  aws ec2 describe-instances --region $r --filters Name=instance-state-name,Values=running \
    --query "Reservations[].Instances[].[InstanceId,InstanceType]" --output text
  echo "-- classic load balancers"
  aws elb describe-load-balancers --region $r --query "LoadBalancerDescriptions[].LoadBalancerName" --output text
  echo "-- application/network load balancers"
  aws elbv2 describe-load-balancers --region $r --query "LoadBalancers[].LoadBalancerName" --output text
done

# ---------------------------------------------------------------- 4
# Credits are filtered OUT so you see gross usage. On a credit-covered account the
# NET cost can look like $0 while the usage underneath is real.
NO_CREDITS='{"Not":{"Dimensions":{"Key":"RECORD_TYPE","Values":["Credit","Refund"]}}}'

section "4. Cost per service, per day (gross usage; today is usually incomplete)"
for n in $(seq $DAYS -1 0); do
  s=$(day $n); e=$(day $((n-1)))
  echo; echo "-- $s"
  aws ce get-cost-and-usage --region us-east-1 --time-period Start=$s,End=$e --granularity DAILY \
    --metrics UnblendedCost --group-by Type=DIMENSION,Key=SERVICE --filter "$NO_CREDITS" \
    --query 'ResultsByTime[0].Groups[?to_number(Metrics.UnblendedCost.Amount)>`0.005`].[Keys[0],Metrics.UnblendedCost.Amount]' \
    --output text | sort -t "$TAB" -k2 -nr | awk -F'\t' '{printf "   %-52s $%8.2f\n", $1, $2}'
done

# ---------------------------------------------------------------- 5
SM_ONLY='{"And":[{"Dimensions":{"Key":"SERVICE","Values":["Amazon SageMaker"]}},{"Not":{"Dimensions":{"Key":"RECORD_TYPE","Values":["Credit","Refund"]}}}]}'

section "5. SageMaker only: cost and hours by usage type (Host=endpoint, Train=training, Proc=processing)"
for n in $(seq $DAYS -1 0); do
  s=$(day $n); e=$(day $((n-1)))
  echo; echo "-- $s"
  aws ce get-cost-and-usage --region us-east-1 --time-period Start=$s,End=$e --granularity DAILY \
    --metrics UnblendedCost UsageQuantity --group-by Type=DIMENSION,Key=USAGE_TYPE --filter "$SM_ONLY" \
    --query 'ResultsByTime[0].Groups[?to_number(Metrics.UnblendedCost.Amount)>`0.005`].[Keys[0],Metrics.UnblendedCost.Amount,Metrics.UsageQuantity.Amount]' \
    --output text | sort -t "$TAB" -k2 -nr | awk -F'\t' '{printf "   %-46s $%7.2f  %8.2f units\n", $1, $2, $3}'
done

echo
echo "Sanity check: for a Host: line, cost / units = your effective hourly rate,"
echo "and units should roughly equal hours the endpoint existed x instance count."