/**
 * Dev-стенд drill-модуля: кейс-заглушка -> LLM-форма (A2UI) -> userAction.
 * Surface-ядро — по образцу референсного shell'а (то же, что в спайке 2).
 * Импорты строго /v0_9: дефолтный экспорт пакетов — сломанный v0_8.
 */
import {useState, useEffect, useCallback, useMemo, useRef} from 'react';
import {A2uiSurface, basicCatalog, MarkdownContext, ReactComponentImplementation} from '@a2ui/react/v0_9';
import {MessageProcessor, SurfaceModel} from '@a2ui/web_core/v0_9';
import {renderMarkdown} from '@a2ui/markdown-it';
import {sendA2ui} from './client';

// В фазе 3 сюда поедет threadId живого чата companion.
const THREAD_ID = 'devstand-thread-1';

export function App() {
  const [caseData, setCaseData] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState<string | null>(null);
  const [delivered, setDelivered] = useState('');
  const [surfaces, setSurfaces] = useState<SurfaceModel<ReactComponentImplementation>[]>([]);
  const sendActionRef = useRef<((action: unknown) => Promise<void>) | null>(null);
  const busyRef = useRef(false);
  useEffect(() => {
    busyRef.current = busy;
  }, [busy]);

  // actionHandler MessageProcessor'а — единственное место, где библиотека
  // отдаёт userAction; транспорт до сервера целиком на приложении.
  const processor = useMemo(
    () =>
      new MessageProcessor<ReactComponentImplementation>([basicCatalog], action => {
        console.log('userAction:', action);
        void sendActionRef.current?.(action);
      }),
    [],
  );

  useEffect(() => {
    const sub1 = processor.onSurfaceCreated(s => setSurfaces(prev => [...prev, s]));
    const sub2 = processor.onSurfaceDeleted(id => setSurfaces(prev => prev.filter(s => s.id !== id)));
    return () => {
      sub1.unsubscribe();
      sub2.unsubscribe();
    };
  }, [processor]);

  useEffect(() => {
    fetch('/devstand/case')
      .then(r => r.json())
      .then(setCaseData)
      .catch(e => setError(`кейс не загрузился: ${e}`));
  }, []);

  const sendAction = useCallback(
    async (action: unknown) => {
      // Кнопка «Отправить» живёт внутри A2UI-surface и нашим busy не
      // блокируется — двойной клик глушим здесь, чтобы не задвоить доставку.
      if (busyRef.current) return;
      try {
        setBusy(true);
        setError(null);
        setStatus('отправляю userAction…');
        // Транспорт спайка: POST {version:'v0.9', action} (+ threadId для доставки).
        await sendA2ui('/drill/a2ui', {version: 'v0.9', action, threadId: THREAD_ID}, chunk =>
          processor.processMessages(chunk),
        );
        const records = await fetch('/devstand/delivered').then(r => r.json());
        setDelivered(JSON.stringify(records, null, 2));
        setStatus('userAction доставлен');
      } catch (e) {
        console.error(e);
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setBusy(false);
      }
    },
    [processor],
  );

  useEffect(() => {
    sendActionRef.current = sendAction;
  }, [sendAction]);

  const startCase = useCallback(async () => {
    if (!caseData) return;
    try {
      setBusy(true);
      setError(null);
      setDelivered('');
      // Новый прогон кейса — сбрасываем поверхности прошлого.
      Array.from(processor.model.surfacesMap.keys()).forEach(id => processor.model.deleteSurface(id));
      setSurfaces([]);
      setStatus('LLM генерирует форму…');
      let count = 0;
      await sendA2ui('/drill/a2ui', {case: caseData}, chunk => {
        count += chunk.length;
        processor.processMessages(chunk);
        setStatus(`LLM генерирует форму… получено ${count} a2ui-сообщений`);
      });
      setStatus(s => `${s} — готово`);
    } catch (e) {
      console.error(e);
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }, [caseData, processor]);

  return (
    <MarkdownContext.Provider value={renderMarkdown}>
      <div className="shell">
        <div className="badge">dev-стенд drill-модуля — не боевой UI</div>
        <div className="controls">
          <button id="start-case" disabled={busy || !caseData} onClick={() => void startCase()}>
            Сгенерировать форму кейса (LLM)
          </button>
        </div>
        <div className="status" id="status">{status}</div>
        {error && <div className="error" id="error">{error}</div>}
        <section className="surfaces">
          {surfaces.map(surface => (
            <A2uiSurface key={surface.id} surface={surface} />
          ))}
        </section>
        {delivered && (
          <div className="delivered">
            <div>Доставлено в тред companion (лог заглушки):</div>
            <pre id="delivered">{delivered}</pre>
          </div>
        )}
      </div>
    </MarkdownContext.Provider>
  );
}
