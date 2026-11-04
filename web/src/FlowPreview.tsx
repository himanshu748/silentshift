import { useEffect, useState } from "react";
import {
  ArrowRight,
  Check,
  FileJson2,
  GitCompareArrows,
  Play,
  RotateCcw,
  ShieldCheck,
  Workflow,
  X,
} from "lucide-react";

const stages = [
  {
    name: "Receive",
    icon: FileJson2,
    detail:
      "The payload is valid JSON. The original quantity, unit and event time stay intact.",
  },
  {
    name: "Read evidence",
    icon: GitCompareArrows,
    detail:
      "The investigation reads the message, approved contracts, related records and similar precedents.",
  },
  {
    name: "Policy gate",
    icon: ShieldCheck,
    detail:
      "Deterministic policy checks current authority. A plausible conversion cannot authorize release.",
  },
  {
    name: "Route",
    icon: Workflow,
    detail:
      "IRIS preserves the outcome and receipt. The example below explains the route; it does not send a transaction.",
  },
];

/** An explicitly labeled illustration, never a substitute for native execution. */
export default function FlowPreview() {
  const [approved, setApproved] = useState(false);
  const [step, setStep] = useState(2);
  const [playing, setPlaying] = useState(false);
  useEffect(() => {
    if (!playing) return;
    const timer = window.setTimeout(() => {
      if (step === 3) setPlaying(false);
      else setStep((value) => value + 1);
    }, 700);
    return () => window.clearTimeout(timer);
  }, [playing, step]);
  const select = (value: boolean) => {
    setApproved(value);
    setPlaying(false);
    setStep(2);
  };
  return (
    <div
      className={`flow-preview ${approved ? "flow-approved" : ""}`}
      aria-label="Interactive semantic policy illustration"
    >
      <div className="flow-window-bar">
        <span className="flow-window-dots" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
        <span>Order investigation</span>
        <code>PO-2048</code>
      </div>
      <div className="flow-preview-inner">
        <div className="flow-mode">
          <span className="flow-label">Explore the decision</span>
          <span>Illustrated · synthetic</span>
        </div>
        <div
          className="flow-variants"
          role="group"
          aria-label="Example contract"
        >
          <button aria-pressed={!approved} onClick={() => select(false)}>
            Unsupported change
          </button>
          <button aria-pressed={approved} onClick={() => select(true)}>
            Approved amendment
          </button>
        </div>
        <div className="flow-comparison">
          <div>
            <span>Partner sends</span>
            <strong>
              20 <small>CASE</small>
            </strong>
            <code>Original message</code>
          </div>
          <span className="flow-compare-mark" aria-hidden="true">
            {approved ? "=" : "≠"}
          </span>
          <div key={String(approved)} className="flow-reference">
            <span>Approved evidence</span>
            <strong>
              {approved ? "20" : "240"}{" "}
              <small>{approved ? "CASE" : "EA"}</small>
            </strong>
            <code>{approved ? "Effective amendment" : "Active contract"}</code>
          </div>
        </div>
        <div
          className="flow-stage-buttons"
          role="group"
          aria-label="Investigation stages"
        >
          {stages.map(({ name, icon: Icon }, index) => (
            <button
              key={name}
              aria-pressed={step === index}
              className={`${index <= step ? "flow-reached" : ""} ${step === index ? "flow-current" : ""}`}
              onClick={() => {
                setPlaying(false);
                setStep(index);
              }}
            >
              <span>
                <Icon size={18} aria-hidden="true" />
              </span>
              <small>{name}</small>
            </button>
          ))}
        </div>
        <div className="flow-step-detail" key={step} aria-live="polite">
          <span className="flow-step-number">
            {String(step + 1).padStart(2, "0")}
          </span>
          <p>{stages[step]!.detail}</p>
        </div>
        <div className="flow-outcome" aria-live="polite" key={String(approved)}>
          <span className="flow-outcome-icon">
            {approved ? <Check size={21} /> : <X size={21} />}
          </span>
          <div>
            <strong>
              {approved ? "Eligible for delivery" : "Held before delivery"}
            </strong>
            <p>
              {approved
                ? "Current approved evidence authorizes 20 CASE."
                : "No approved CASE-to-EA conversion exists."}
            </p>
          </div>
          <ShieldCheck size={18} aria-hidden="true" />
        </div>
        <div className="flow-preview-footer">
          <button
            onClick={() => {
              if (playing) {
                setPlaying(false);
                setStep(0);
              } else if (
                window.matchMedia("(prefers-reduced-motion: reduce)").matches
              ) {
                setStep(3);
              } else {
                setStep(0);
                setPlaying(true);
              }
            }}
          >
            {playing ? <RotateCcw size={14} /> : <Play size={14} />}{" "}
            {playing ? "Reset walkthrough" : "Play the walkthrough"}
          </button>
          <span>No live API or model call</span>
        </div>
      </div>
      <a className="flow-live-link" href="#scenarios">
        Run the real scenario in IRIS <ArrowRight size={14} />
      </a>
    </div>
  );
}
