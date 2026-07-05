import { Link, NavLink, Route, Routes } from "react-router-dom";
import { Boxes, GitBranch, UploadCloud } from "lucide-react";
import UploadPage from "./pages/UploadPage.jsx";
import AnalysisPage from "./pages/AnalysisPage.jsx";
import ThemeToggle from "./components/ThemeToggle.jsx";

const navClass = ({ isActive }) =>
  `inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition ${
    isActive
      ? "bg-accent text-white"
      : "text-ink/70 hover:bg-black/5 dark:text-white/70 dark:hover:bg-white/10"
  }`;

export default function App() {
  return (
    <div className="min-h-screen bg-panel text-ink dark:bg-[#15171a] dark:text-white">
      <header className="border-b border-line bg-white/70 backdrop-blur dark:border-white/10 dark:bg-[#1d2025]/80">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <Link to="/" className="inline-flex items-center gap-3 font-semibold">
            <span className="grid size-9 place-items-center rounded-md bg-ink text-white dark:bg-white dark:text-ink">
              <Boxes size={18} />
            </span>
            <span>Code Intelligence</span>
          </Link>
          <nav className="flex items-center gap-2">
            <NavLink to="/" className={navClass}>
              <UploadCloud size={16} />
              Upload
            </NavLink>
            <NavLink to="/analysis/demo" className={navClass}>
              <GitBranch size={16} />
              Demo
            </NavLink>
            <ThemeToggle />
          </nav>
        </div>
      </header>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/analysis/:analysisId" element={<AnalysisPage />} />
      </Routes>
    </div>
  );
}

