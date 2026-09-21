import { useState } from "react";
import { AppShell } from "./components/AppShell";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { EmptyState } from "./components/ui";
import { ActivityPage } from "./pages/ActivityPage";
import { AboutPage } from "./pages/AboutPage";
import { DrugLibraryPage } from "./pages/DrugLibraryPage";
import { DrugProfilePage } from "./pages/DrugProfilePage";
import { LabTrendsPage } from "./pages/LabTrendsPage";
import { OverviewPage } from "./pages/OverviewPage";
import { ReviewPage } from "./pages/ReviewPage";
import { href, useRoute } from "./lib/route";
import { StoreProvider } from "./lib/store";

export default function App() {
  const route = useRoute();
  const [drugName, setDrugName] = useState("");
  return (
    <StoreProvider>
      <AppShell route={route} drugName={drugName || undefined}>
        <ErrorBoundary key={`${route.name}:${route.id ?? ""}`}>
          {route.name === "overview" && <OverviewPage />}
          {route.name === "review" && <ReviewPage />}
          {route.name === "drugs" && <DrugLibraryPage />}
          {route.name === "drug" && route.id && <DrugProfilePage id={route.id} onLoaded={setDrugName} />}
          {route.name === "labs" && <LabTrendsPage />}
          {route.name === "activity" && <ActivityPage />}
          {route.name === "about" && <AboutPage />}
          {route.name === "notfound" && (
            <div className="panel"><EmptyState icon="search" title="Page not found" action={<a className="btn btn-primary" href={href("/")}>Go to overview</a>}>That address doesn’t match a page in PharmaSafe AI.</EmptyState></div>
          )}
        </ErrorBoundary>
      </AppShell>
    </StoreProvider>
  );
}
