import { Activity, CircleAlert, Play, RadioTower, TimerReset } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { ErrorState } from "@/components/common/error-state";
import { PageHeader } from "@/components/common/page-header";
import { TaskStatusBadge } from "@/components/common/task-status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { isTaskFinished, useStartCollection, useTaskStatus, useTrackedTasks } from "@/features/tasks/hooks/use-tasks";
import { getErrorMessage } from "@/services/api-error";
import { formatDate } from "@/lib/utils";

function getProgress(status: string): number {
  if (status === "SUCCESS" || status === "FAILURE" || status === "REVOKED") return 100;
  if (status === "STARTED") return 65;
  if (status === "RETRY") return 35;
  return 15;
}

export function TaskMonitorPage() {
  const { trackedTasks, addTask, updateTask } = useTrackedTasks();
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const startCollection = useStartCollection();
  const taskStatus = useTaskStatus(activeTaskId);
  const activeStoredTask = trackedTasks.find((task) => task.task_id === activeTaskId);
  const displayedStatus = taskStatus.data?.status ?? activeStoredTask?.status ?? "PENDING";

  useEffect(() => {
    if (!activeTaskId && trackedTasks[0]) setActiveTaskId(trackedTasks[0].task_id);
  }, [activeTaskId, trackedTasks]);

  useEffect(() => {
    if (!taskStatus.data) return;
    updateTask({ task_id: taskStatus.data.task_id, status: taskStatus.data.status, startedAt: activeStoredTask?.startedAt ?? new Date().toISOString() });
  }, [activeStoredTask?.startedAt, taskStatus.data, updateTask]);

  const start = () => {
    startCollection.mutate(undefined, {
      onSuccess: ({ task_id }) => { addTask(task_id); setActiveTaskId(task_id); toast.success("Collection task started."); },
      onError: (error) => toast.error(getErrorMessage(error)),
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader title="Task monitor" description="Launch price collection and follow Celery's status through automatic polling." actions={<Button disabled={startCollection.isPending} onClick={start}>{startCollection.isPending ? <Spinner /> : <Play className="size-4" />}Run price collection</Button>} />
      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
        <Card>
          <CardHeader><CardTitle>Active task</CardTitle><CardDescription>The selected task is polled every 2.5 seconds until it finishes.</CardDescription></CardHeader>
          <CardContent>
            {!activeTaskId ? (
              <div className="grid min-h-60 place-items-center text-center text-sm text-zinc-500 dark:text-zinc-400"><div><RadioTower className="mx-auto mb-3 size-5" />Start a collection task to monitor it here.</div></div>
            ) : taskStatus.isError ? <ErrorState error={taskStatus.error} onRetry={() => void taskStatus.refetch()} /> : (
              <div className="space-y-6">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><p className="text-xs uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Task ID</p><p className="mt-1 break-all font-mono text-sm">{activeTaskId}</p></div><TaskStatusBadge status={displayedStatus} /></div>
                <div className="space-y-2"><div className="h-2 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-900"><div className={"h-full rounded-full bg-zinc-800 transition-all duration-500 dark:bg-zinc-200 " + (!isTaskFinished(displayedStatus) ? "animate-pulse" : "")} style={{ width: `${getProgress(displayedStatus)}%` }} /></div><p className="text-xs text-zinc-500 dark:text-zinc-400">{isTaskFinished(displayedStatus) ? "Finished" : "In progress"} · status-derived indicator</p></div>
                <div className="grid gap-3 rounded-lg bg-zinc-50 p-4 text-sm dark:bg-zinc-900"><div className="flex items-center gap-2"><Activity className="size-4 text-zinc-500" /><span>Status: <strong>{displayedStatus}</strong></span></div><div className="flex items-center gap-2"><TimerReset className="size-4 text-zinc-500" /><span>Started: {activeStoredTask ? formatDate(activeStoredTask.startedAt) : "—"}</span></div>{displayedStatus === "FAILURE" ? <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400"><CircleAlert className="size-4" />The current API exposes only the status, not an error message.</div> : null}</div>
              </div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Started in this browser</CardTitle><CardDescription>Up to 10 recent task IDs are retained locally.</CardDescription></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {trackedTasks.length === 0 ? <p className="text-sm text-zinc-500 dark:text-zinc-400">No local task history.</p> : trackedTasks.map((task) => <button key={task.task_id} className={"flex w-full items-center justify-between gap-2 rounded-lg border p-3 text-left transition-colors " + (task.task_id === activeTaskId ? "border-zinc-500 bg-zinc-50 dark:border-zinc-500 dark:bg-zinc-900" : "border-zinc-200 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900")} type="button" onClick={() => setActiveTaskId(task.task_id)}><span className="min-w-0 truncate font-mono text-xs">{task.task_id}</span><TaskStatusBadge status={task.status} /></button>)}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
