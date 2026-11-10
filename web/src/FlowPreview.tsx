import { useEffect, useState } from "react";
import { ArrowRight, Pause, Play, RotateCcw } from "lucide-react";

const stages = [
  {
    name: "Receive",
    detail:
      "The payload is valid JSON. The original quantity, unit and event time stay intact.",
  },
  {
    name: "Read evidence",
    detail:
      "The investigation reads the message, approved contracts, related records and similar precedents.",
  },
  {
    name: "Policy gate",
    detail:
      "Deterministic policy checks current authority. A plausible conversion cannot authorize release.",
  },
  {
    name: "Route",
    detail:
      "IRIS preserves the outcome and receipt. This example explains the route; it does not send a transaction.",
  },
];

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** An explicitly labeled illustration, never a substitute for native execution. */
export default function FlowPreview() {
  const [approved, setApproved] = useState(false);
  const [step, setStep] = useState(2);
  const [playing, setPlaying] = useState(false);
  useEffect(() => {
    if (!playing) return;
    const timer = window.setTimeout(() => {
      if (step === stages.length - 1) setPlaying(false);
      else setStep((value) => value + 1);
    }, 900);
    return () => window.clearTimeout(timer);
  }, [playing, step]);
  const select = (value: boolean) => {
    setApproved(value);
    setPlaying(false);
    setStep(2);
  };
  const decided = step >= 2;
  return (
    <figure className="flow" aria-label="Interactive semantic policy illustration">
      <div className="flow-bar">
        <span className="flow-label">Illustration · synthetic values</span>
        <code>PO-2048</code>
      </div>
      <div className="flow-body">
        <div className="flow-toggle" role="group" aria-label="Example contract">
          <button type="button" aria-pressed={!approved} onClick={() => select(false)}>
            Unsupported change
          </button>
          <button type="button" aria-pressed={approved} onClick={() => select(true)}>
            Approved amendment
          </button>
        </div>

        <div className="flow-compare">
          <div>
            <span className="kicker">Partner sends</span>
            <strong className="mono">
              20 <small>CASE</small>
            </strong>
            <span className="quiet small">Original message</span>
          </div>
          <span className={`flow-mark ${approved ? "eq" : "ne"}`} aria-hidden="true">
            {approved ? "=" : "≠"}
          </span>
          <div>
            <span className="kicker">Approved evidence</span>
            <strong className="mono">
              {approved ? "20" : "240"} <small>{approved ? "CASE" : "EA"}</small>
            </strong>
            <span className="quiet small">{approved ? "Effective amendment" : "Active contract"}</span>
          </div>
        </div>

        <ol className="flow-steps" aria-label="Investigation stages">
          {stages.map(({ name }, index) => (
            <li key={name}>
              <button
                type="button"
                aria-pressed={step === index}
                data-reached={index <= step}
                onClick={() => {
                  setPlaying(false);
                  setStep(index);
                }}
              >
                <span className="mono">{String(index + 1).padStart(2, "0")}</span>
                {name}
              </button>
            </li>
          ))}
        </ol>
        <p className="flow-detail" aria-live="polite">
          {stages[step]!.detail}
        </p>

        <div
          className={`flow-outcome ${decided ? (approved ? "allow" : "hold") : "pending"}`}
          aria-live="polite"
        >
          <strong>
            {!decided
              ? "Awaiting policy"
              : approved
                ? "Eligible for delivery"
                : "Held before delivery"}
          </strong>
          <span>
            {!decided
              ? "Evidence is still being read."
              : approved
                ? "Current approved evidence authorizes 20 CASE."
                : "No approved CASE-to-EA conversion exists."}
          </span>
        </div>

        <div className="flow-foot">
          <button
            type="button"
            className="link"
            onClick={() => {
              if (playing) {
                setPlaying(false);
              } else if (reducedMotion()) {
                setStep(stages.length - 1);
              } else {
                setStep(0);
                setPlaying(true);
              }
            }}
          >
            {playing ? (
              <Pause size={14} aria-hidden="true" />
            ) : step === stages.length - 1 ? (
              <RotateCcw size={14} aria-hidden="true" />
            ) : (
              <Play size={14} aria-hidden="true" />
            )}
            {playing ? "Pause walkthrough" : step === stages.length - 1 ? "Replay walkthrough" : "Play the walkthrough"}
          </button>
          <span className="quiet small">No live API or model call</span>
        </div>
      </div>
      <figcaption>
        <a className="link" href="/#scenarios">
          Run the real scenario in IRIS <ArrowRight size={13} aria-hidden="true" />
        </a>
      </figcaption>
    </figure>
  );
}
