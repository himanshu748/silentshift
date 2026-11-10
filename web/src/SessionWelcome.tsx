import { KeyRound } from "lucide-react";
import { Button } from "./ui";

const INSPECTABLE = [
  { title: "Original payload", text: "The message exactly as it arrived at the native endpoint." },
  { title: "Approved meaning", text: "How the message compares with the business references that were approved." },
  { title: "Policy decision", text: "Findings, the recommendation and the route that was taken." },
  { title: "Review history", text: "Recorded reviewer actions, where your role permits them." },
] as const;

export function SessionWelcome({ onConnect }: { onConnect: () => void }) {
  return (
    <section className="welcome" aria-labelledby="session-welcome-title">
      <div>
        <span className="kicker">Local IRIS instance</span>
        <h2 id="session-welcome-title">Connect your IRIS session</h2>
        <p>
          Investigations are read from this local IRIS instance. Sign in with your IRIS
          credentials to load the case records your role allows you to see.
        </p>
        <Button kind="primary" icon={KeyRound} onClick={onConnect}>
          Connect to IRIS
        </Button>
        <p className="small quiet">
          Your credentials go only to this IRIS instance, and IRIS still checks every request and
          review action.
        </p>
      </div>
      <div>
        <h3>After connecting, you can inspect</h3>
        <ol className="welcome-list">
          {INSPECTABLE.map(({ title, text }, index) => (
            <li key={title}>
              <span className="mono">{String(index + 1).padStart(2, "0")}</span>
              <span>
                <strong>{title}</strong>
                <span>{text}</span>
              </span>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
