import { ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";


export function NotFoundPage() {
  return (
    <section className="not-found page-width">
      <span>404</span>
      <h1>That path does not lead to an agency.</h1>
      <p>Return to the directory and describe what happened.</p>
      <Link className="button button-primary" to="/"><ArrowLeft aria-hidden="true" /> Back to the directory</Link>
    </section>
  );
}
