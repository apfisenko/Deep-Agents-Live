import { useEffect, useRef, useState } from "react";

import {
  AIMessage,
  HumanMessage,
  ToolMessage,
  type BaseMessage,
} from "@langchain/core/messages";
import {
  useMessages,
  useStream,
  useSubmissionQueue,
  type AnyStream,
  type SubagentDiscoverySnapshot,
} from "@langchain/react";
import ReactMarkdown from "react-markdown";

import { DrillPanel } from "./DrillPanel";

/**
 * Веб-чат Course Companion поверх Agent Server API (ступени 1–4).
 *
 * Ступень 1: один хук useStream — сообщения, стриминг, threadId.
 * Ступень 2 добавляет три вещи, ради которых фронт вообще эволюционирует:
 * - очередь сообщений (useSubmissionQueue + multitaskStrategy=enqueue):
 *   composer больше не блокируется бегущим раном;
 * - карточки субагентов (stream.subagents + useMessages) и карточки
 *   ФОНОВЫХ задач (values.async_tasks — канал стейта companion);
 * - поллер чекера: UI сам опрашивает сервер чекера по thread_id задачи и по
 *   success авто-отправляет служебное сообщение в тред companion — так
 *   «фидбек приходит сам», хотя AsyncSubAgent — чистый поллинг.
 * Ступень 4 — тренажёр (drill): companion кладёт кейс в канал drill_case
 * стейта, App видит его в values и монтирует DrillPanel (A2UI-surface,
 * канал 2). Ответ студента drill-endpoint инжектит в тред сервер-сайд;
 * разбор стримится в чат штатной thread-scoped подпиской useStream, а
 * панель закрывается локально, как только разбор начал приходить.
 * threadId живёт в sessionStorage — перезагрузка страницы переподключается
 * к бегущему рану (паттерн join/rejoin), ран на сервере не гибнет.
 */

const API_URL = `${window.location.origin}/api/langgraph`;
// Поллер ходит на сервер ЧЕКЕРА через свой прокси-путь (см. vite.config.ts):
// co-deployed это тот же сервер, при распиле — :2025. Код фронта одинаковый.
const CHECKER_API_URL = `${window.location.origin}/api/checker`;
const CHECKER_MODE = import.meta.env.VITE_CHECKER_MODE ?? "agent_protocol";
const ASSISTANT_ID = "companion"; // graph id из langgraph.json
const THREAD_KEY = "companion-thread-id";
const AUTO_PREFIX = "[авто]"; // маркер служебных сообщений поллера
const DRILL_PREFIX = "[drill]"; // маркер служебных сообщений drill-доставки
const POLL_INTERVAL_MS = 3000;

/** Задача фонового чекера, как её хранит deepagents / A2A middleware. */
type AsyncTask = {
  task_id: string;
  agent_name: string;
  thread_id: string;
  run_id: string;
  status: string;
  created_at: string;
  transport?: string;
  a2a_rpc_path?: string;
};

type CompanionValues = {
  mode?: string;
  async_tasks?: Record<string, AsyncTask>;
  // кейс тренажёра из канала drill_case (кладёт тул show_drill_case)
  drill_case?: (Record<string, unknown> & { case_id?: string }) | null;
};

/** Разбор по кейсу уже пришёл в чат? Ответ студента drill-endpoint инжектит
 * в тред служебным сообщением "[drill] … surfaceId=…"; появившийся ПОСЛЕ него
 * текст companion — это и есть разбор: с этого момента форма своё отработала
 * (решение «закрываем surface локально по получению разбора»). Детект по
 * истории треда — переживает перезагрузку страницы. */
