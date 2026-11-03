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

const AgentObservation = z.object({
  tool_reads: z.object({
    message: z.number().int().nonnegative().optional(),
    contracts: z.number().int().nonnegative().optional(),
    related: z.number().int().nonnegative().optional(),
    precedents: z.number().int().nonnegative().optional(),
  }).passthrough().nullable().optional(),
}).catchall(z.unknown());

export const PrecedentContextSchema = z.object({
  status: z.enum(["retrieved", "unavailable"]),
  implementation: z.literal("IRIS VECTOR_COSINE"),
  model: z.literal("all-minilm:22m"),
  dimensions: z.literal(384),
  matches: z.array(z.object({
    precedent_id: Text,
    source_id: Text,
    source_type: z.enum(["resolved_case", "approved_amendment"]),
    contract_id: Text,
    kind: Text,
    summary: Text.max(400),
    outcome: Text,
    similarity: z.number().finite().min(-1).max(1),
    synthetic: z.boolean().nullable(),
    decision_authority: z.literal(false),
  }).passthrough()).max(3),
  decision_authority: z.literal(false),
}).passthrough();

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
    agent: AgentObservation.nullable(),
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
    workflow: z.object({
      engine: z.literal("native-iris-workflow"),
      status: z.enum(["queued", "pending", "completion_pending", "completed"]),
      role: Text,
      task_id: z.union([Text, z.number()]).optional(),
      completion_received: z.boolean(),
    }).passthrough().optional(),
    runbook_context: z.object({
      status: z.enum(["retrieved", "unavailable"]),
      implementation: Text,
      decision_authority: z.literal(false),
      matches: z.array(z.object({
        id: Text,
        title: Text,
        guidance: Text,
        similarity: z.number().finite().min(-1).max(1),
        decision_authority: z.literal(false),
      }).passthrough()).max(2),
    }).passthrough().optional(),
    precedent_context: PrecedentContextSchema.optional(),
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

export const ReviewTaskSchema = z.object({
  task_id: Text,
  case_id: Text,
  role: z.literal("ReviewWorklist"),
  status: z.enum(["pending", "completion_pending"]),
  assigned_to: z.string().nullable(),
  created_at: Text,
  case_version: z.number().int().positive(),
  title: Text,
}).passthrough();
export const ReviewsSchema = z.object({
  engine: z.literal("native-iris-workflow"),
  items: z.array(ReviewTaskSchema).max(100),
  total: z.number().int().nonnegative(),
  limit: z.number().int().positive().max(100),
  offset: z.number().int().nonnegative(),
}).passthrough();
export type ReviewTask = z.infer<typeof ReviewTaskSchema>;

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
