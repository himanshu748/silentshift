import { useEffect, useRef, useState } from "react";
import { ArrowRight, CheckCheck, ChevronLeft, ChevronRight, LockKeyhole } from "lucide-react";
import { useApi } from "./api";
import type { Resource } from "./api";
import { CaseSchema, ReviewsSchema } from "./schema";
import type { Health } from "./schema";
import { CaseDetail, listKeys } from "./Investigations";
import {
  Badge,
  Button,
  EmptyState,
  ErrorState,
  humanize,
  Loading,
  PageHeading,
  shortTime,
  useActions,
} from "./ui";

const PAGE = 50;

export default function Reviews({
  refresh,
  caseId,
  health,
}: {
  refresh: number;
  caseId?: string;
  health: Resource<Health>;
}) {
  const [offset, setOffset] = useState(0);
  const { openConnect } = useActions();
  const canReview = health.data?.permissions?.review === true;
  const tasks = useApi(
    canReview ? `/api/reviews?limit=${PAGE}&offset=${offset}` : null,
    ReviewsSchema,
    refresh,
  );
  const activeTask = caseId
    ? tasks.data?.items.find((task) => task.case_id === caseId)
    : tasks.data?.items[0];
  const detail = useApi(
    activeTask ? `/api/cases/${encodeURIComponent(activeTask.case_id)}` : null,
    CaseSchema,
    refresh,
  );
  const detailRegion = useRef<HTMLDivElement>(null);
  const openedCase = useRef<string | null>(null);
  useEffect(() => {
    if (!caseId || detail.data?.id !== caseId || openedCase.current === caseId) return;
    openedCase.current = caseId;
    detailRegion.current?.querySelector<HTMLElement>("[data-case-heading]")?.focus();
  }, [caseId, detail.data]);

  const inspectHref = caseId ? `#investigations/${encodeURIComponent(caseId)}` : "#investigations";
  const permissionRequired = (
    <EmptyState
      icon={LockKeyhole}
      title="Reviewer permission required"
      action={<Button onClick={openConnect}>Connect reviewer session</Button>}
    >
      Connect with the configured IRIS reviewer to act on native review tasks. Your current
      account can still inspect investigations.
    </EmptyState>
  );

  return (
    <>
      <PageHeading
        title="Review"
        description="Resolve held transactions with their evidence and policy in view."
      >
        <a className="btn btn-secondary" href="#investigations">
          All investigations <ArrowRight size={15} aria-hidden="true" />
        </a>
      </PageHeading>

      {health.loading ? (
        <Loading>Checking reviewer access…</Loading>
      ) : health.error ? (
        <ErrorState error={health.error} />
      ) : !canReview ? (
        permissionRequired
      ) : tasks.loading ? (
        <Loading>Reading native review tasks…</Loading>
      ) : tasks.error ? (
        tasks.error.status === 403 ? permissionRequired : <ErrorState error={tasks.error} />
      ) : tasks.data ? (
        <>
          {tasks.data.items.length ? (
            <div className="split">
              <aside className="queue" aria-label="Native review worklist">
                <div className="queue-head">
                  <h2>Pending native tasks</h2>
                  <span
                    className="count mono"
                    aria-label={`${tasks.data.total} pending native tasks`}
                  >
                    {tasks.data.total}
                  </span>
                </div>
                <div className="queue-body">
                  <ol className="queue-list" onKeyDown={listKeys}>
                    {tasks.data.items.map((task) => {
                      const selected = activeTask?.task_id === task.task_id;
                      return (
                        <li key={task.task_id}>
                          <a
                            data-list-item
                            className={`queue-item tone-review ${selected ? "selected" : ""}`}
                            data-task-id={task.task_id}
                            href={`#reviews/${encodeURIComponent(task.case_id)}`}
                            aria-current={selected ? "true" : undefined}
                          >
                            <span className="queue-item-top">
                              <strong>{task.title}</strong>
                              <span className="mono">v{task.case_version}</span>
                            </span>
                            <span className="queue-item-meta mono">
                              Task {task.task_id} · {task.case_id}
                            </span>
                            <span className="queue-item-bottom">
                              <span className="queue-item-source">
                                {task.assigned_to
                                  ? `Assigned to ${task.assigned_to}`
                                  : "Ready for review"}
                                {" · "}
                                {shortTime(task.created_at)}
                              </span>
                              <Badge tone="review">{humanize(task.status)}</Badge>
                            </span>
                          </a>
                        </li>
                      );
                    })}
                  </ol>
                  <p className="queue-foot">
                    Completed tasks leave this worklist. Their decisions stay with the
                    investigation.
                  </p>
                </div>
              </aside>
              <div className="split-main" ref={detailRegion}>
                {activeTask && detail.data?.id === activeTask.case_id ? (
                  <CaseDetail item={detail.data} key={detail.data.id} />
                ) : detail.loading ? (
                  <Loading>Reading task evidence…</Loading>
                ) : detail.error ? (
                  <ErrorState error={detail.error} />
                ) : (
                  <EmptyState
                    icon={CheckCheck}
                    title="Task no longer pending"
                    action={
                      <a className="btn btn-secondary" href={inspectHref}>
                        Inspect the recorded outcome <ArrowRight size={15} aria-hidden="true" />
                      </a>
                    }
                  >
                    This task is not on the current page. Inspect its investigation or choose
                    another pending task.
                  </EmptyState>
                )}
              </div>
            </div>
          ) : (
            <EmptyState
              icon={CheckCheck}
              title={tasks.data.total ? "No tasks on this page" : "No pending native reviews"}
              action={
                <a className="btn btn-secondary" href={inspectHref}>
                  Inspect investigations <ArrowRight size={15} aria-hidden="true" />
                </a>
              }
            >
              {tasks.data.total
                ? "Return to an earlier page to choose a pending task."
                : "There are no pending native tasks for this reviewer. Resolved transactions remain in Investigations."}
            </EmptyState>
          )}
          <nav className="pager" aria-label="Review task pages">
            <span>
              {tasks.data.items.length
                ? `${tasks.data.offset + 1} to ${tasks.data.offset + tasks.data.items.length} of ${tasks.data.total}`
                : "No tasks shown"}
            </span>
            <div className="row-actions">
              <Button
                icon={ChevronLeft}
                disabled={offset === 0}
                onClick={() => setOffset((value) => Math.max(0, value - PAGE))}
              >
                Previous tasks
              </Button>
              <Button
                disabled={offset + tasks.data.limit >= tasks.data.total}
                onClick={() => setOffset((value) => value + PAGE)}
              >
                Next tasks <ChevronRight size={15} aria-hidden="true" />
              </Button>
            </div>
          </nav>
        </>
      ) : null}
    </>
  );
}