function drillReviewArrived(
  messages: readonly (BaseMessage | undefined)[],
  surfaceId: string
): boolean {
  let deliveredAt = -1;
  messages.forEach((m, i) => {
    if (
      m != null &&
      HumanMessage.isInstance(m) &&
      m.text.startsWith(DRILL_PREFIX) &&
      m.text.includes(surfaceId)
    ) {
      deliveredAt = i;
    }
  });
  if (deliveredAt < 0) return false;
  return messages
    .slice(deliveredAt + 1)
    .some(
      (m) => m != null && AIMessage.isInstance(m) && m.text.trim().length > 0
    );
}

const TERMINAL_TASK_STATUSES = new Set(["success", "error", "cancelled"]);

const A2A_STATE_TO_STATUS: Record<string, string> = {
  submitted: "pending",
  working: "running",
  "input-required": "running",
  completed: "success",
  failed: "error",
  canceled: "cancelled",
};

function taskUsesA2A(task: AsyncTask): boolean {
  return CHECKER_MODE === "a2a" || task.transport === "a2a";
}

/** Человеческая подпись статуса задачи (+ маппинг статусов на шве:
 * отменённый ран на сервере чекера — это `interrupted`, не `cancelled`). */
function taskStatusLabel(status: string): string {
  switch (status) {
    case "running":
    case "pending":
      return "проверяется…";
    case "success":
      return "готово";
    case "error":
      return "ошибка";
    case "cancelled":
      return "отменена";
    case "interrupted":
      return "перебита (отмена или новая инструкция)";
    default:
      return status;
  }
}

type ToolCallView = {
  callId: string;
  name: string;
  args: Record<string, unknown>;
  status: "running" | "finished" | "error";
};

/** Собрать tool-вызовы из истории: вызовы из AI-сообщений + их результаты.
 *
 * Пока ран идёт, вызов считается завершённым только если пришёл его
 * СОБСТВЕННЫЙ ToolMessage или диалог ушёл дальше (следующий AI/human-ход).
 * Просто «есть сообщения позже» не годится: при параллельных вызовах
 * результат соседнего тула помечал бы ещё бегущий как finished.
 */
function assembleToolCalls(
  messages: readonly (BaseMessage | undefined)[],
  isLoading: boolean,
  runFailed: boolean
): ToolCallView[] {
  const resultById = new Map<string, ToolMessage>();
  for (const m of messages) {
    if (m != null && ToolMessage.isInstance(m) && m.tool_call_id) {
      resultById.set(m.tool_call_id, m);
    }
  }
  const calls: ToolCallView[] = [];
  messages.forEach((m, i) => {
    if (m == null || !AIMessage.isInstance(m) || !m.tool_calls?.length) return;
    const turnPassed = messages
      .slice(i + 1)
      .some(
        (later) =>
          later != null &&
          (AIMessage.isInstance(later) || HumanMessage.isInstance(later))
      );
    for (const call of m.tool_calls) {
      if (!call.id) continue;
      const result = resultById.get(call.id);
      calls.push({
        callId: call.id,
        name: call.name,
        args: (call.args ?? {}) as Record<string, unknown>,
        status: result
          ? result.status === "error"
            ? "error"
            : "finished"
          : turnPassed
            ? "finished"
            : isLoading
              ? "running"
              // ран кончился, а результата вызова нет: упавший/оборванный ран
              // не должен рисовать ✓ на вызове, который не завершился
              : runFailed
                ? "error"
                : "finished",
      });
    }
  });
  return calls;
}

/** Метка инструмента: для task показываем, какому субагенту делегировали. */
function toolLabel(name: string, args: Record<string, unknown>): string {
  if (name === "task") return `task → ${String(args.subagent_type ?? "субагент")}`;
  if (name === "start_async_task")
    return `фоновая задача → ${String(args.subagent_type ?? "субагент")}`;
  return name;
}

/** Секундомер бегущего рана — делает работу агента видимой (и измеримой). */
function useElapsedSeconds(running: boolean): number {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    if (!running) return;
    setElapsed(0);
    const startedAt = Date.now();
    const timer = setInterval(
      () => setElapsed(Math.round((Date.now() - startedAt) / 1000)),
      1000
    );
    return () => clearInterval(timer);
  }, [running]);
  return elapsed;
}

