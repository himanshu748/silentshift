import { useEffect, useRef, useState } from "react";
import { ArrowRight, CheckCheck, ChevronLeft, ChevronRight, LockKeyhole, UserRoundCheck } from "lucide-react";
import { useApi } from "./api";
import type { Resource } from "./api";
import { CaseSchema, ReviewsSchema } from "./schema";
import type { Health } from "./schema";
import { CaseDetail } from "./Investigations";
import { Badge, Button, EmptyState, ErrorState, humanize, PageHeading, useActions } from "./ui";

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
    canReview ? `/api/reviews?limit=50&offset=${offset}` : null,
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
    detailRegion.current?.querySelector<HTMLElement>(".detail-title-row h2")?.focus();
  }, [caseId, detail.data]);

  const permissionRequired = (
    <EmptyState
      icon={LockKeyhole}
      title="Reviewer permission required"
      action={<Button onClick={openConnect}>Connect reviewer session</Button>}
    >
      Connect with the configured IRIS reviewer to act on native review tasks.
      Your current account can still inspect investigations.
    </EmptyState>
  );

  return (
    <>
      <PageHeading
        eyebrow="Workspace / human review"
        title="Review"
        description="Resolve held transactions with their evidence and policy in view."
      >
        <a className="button secondary" href="#investigations">
          All investigations <ArrowRight size={15} aria-hidden="true" />
        </a>
      </PageHeading>

      {health.loading ? (
        <div className="loading-state" role="status">Checking reviewer access…</div>
      ) : health.error ? (
        <ErrorState error={health.error} />
      ) : !canReview ? permissionRequired : tasks.loading ? (
        <div className="loading-state" role="status">Reading native review tasks…</div>
      ) : tasks.error ? (
        tasks.error.status === 403 ? permissionRequired : <ErrorState error={tasks.error} />
      ) : tasks.data ? (
        <>
          <div className="review-worklist-heading">
            <div>
              <UserRoundCheck size={19} aria-hidden="true" />
              <h2>Pending native tasks</h2>
              <span className="count mono" aria-label={`${tasks.data.total} pending native tasks`}>{tasks.data.total}</span>
            </div>
            <p>Completed tasks leave this worklist. Their decisions stay with the investigation.</p>
          </div>
          {tasks.data.items.length ? (
            <div className="reviews-workbench">
              <aside className="review-task-queue" aria-label="Native review worklist">
                <ol className="review-task-list">
                  {tasks.data.items.map((task) => (
                    <li key={task.task_id}>
                      <a
                        className={`review-task ${activeTask?.task_id === task.task_id ? "selected" : ""}`}
                        data-task-id={task.task_id}
                        href={`#reviews/${encodeURIComponent(task.case_id)}`}
                        aria-current={activeTask?.task_id === task.task_id ? "true" : undefined}
                      >
                        <span className="review-task-top"><span>Task <code>{task.task_id}</code></span><ChevronRight size={15} aria-hidden="true" /></span>
                        <strong>{task.title}</strong>
                        <code className="review-task-case">{task.case_id}</code>
                        <span className="review-task-bottom"><Badge tone="amber">{humanize(task.status)}</Badge><span>v{task.case_version}</span></span>
                        <span className="review-task-owner">{task.assigned_to ? `Assigned to ${task.assigned_to}` : "Ready for review"}</span>
                      </a>
                    </li>
                  ))}
                </ol>
              </aside>
              <div className="review-task-detail" ref={detailRegion}>
                {activeTask && detail.data?.id === activeTask.case_id ? (
                  <CaseDetail item={detail.data} key={detail.data.id} />
                ) : detail.loading ? (
                  <div className="loading-state" role="status">Reading task evidence…</div>
                ) : detail.error ? (
                  <ErrorState error={detail.error} />
                ) : (
                  <EmptyState
                    icon={CheckCheck}
                    title="Task no longer pending"
                    action={<a className="button secondary" href={caseId ? `#investigations/${encodeURIComponent(caseId)}` : "#investigations"}>Inspect the recorded outcome <ArrowRight size={15} /></a>}
                  >
                    This task is not on the current page. Inspect its investigation or choose another pending task.
                  </EmptyState>
                )}
              </div>
            </div>
          ) : (
            <EmptyState
              icon={CheckCheck}
              title={tasks.data.total ? "No tasks on this page" : "No pending native reviews"}
              action={<a className="button secondary" href={caseId ? `#investigations/${encodeURIComponent(caseId)}` : "#investigations"}>Inspect investigations <ArrowRight size={15} /></a>}
            >
              {tasks.data.total ? "Return to an earlier page to choose a pending task." : "There are no pending native tasks for this reviewer. Resolved transactions remain in Investigations."}
            </EmptyState>
          )}
          <div className="review-pagination">
            <span>{tasks.data.items.length ? `${tasks.data.offset + 1}–${tasks.data.offset + tasks.data.items.length} of ${tasks.data.total}` : "No tasks shown"}</span>
            <div>
              <Button icon={ChevronLeft} disabled={offset === 0} onClick={() => setOffset((value) => Math.max(0, value - 50))}>Previous tasks</Button>
              <Button disabled={offset + tasks.data.limit >= tasks.data.total} onClick={() => setOffset((value) => value + 50)}>Next tasks <ChevronRight size={15} aria-hidden="true" /></Button>
            </div>
          </div>
        </>
      ) : null}
    </>
  );
}
