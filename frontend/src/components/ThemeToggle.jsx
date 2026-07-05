import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [dark, setDark] = useState(() => localStorage.getItem("theme") === "dark");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  return (
    <button className="icon-button" onClick={() => setDark((value) => !value)} title="Toggle theme">
      {dark ? <Sun size={17} /> : <Moon size={17} />}
    </button>
  );
}

