import { Component, type ReactNode } from "react";
import { ErrorState } from "./ui";

/** Catches render errors so users see a safe message, never a stack trace or a blank page. */
export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(error: unknown) { console.error("Render error", error); }
  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <div className="panel">
        <ErrorState title="This page could not be displayed" message="Something went wrong while drawing this screen. Your data was not changed." onRetry={() => { this.setState({ failed: false }); }} homeLink />
      </div>
    );
  }
}
