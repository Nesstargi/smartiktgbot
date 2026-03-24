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
  "📲",
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

const SALES_EMOJI_OPTIONS = [
  "🔥",
  "💥",
  "✅",
  "💚",
  "⭐",
  "🌟",
  "⚡",
  "🏷️",
  "🛍️",
  "🛒",
  "🎁",
  "🚚",
  "📦",
  "💎",
  "📣",
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
  showSalesEmojis = true,
  assistLabel = "Эмодзи и подсказки",
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
              <p className="assist-heading">Эмодзи по теме техники</p>
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

            {showSalesEmojis && (
              <div className="assist-section">
                <p className="assist-heading">Продающие эмодзи</p>
                <div className="assist-chip-list">
                  {SALES_EMOJI_OPTIONS.map((item) => (
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
            )}
          </div>
        )}
      </div>
    </div>
  );
}
