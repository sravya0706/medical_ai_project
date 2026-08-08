import "./VitalLine.css";

/**
 * The page's one signature element: a thin ECG-style trace that draws
 * itself while the assistant is "thinking." Ties to the medical subject
 * without reaching for a stethoscope icon or a red cross — the vital
 * line is quiet, precise, and only appears when something is actually
 * being computed.
 */
export default function VitalLine({ label = "MediAssist is thinking" }) {
  return (
    <div className="vital-line" role="status" aria-label={label}>
      <svg viewBox="0 0 240 40" preserveAspectRatio="none" className="vital-line__svg">
        <path
          className="vital-line__trace"
          d="M0,20 L60,20 L72,20 L80,4 L90,36 L100,20 L112,20 L240,20"
          fill="none"
        />
      </svg>
      <span className="vital-line__label mono">{label}&hellip;</span>
    </div>
  );
}
