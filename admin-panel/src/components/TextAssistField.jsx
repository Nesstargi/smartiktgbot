import { useId, useRef, useState } from "react";

const TECH_EMOJI_OPTIONS = [
  "📱",
  "💻",
  "🖥️",
  "⌚",
  "🎧",
  "🖱️",
  "⌨️",
  "🖨️",
  "📷",
  "📹",
  "🎮",
  "📺",
  "🔊",
  "🎙️",
  "🔋",
  "⚡",
  "🔌",
  "💡",
  "📡",
  "🛰️",
  "🛜",
  "💾",
  "🧠",
  "🤖",
  "🛠️",
  "🔒",
  "📶",
  "🌐",
  "🚀",
  "✨",
];

const SALES_PHRASE_OPTIONS = [
  "Хит продаж",
  "Лучшая цена",
  "Выбор покупателей",
  "Премиальное качество",
  "Ограниченное предложение",
  "Гарантия производителя",
  "Идеально для дома и офиса",
  "В наличии сейчас",
  "Быстрая доставка",
  "Надежный выбор на каждый день",
  "Отличный подарок",
  "Новинка сезона",
  "Топовая модель",
  "Рекомендуем",
  "Максимум пользы за свои деньги",
];

function buildNextValue(currentValue, snippet, start, end) {
  const before = currentValue.slice(0, start);
  const after = currentValue.slice(end);
  const needsLeadingSpace = before && !/[\s([{"'«-]$/.test(before);
  const needsTrailingSpace = after && !/^[\s)\]}",.!?:;'»-]/.test(after);
  const inserted = `${needsLeadingSpace ? " " : ""}${snippet}${needsTrailingSpace ? " " : ""}`;

  return {
    nextValue: `${before}${inserted}${after}`,
    caretPosition: before.length + inserted.length,
  };
}

export default function TextAssistField({
  value,
  onChange,
  multiline = false,
  showPhrases = true,
  assistLabel = "Эмодзи и фразы",
  rows = 3,
  ...inputProps
}) {
  const [open, setOpen] = useState(false);
  const fieldRef = useRef(null);
  const panelId = useId();
  const FieldTag = multiline ? "textarea" : "input";

  const handleInsert = (snippet) => {
    const element = fieldRef.current;
    const currentValue = value ?? "";
    const start = typeof element?.selectionStart === "number" ? element.selectionStart : currentValue.length;
    const end = typeof element?.selectionEnd === "number" ? element.selectionEnd : currentValue.length;
    const { nextValue, caretPosition } = buildNextValue(currentValue, snippet, start, end);

    onChange(nextValue);

    requestAnimationFrame(() => {
      if (!fieldRef.current) return;
      fieldRef.current.focus();
      fieldRef.current.setSelectionRange(caretPosition, caretPosition);
    });
  };

  return (
    <div className="assist-field">
      <FieldTag
        ref={fieldRef}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={multiline ? rows : undefined}
        {...inputProps}
      />

      <div className="assist-toolbar">
        <button
          type="button"
          className="assist-toggle"
          aria-expanded={open}
          aria-controls={panelId}
          onClick={() => setOpen((prev) => !prev)}
        >
          {open ? "Скрыть подсказки" : assistLabel}
        </button>

        {open && (
          <div className="assist-panel" id={panelId}>
            <div className="assist-section">
              <p className="assist-heading">Эмодзи</p>
              <div className="assist-chip-list">
                {TECH_EMOJI_OPTIONS.map((item) => (
                  <button
                    key={item}
                    type="button"
                    className="assist-chip"
                    onClick={() => handleInsert(item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>

            {showPhrases && (
              <div className="assist-section">
                <p className="assist-heading">Готовые фразы</p>
                <div className="assist-chip-list">
                  {SALES_PHRASE_OPTIONS.map((item) => (
                    <button
                      key={item}
                      type="button"
                      className="assist-chip assist-chip-text"
                      onClick={() => handleInsert(item)}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