/**
 * Поллер фоновых проверок («результат пришёл сам», §механика):
 * Agent Protocol — GET /threads/{id}/runs/{run_id};
 * A2A — JSON-RPC tasks/get на rpc-path чекера.
 */
function useCheckerPoller(
  tasks: Record<string, AsyncTask>,
  alreadyNotified: ReadonlySet<string>,
  onDone: (task: AsyncTask) => void
): Record<string, string> {
  const [liveStatuses, setLiveStatuses] = useState<Record<string, string>>({});
  const notifiedRef = useRef<Set<string>>(new Set());
  const onDoneRef = useRef(onDone);
  onDoneRef.current = onDone;
  for (const id of alreadyNotified) notifiedRef.current.add(id);

  const pendingKey = Object.values(tasks)
    .filter((t) => !TERMINAL_TASK_STATUSES.has(t.status))
    .map((t) => `${t.task_id}:${t.run_id}:${t.transport ?? CHECKER_MODE}`)
    .sort()
    .join(",");

  useEffect(() => {
    if (!pendingKey) return;
    const pending = Object.values(tasks).filter(
      (t) => !TERMINAL_TASK_STATUSES.has(t.status)
    );
    let alive = true;

    async function pollAgentProtocol(task: AsyncTask) {
      const res = await fetch(
        `${CHECKER_API_URL}/threads/${task.thread_id}/runs/${task.run_id}`
      );
      if (!res.ok) return null;
      const run = (await res.json()) as { status?: string };
      return run.status ?? "unknown";
    }

    async function pollA2A(task: AsyncTask) {
      const rpcPath = task.a2a_rpc_path ?? "/a2a";
      const res = await fetch(`${CHECKER_API_URL}${rpcPath}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: `poll-${task.task_id}`,
          method: "tasks/get",
          params: { id: task.task_id },
        }),
      });
      if (!res.ok) return null;
      const body = (await res.json()) as {
        result?: { status?: { state?: string } };
      };
      const state = body.result?.status?.state ?? "working";
      return A2A_STATE_TO_STATUS[state] ?? state;
    }

    async function poll() {
      for (const task of pending) {
        try {
          const status = taskUsesA2A(task)
            ? await pollA2A(task)
            : await pollAgentProtocol(task);
          if (status == null || !alive) return;
          setLiveStatuses((prev) =>
            prev[task.task_id] === status
              ? prev
              : { ...prev, [task.task_id]: status }
          );
          if (status === "success" && !notifiedRef.current.has(task.task_id)) {
            notifiedRef.current.add(task.task_id);
            onDoneRef.current(task);
          }
        } catch {
          // чекер недоступен — молча пробуем в следующий тик
        }
      }
    }

    void poll();
    const timer = setInterval(() => void poll(), POLL_INTERVAL_MS);
    return () => {
      alive = false;
      clearInterval(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingKey]);

  return liveStatuses;
}

export function App() {
  // threadId переживает перезагрузку страницы: remount с тем же threadId
  // присоединяется к треду и его бегущему рану (join/rejoin).
  const [threadId, setThreadId] = useState<string | null>(() =>
    sessionStorage.getItem(THREAD_KEY)
  );
  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const stream = useStream({
    apiUrl: API_URL,
    assistantId: ASSISTANT_ID,
    threadId,
    onThreadId(id) {
      setThreadId(id);
      if (id) sessionStorage.setItem(THREAD_KEY, id);
    },
  });
  const queue = useSubmissionQueue(stream);

  // Пока ран идёт — показываем весь живой стрим (включая работу внутри
  // подграфов: видно, ЧЕМ занят агент). Когда ран завершён, перечитываем
  // персистентную историю треда с сервера и оставляем только её: временные
  // сообщения вложенных прогонов в диалоге треда не живут.
  const [settledIds, setSettledIds] = useState<Set<string> | null>(null);
  useEffect(() => {
    if (stream.isLoading || !threadId) {
      setSettledIds(null);
      return;
    }
    let alive = true;
    stream.client.threads
      .getState<{ messages?: { id?: string }[] }>(threadId)
      .then((state) => {
        if (!alive) return;
        const persisted = (state.values.messages ?? [])
          .map((m) => m.id)
          .filter((id): id is string => Boolean(id));
        setSettledIds(new Set(persisted));
      })
      .catch(() => setSettledIds(null));
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stream.isLoading, threadId]);

  const messages = stream.messages.filter(
    (m): m is BaseMessage =>
      m != null &&
      m.type !== "tool" &&
      (stream.isLoading ||
        settledIds == null ||
        (m.id != null && settledIds.has(m.id)))
  );
  const values = stream.values as CompanionValues | undefined;
  const mode = values?.mode;
  const asyncTasks = values?.async_tasks ?? {};

  // Тренажёр: кейс появился в values (канал drill_case) → монтируем панель
  // с A2UI-surface. Панель живёт, пока студент в drill-режиме и разбор по
  // ЭТОМУ кейсу ещё не пришёл; key=case_id — новый кейс = свежая панель.
  const drillCase = values?.drill_case ?? null;
  const drillCaseId =
    typeof drillCase?.case_id === "string" ? drillCase.case_id : null;
  const showDrill =
    mode === "drill" &&
    drillCase != null &&
    drillCaseId != null &&
    threadId != null &&
    !drillReviewArrived(stream.messages, `drill-${drillCaseId}`);
  const toolCalls = assembleToolCalls(
    stream.messages,
    stream.isLoading,
    stream.error != null
  );
  const subagentsByCallId = new Map(
    [...stream.subagents.values()].map((s) => [s.id, s])
  );
  const runningTools = toolCalls.filter((tc) => tc.status === "running");
  const elapsed = useElapsedSeconds(stream.isLoading);

  // «Результат пришёл сам»: по success на сервере чекера отправляем в тред
  // companion служебное сообщение — оно встаёт в очередь (enqueue), companion
  // штатно вызывает check_async_task и отдаёт разбор в чат.
  const notifiedTaskIds = new Set(
    Object.keys(asyncTasks).filter((taskId) =>
      stream.messages.some(
        (m) =>
          m != null &&
          HumanMessage.isInstance(m) &&
          m.text.startsWith(AUTO_PREFIX) &&
          m.text.includes(taskId)
      )
    )
  );
  const liveStatuses = useCheckerPoller(asyncTasks, notifiedTaskIds, (task) => {
    void stream.submit(
      {
        messages: [
          new HumanMessage(
            `${AUTO_PREFIX} фоновая проверка ${task.task_id} завершена — ` +
              "вызови check_async_task с этим task_id, забери результат и дай разбор."
          ),
        ],
      },
      { multitaskStrategy: "enqueue" }
    );
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [stream.messages]);

  function handleSubmit() {
    const text = draft.trim();
    if (!text) return;
    setDraft("");
    // enqueue: если ран уже идёт, сообщение встаёт в очередь треда и уйдёт
    // следующим раном — composer не блокируется (double texting: enqueue).
    void stream.submit(
      { messages: [new HumanMessage(text)] },
      { multitaskStrategy: "enqueue" }
    );
  }

  function handleNewThread() {
    sessionStorage.removeItem(THREAD_KEY);
    setThreadId(null);
  }

  const taskList = Object.values(asyncTasks).sort((a, b) =>
    a.created_at.localeCompare(b.created_at)
  );

  return (
    <div className="app">
      <header>
        <h1>Course Companion</h1>
        <div className="meta">
          {mode ? <span className="badge">режим: {mode}</span> : null}
          {threadId ? <span className="thread">тред {threadId.slice(0, 8)}</span> : null}
          <button type="button" onClick={handleNewThread} disabled={stream.isLoading}>
            Новый диалог
          </button>
        </div>
      </header>

      {taskList.length > 0 ? (
        <section className="tasks" aria-label="Фоновые проверки">
          {taskList.map((task) => (
            <TaskCard
              key={task.task_id}
              task={task}
              liveStatus={liveStatuses[task.task_id]}
            />
          ))}
        </section>
      ) : null}

      <main>
        {messages.length === 0 && !stream.isLoading ? (
          <p className="empty">
            Задай вопрос по курсу или сдай домашку (путь к коду + тема).
          </p>
        ) : null}

        {messages.map((message, i) => (
          <Message
            key={message.id ?? i}
            message={message}
            toolCalls={toolCalls}
            stream={stream as unknown as AnyStream}
            subagentsByCallId={subagentsByCallId}
          />
        ))}

        {showDrill ? (
          <DrillPanel
            key={drillCaseId}
            drillCase={drillCase}
            threadId={threadId}
          />
        ) : null}

        {stream.isLoading ? (
          <div className="status" role="status">
            <span className="spinner" />
            {runningTools.length > 0
              ? `агент вызвал инструмент: ${runningTools
                  .map((tc) => toolLabel(tc.name, tc.args))
                  .join(", ")}`
              : "агент работает"}
            {elapsed > 0 ? ` · ${elapsed} с` : ""}
          </div>
        ) : null}

        {stream.error ? (
          <div className="error">
            Ошибка: {String((stream.error as Error)?.message ?? stream.error)}
          </div>
        ) : null}
        <div ref={bottomRef} />
      </main>

      {queue.size > 0 ? (
        <section className="queue" aria-label="Очередь сообщений">
          <div className="queue-header">
            <span>в очереди: {queue.size}</span>
            <button type="button" onClick={() => void queue.clear()}>
              очистить
            </button>
          </div>
          <ul>
            {queue.entries.map((entry) => {
              const values = entry.values as
                | { messages?: { content?: unknown }[] }
                | undefined;
              const text = String(values?.messages?.at(-1)?.content ?? "…");
              return (
                <li key={entry.id}>
                  <span className="queue-text">{text}</span>
                  <button type="button" onClick={() => void queue.cancel(entry.id)}>
                    отменить
                  </button>
                </li>
              );
            })}
          </ul>
        </section>
      ) : null}

      <form
        className="composer"
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
      >
        <textarea
          value={draft}
          rows={2}
          placeholder={
            stream.isLoading
              ? "агент занят — сообщение встанет в очередь"
              : "Сообщение… (Enter — отправить)"
          }
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
        />
        <button type="submit" disabled={draft.trim() === ""}>
          {stream.isLoading ? "в очередь" : "Отправить"}
        </button>
      </form>
    </div>
  );
}

/** Карточка фоновой проверки: локальный статус из стейта companion +
 * живой статус с сервера чекера (поллер). */
function TaskCard({
  task,
  liveStatus,
}: {
  task: AsyncTask;
  liveStatus: string | undefined;
}) {
  // стейт супервизора обновляется только его же тулами (check/cancel) —
  // живой статус с сервера чекера свежее, если он есть
  const effective = TERMINAL_TASK_STATUSES.has(task.status)
    ? task.status
    : (liveStatus ?? task.status);
  const busy = effective === "running" || effective === "pending";
  return (
    <div className={`task-card ${busy ? "busy" : ""}`}>
      {busy ? <span className="spinner" /> : null}
      <span className="task-name">{task.agent_name}</span>
      <span className={`task-status st-${effective}`}>
        {taskStatusLabel(effective)}
      </span>
      <span className="task-id">задача {task.task_id.slice(0, 8)}…</span>
    </div>
  );
}

/** Карточка субагента: имя, статус и последний ответ из его неймспейса
 * (селектор useMessages подписывается на поток субагента только пока
 * карточка смонтирована). */
function SubagentCard({
  stream,
  subagent,
}: {
  stream: AnyStream;
  subagent: SubagentDiscoverySnapshot;
}) {
  const [expanded, setExpanded] = useState(false);
  const subMessages = useMessages(stream, subagent);
  const lastAI = subMessages.filter(AIMessage.isInstance).at(-1);
  const preview =
    lastAI?.text ??
    (typeof subagent.output === "string" ? subagent.output : "");

  return (
    <div className={`subagent ${subagent.status}`}>
      <button type="button" onClick={() => setExpanded((v) => !v)}>
        {subagent.status === "running" ? "⏳" : subagent.status === "error" ? "✗" : "✓"}{" "}
        субагент {subagent.name}
        <span className="chevron">{expanded ? "▾" : "▸"}</span>
      </button>
      {expanded ? (
        <div className="subagent-body">
          {subagent.taskInput ? (
            <p className="subagent-task">задание: {subagent.taskInput}</p>
          ) : null}
          {preview ? (
            <div className="md">
              <ReactMarkdown>{preview}</ReactMarkdown>
            </div>
          ) : (
            <p className="subagent-task">
              {subagent.status === "running"
                ? "пока нет ответа…"
                : "поток субагента завершён — результат пересказан в чате"}
            </p>
          )}
        </div>
      ) : null}
    </div>
  );
}

/** Пузырь сообщения + tool-чипы + карточки субагентов этого хода. */
function Message({
  message,
  toolCalls,
  stream,
  subagentsByCallId,
}: {
  message: BaseMessage;
  toolCalls: readonly ToolCallView[];
  stream: AnyStream;
  subagentsByCallId: ReadonlyMap<string, SubagentDiscoverySnapshot>;
}) {
  const isHuman = message.type === "human";
  // служебные сообщения — и от поллера ([авто]), и от drill-доставки ([drill])
  const autoPrefix = [AUTO_PREFIX, DRILL_PREFIX].find(
    (p) => isHuman && message.text.startsWith(p)
  );
  const ownCalls = AIMessage.isInstance(message)
    ? toolCalls.filter((tc) => message.tool_calls?.some((t) => t.id === tc.callId))
    : [];
  // вызовы, по которым есть карточка субагента, чипом не дублируем
  const chipCalls = ownCalls.filter((tc) => !subagentsByCallId.has(tc.callId));
  const cardSubagents = ownCalls
    .map((tc) => subagentsByCallId.get(tc.callId))
    .filter((s): s is SubagentDiscoverySnapshot => s != null);

  if (!message.text && ownCalls.length === 0) return null;

  if (autoPrefix) {
    return (
      <div className="auto-note">
        {message.text.slice(autoPrefix.length).trim()}
      </div>
    );
  }

  return (
    <div className={`message ${isHuman ? "human" : "ai"}`}>
      <span className="author">{isHuman ? "Ты" : "Companion"}</span>
      {chipCalls.length > 0 ? (
        <ul className="tools">
          {chipCalls.map((tc) => (
            <li key={tc.callId} className={`tool ${tc.status}`}>
              {tc.status === "running" ? "⏳" : tc.status === "error" ? "✗" : "✓"}{" "}
              {toolLabel(tc.name, tc.args)}
            </li>
          ))}
        </ul>
      ) : null}
      {cardSubagents.map((subagent) => (
        <SubagentCard key={subagent.id} stream={stream} subagent={subagent} />
      ))}
      {message.text ? (
        isHuman ? (
          <p>{message.text}</p>
        ) : (
          // ответы companion приходят в Markdown (заголовки/списки фидбека) — рендерим
          <div className="md">
            <ReactMarkdown>{message.text}</ReactMarkdown>
          </div>
        )
      ) : null}
    </div>
  );
}
