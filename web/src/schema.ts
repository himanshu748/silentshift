import { z } from "zod";

export const JsonObject = z.record(z.string(), z.unknown());
const Text = z.string().min(1);
const Timestamp = Text.refine(
  (value) => Number.isFinite(Date.parse(value)),
  "Expected an ISO timestamp",
);
export const Decision = z.enum(["ALLOW", "QUARANTINE", "REQUEST_REVIEW"]);
export type Decision = z.infer<typeof Decision>;

const Finding = z
  .object({
    code: Text,
    field: Text,
    observed: z.unknown(),
    expected: z.unknown(),
    severity: z.enum(["critical", "warning", "info"]),
    evidence_ids: z.array(Text),
    explanation: Text,
  })
  .passthrough();

export const CaseSchema = z
  .object({
    id: Text,
    event_id: Text,
    source: Text,
    received_at: Timestamp,
    version: z.number().int().nonnegative(),
    message: JsonObject,
    references: z.array(JsonObject),
    assessment: z
      .object({
        classification: Text,
        findings: z.array(Finding),
        evidence_ids: z.array(Text),
        critical: z.boolean(),
      })
      .passthrough()
      .nullable(),
    recommendation: JsonObject.nullable(),
    agent: JsonObject.nullable(),
    policy: z
      .object({
        decision: Decision,
        reasons: z.array(z.string()),
        checks: z.union([JsonObject, z.array(JsonObject)]),
        policy_version: Text,
      })
      .passthrough()
      .nullable(),
    routing: z.enum([
      "PROCESSING",
      "DELIVERED",
      "QUARANTINED",
      "REVIEW",
      "REJECTED",
    ]),
    events: z.array(
      z
        .object({
          id: z.union([Text, z.number()]),
          kind: Text,
          at: Timestamp,
          detail: JsonObject,
        })
        .passthrough(),
    ),
    trace_id: z.union([z.string(), z.number()]).nullable(),
    trace_url: z.string().optional(),
    review: JsonObject.nullable(),
  })
  .passthrough();
export type Investigation = z.infer<typeof CaseSchema>;

export const CasesSchema = z
  .object({
    items: z.array(CaseSchema),
    total: z.number().int().nonnegative(),
    limit: z.number().int().positive(),
    offset: z.number().int().nonnegative(),
  })
  .passthrough();

export const HealthSchema = z
  .object({
    build: Text,
    production: z.object({ running: z.boolean(), name: Text }).passthrough(),
    agent: z
      .object({
        configured: z.boolean(),
        last_success_at: Timestamp.nullable(),
      })
      .passthrough(),
    components: z.array(z.object({ name: Text, status: Text }).passthrough()),
    permissions: z.object({ review: z.boolean() }).passthrough().optional(),
  })
  .passthrough();
export type Health = z.infer<typeof HealthSchema>;

export const ScenarioSchema = z
  .object({
    id: Text,
    name: Text,
    summary: Text,
    message: JsonObject,
    references: z.array(JsonObject),
    ground_truth: z.object({ decision: Decision, reason: Text }).passthrough(),
  })
  .passthrough();
export type Scenario = z.infer<typeof ScenarioSchema>;
export const ScenariosSchema = z
  .object({
    version: Text,
    clock: Timestamp,
    scenarios: z.array(ScenarioSchema),
  })
  .passthrough();

export const PoliciesSchema = z
  .object({
    version: Text,
    rules: z.array(z.object({ id: Text, description: Text }).passthrough()),
  })
  .passthrough();

export const OverviewSchema = z
  .object({
    processed: z.number().int().nonnegative(),
    contradictions: z.number().int().nonnegative(),
    pending_reviews: z.number().int().nonnegative(),
    quarantined: z.number().int().nonnegative(),
    recent: z.array(CaseSchema),
  })
  .passthrough();

const RatioSchema = z
  .object({
    value: z.number().min(0).max(1).nullable(),
    numerator: z.number().int().nonnegative(),
    denominator: z.number().int().nonnegative(),
  })
  .passthrough();
export const EvaluationsSchema = z
  .object({
    items: z.array(
      z
        .object({
          id: Text,
          created_at: Timestamp,
          dataset_version: Text,
          case_ids: z.array(Text),
          native: z
            .object({
              status: Text,
              passed: z.boolean(),
              accepted_records: z.number().int().nonnegative(),
              expected_cases: z.number().int().nonnegative(),
              proposal_accuracy: RatioSchema,
              final_accuracy: RatioSchema,
              false_quarantine_rate: RatioSchema,
              unsafe_release: z
                .object({
                  count: z.number().int().nonnegative().nullable(),
                  denominator: z.number().int().nonnegative(),
                })
                .passthrough(),
              review_rate: RatioSchema,
              latency: z
                .object({
                  mean_ms: z.number().nonnegative().nullable(),
                  p95_ms: z.number().nonnegative().nullable(),
                  observed_records: z.number().int().nonnegative(),
                  total_records: z.number().int().nonnegative(),
                })
                .passthrough(),
              model_usage: z.unknown(),
              model_cost: z.unknown(),
              issues: z.array(z.unknown()),
              cases: z.array(JsonObject),
            })
            .passthrough(),
        })
        .passthrough(),
    ),
  })
  .passthrough();
