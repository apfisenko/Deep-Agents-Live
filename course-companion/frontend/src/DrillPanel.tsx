/**
 * Панель тренажёра: A2UI-surface поверх кейса из стейта companion (§1.2).
 *
 * «UI как проекция стейта агента» вживую: show_drill_case положил кейс в
 * канал drill_case -> App увидел его в values (канал 1, useStream) и
 * смонтировал эту панель -> панель открывает канал 2 (drill-endpoint,
 * POST+SSE): отдельный LLM-вызов стримит A2UI-сообщения, форма «проявляется»
 * инкрементально. Ответ студента (userAction) уезжает тем же каналом 2 и
 * инжектится сервером в тред companion — разбор приходит текстом в чат
 * (канал 1), по нему App панель размонтирует.
 *
 * Surface-ядро (MessageProcessor + A2uiSurface + userAction-callback)
 * перенесено из devstand-клиента drill-модуля. Импорты строго /v0_9 —
 * дефолтный экспорт пакетов сломанный v0_8 (грабли версий A2UI).
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  A2uiSurface,
  basicCatalog,
  MarkdownContext,
  ReactComponentImplementation,
} from "@a2ui/react/v0_9";
import { MessageProcessor, SurfaceModel } from "@a2ui/web_core/v0_9";
import { renderMarkdown } from "@a2ui/markdown-it";

import { sendA2ui } from "./a2ui";

// Через Vite-прокси: /api/drill/a2ui -> <drill upstream>/drill/a2ui
// (по умолчанию тот же companion :2024 — endpoint вмонтирован http.app'ом).
const DRILL_API = "/api/drill/a2ui";

export function DrillPanel({
  drillCase,
  threadId,
}: {
  drillCase: Record<string, unknown>;
  threadId: string;
}) {
  const [surfaces, setSurfaces] = useState<
    SurfaceModel<ReactComponentImplementation>[]
  >([]);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("форма кейса готовится…");
  const [error, setError] = useState<string | null>(null);
  const busyRef = useRef(false);
  const generatedRef = useRef(false);
  const sendActionRef = useRef<((action: unknown) => Promise<void>) | null>(null);

  // actionHandler MessageProcessor'а — единственное место, где библиотека
  // отдаёт userAction; транспорт до сервера целиком на приложении.
  const processor = useMemo(
    () =>
      new MessageProcessor<ReactComponentImplementation>(
        [basicCatalog],
        (action) => {
          void sendActionRef.current?.(action);
        }
      ),
    []
  );

  useEffect(() => {
    const sub1 = processor.onSurfaceCreated((s) =>
      setSurfaces((prev) => [...prev, s])
    );
    const sub2 = processor.onSurfaceDeleted((id) =>
      setSurfaces((prev) => prev.filter((s) => s.id !== id))
    );
    return () => {
      sub1.unsubscribe();
      sub2.unsubscribe();
    };
  }, [processor]);

  const sendAction = useCallback(
    async (action: unknown) => {
      // Кнопка «Отправить» живёт внутри A2UI-surface и нашим busy не
      // блокируется — двойной клик глушим здесь, чтобы не задвоить доставку.
      if (busyRef.current) return;
      try {
        busyRef.current = true;
        setBusy(true);
        setError(null);
        setStatus("отправляю ответ на разбор…");
        await sendA2ui(
          DRILL_API,
          { version: "v0.9", action, threadId },
          (chunk) => processor.processMessages(chunk)
        );
        setStatus("ответ доставлен — разбор придёт в чат");
      } catch (e) {
        console.error(e);
        setError(e instanceof Error ? e.message : String(e));
        setStatus("ответ не доставлен");
      } finally {
        busyRef.current = false;
        setBusy(false);
      }
    },
    [processor, threadId]
  );

  useEffect(() => {
    sendActionRef.current = sendAction;
  }, [sendAction]);

  // Генерация формы — один раз на кейс (панель монтируется с key=case_id;
  // ref-гард гасит второй прогон эффекта в StrictMode).
  useEffect(() => {
    if (generatedRef.current) return;
    generatedRef.current = true;
    let count = 0;
    setStatus("LLM генерирует форму кейса…");
    sendA2ui(DRILL_API, { case: drillCase }, (chunk) => {
      count += chunk.length;
      processor.processMessages(chunk);
      setStatus(`LLM генерирует форму кейса… ${count} a2ui-сообщений`);
    })
      .then(() => setStatus("заполни форму и нажми «Отправить»"))
      .catch((e) => {
        console.error(e);
        setError(e instanceof Error ? e.message : String(e));
        setStatus("форма не сгенерировалась");
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="drill" aria-label="Тренажёр">
      <div className="drill-header">
        <span className="drill-title">тренажёр · кейс-форма</span>
        <span className="drill-status">
          {busy ? <span className="spinner" /> : null}
          {status}
        </span>
      </div>
      {error ? <div className="error">Ошибка формы: {error}</div> : null}
      <MarkdownContext.Provider value={renderMarkdown}>
        <div className="drill-surfaces">
          {surfaces.map((surface) => (
            <A2uiSurface key={surface.id} surface={surface} />
          ))}
        </div>
      </MarkdownContext.Provider>
    </section>
  );
}
