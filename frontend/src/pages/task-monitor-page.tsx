import { Activity, Ban, CircleAlert, Play, RadioTower, TimerReset, Eraser } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { ErrorState } from "@/components/common/error-state";
import { PageHeader } from "@/components/common/page-header";
import { TaskStatusBadge } from "@/components/common/task-status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Spinner } from "@/components/ui/spinner";
import { isTaskFinished, useStartCollection, useTaskStatus, useTrackedTasks, useRevokeTask } from "@/features/tasks/hooks/use-tasks";
import { useProducts } from "@/features/products/hooks/use-products";
import { getErrorMessage } from "@/services/api-error";
import { formatDate } from "@/lib/utils";

function getProgress(status: string): number {
  if (status === "SUCCESS" || status === "FAILURE" || status === "REVOKED" || status === "IGNORED") return 100;
  if (status === "PARSING") return 80;
  if (status === "NAVIGATING") return 50;
  if (status === "INITIALIZING") return 25;
  if (status === "STARTED") return 15;
  return 5; // PENDING
}

export function TaskMonitorPage() {
  const { trackedTasks, addTask, updateTask, clearHistory } = useTrackedTasks();
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  
  // Состояния для модального окна
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState<number | "">("");
  
  // ИСПРАВЛЕНО: size: 100, так как бэкенд не пропускает больше 100 элементов!
  const productsQuery = useProducts({ page: 1, size: 100 }); 
  const startCollection = useStartCollection();
  const revokeTask = useRevokeTask();
  
  const taskStatus = useTaskStatus(activeTaskId);
  const activeStoredTask = trackedTasks.find((task) => task.task_id === activeTaskId);
  
  const displayedStatus = taskStatus.data?.status ?? activeStoredTask?.status ?? "PENDING";
  const displayedMessage = taskStatus.data?.message ?? activeStoredTask?.message;

  useEffect(() => {
    if (!activeTaskId && trackedTasks[0]) setActiveTaskId(trackedTasks[0].task_id);
  }, [activeTaskId, trackedTasks]);

  useEffect(() => {
    if (!taskStatus.data || !activeStoredTask) return;
    updateTask({ 
      task_id: taskStatus.data.task_id, 
      status: taskStatus.data.status, 
      message: taskStatus.data.message,
      productName: activeStoredTask.productName,
      startedAt: activeStoredTask.startedAt 
    });
  }, [taskStatus.data, updateTask]);

  const start = () => {
    if (!selectedProductId) {
      toast.error("Please select a product to collect.");
      return;
    }
    startCollection.mutate(Number(selectedProductId), {
      onSuccess: ({ task_id, product_name }) => { 
        addTask(task_id, product_name); 
        setActiveTaskId(task_id); 
        toast.success("Task dispatched to the queue.");
        setIsDialogOpen(false); // Закрываем окно при успехе
        setSelectedProductId(""); // Сбрасываем выбор
      },
      onError: (error) => toast.error(getErrorMessage(error)),
    });
  };

  const cancelActiveTask = () => {
    if (!activeTaskId) return;
    revokeTask.mutate(activeTaskId, {
      onSuccess: () => {
        toast.success("Task successfully revoked.");
        updateTask({ ...activeStoredTask!, status: "REVOKED", message: "Task forcefully terminated by user." });
      },
      onError: (error) => toast.error(getErrorMessage(error))
    });
  };

  const handleClearHistory = () => {
    clearHistory();
    setActiveTaskId(null);
    toast.success("Task history cleared.");
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Task monitor" 
        description="Launch individual price collections and follow Playwright's execution steps." 
        actions={
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            {/* Кнопка теперь просто открывает модальное окно */}
            <Button disabled={startCollection.isPending} onClick={() => setIsDialogOpen(true)}>
              {startCollection.isPending ? <Spinner /> : <Play className="size-4" />}
              Start collection
            </Button>
            <Button variant="outline" onClick={handleClearHistory}>
              <Eraser className="size-4" />
              Clear history
            </Button>
          </div>
        } 
      />

      {/* Всплывающее окно запуска парсинга */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Start price collection</DialogTitle>
            <DialogDescription>
              Select a product from your catalog to dispatch a new parsing task to the background workers.
            </DialogDescription>
          </DialogHeader>
          <div className="py-2">
            <label className="block space-y-1.5">
              <span className="text-sm font-medium">Active product</span>
              <select 
                className="flex h-9 w-full rounded-lg border border-zinc-200 bg-transparent px-3 text-sm outline-none focus-visible:border-zinc-400 dark:border-zinc-800"
                value={selectedProductId} 
                onChange={(e) => setSelectedProductId(Number(e.target.value))}
                disabled={productsQuery.isLoading}
              >
                <option value="" disabled>-- Choose a product --</option>
                {productsQuery.data?.items.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </label>
          </div>
          <div className="mt-4 flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
            <Button disabled={startCollection.isPending || !selectedProductId} onClick={start}>
              {startCollection.isPending ? <Spinner /> : <Play className="size-4" />}
              Launch Task
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
        <Card>
          <CardHeader><CardTitle>Active task details</CardTitle><CardDescription>Real-time execution logs from the headless browser.</CardDescription></CardHeader>
          <CardContent>
            {!activeTaskId ? (
              <div className="grid min-h-60 place-items-center text-center text-sm text-zinc-500 dark:text-zinc-400"><div><RadioTower className="mx-auto mb-3 size-5" />Select a product and start a task to monitor it here.</div></div>
            ) : taskStatus.isError ? <ErrorState error={taskStatus.error} onRetry={() => void taskStatus.refetch()} /> : (
              <div className="space-y-6">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div className="min-w-0 pr-4">
                    <h2 className="truncate text-xl font-bold tracking-tight">{activeStoredTask?.productName ?? "Unknown Product"}</h2>
                    <p className="mt-1 truncate font-mono text-xs italic text-zinc-500 dark:text-zinc-400">({activeTaskId})</p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <TaskStatusBadge status={displayedStatus} />
                    {!isTaskFinished(displayedStatus) && (
                      <Button size="icon" variant="outline" className="text-red-600 hover:text-red-700" onClick={cancelActiveTask} disabled={revokeTask.isPending}>
                        {revokeTask.isPending ? <Spinner /> : <Ban className="size-4" />}
                      </Button>
                    )}
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="h-2 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-900">
                    <div className={"h-full rounded-full bg-zinc-800 transition-all duration-500 dark:bg-zinc-200 " + (!isTaskFinished(displayedStatus) ? "animate-pulse" : "")} style={{ width: `${getProgress(displayedStatus)}%` }} />
                  </div>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400">{isTaskFinished(displayedStatus) ? "Execution completed" : "Processing"}</p>
                </div>

                <div className="grid gap-3 rounded-lg bg-zinc-50 p-4 text-sm dark:bg-zinc-900">
                  <div className="flex items-center gap-2">
                    <Activity className="size-4 text-zinc-500" />
                    <span>State: <strong>{displayedStatus}</strong></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <TimerReset className="size-4 text-zinc-500" />
                    <span>Started: {activeStoredTask ? formatDate(activeStoredTask.startedAt) : "—"}</span>
                  </div>
                  {displayedMessage && (
                    <p className="mt-2 border-l-2 border-zinc-300 pl-3 font-mono text-xs italic text-zinc-600 dark:border-zinc-700 dark:text-zinc-400">
                      {displayedMessage}
                    </p>
                  )}
                  {displayedStatus === "FAILURE" ? (
                    <div className="mt-2 flex items-center gap-2 text-amber-700 dark:text-amber-400">
                      <CircleAlert className="size-4" /> The execution encountered a fatal error during parsing.
                    </div>
                  ) : null}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Local task queue</CardTitle><CardDescription>Recent tasks dispatched from this device.</CardDescription></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {trackedTasks.length === 0 ? <p className="text-sm text-zinc-500 dark:text-zinc-400">No tasks in history.</p> : trackedTasks.map((task) => (
                <button key={task.task_id} className={"flex w-full flex-col justify-center gap-1 rounded-lg border p-3 text-left transition-colors " + (task.task_id === activeTaskId ? "border-zinc-500 bg-zinc-50 dark:border-zinc-500 dark:bg-zinc-900" : "border-zinc-200 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900")} type="button" onClick={() => setActiveTaskId(task.task_id)}>
                  <div className="flex w-full items-center justify-between gap-2">
                    <span className="min-w-0 truncate font-medium text-sm">{task.productName}</span>
                    <TaskStatusBadge status={task.status} />
                  </div>
                  <span className="truncate font-mono text-xs italic text-zinc-500">({task.task_id.slice(0, 13)}...)</span>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
