import { NavLink } from "react-router-dom";

export default function NavBar() {
  const linkClass = ({ isActive }) =>
    `text-[14px] tracking-wide transition-colors ${
      isActive ? "text-pine font-medium" : "text-muted hover:text-text"
    }`;

  return (
    <header className="flex items-center justify-between border-b border-text/10 px-6 py-5">
      <div className="flex items-center gap-2.5">
        <div className="h-2.5 w-2.5 rounded-full bg-pine" />
        <span className="font-display text-xl font-bold text-text">Programming tutor</span>
      </div>
      <nav className="flex gap-7">
        <NavLink to="/" end className={linkClass}>
          Home
        </NavLink>
        <NavLink to="/chat" className={linkClass}>
          Chat
        </NavLink>
        <NavLink to="/evaluation" className={linkClass}>
          Evaluation
        </NavLink>
      </nav>
    </header>
  );
}