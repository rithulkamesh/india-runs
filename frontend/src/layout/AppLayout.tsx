import { NavLink, Outlet, Link, useNavigate } from 'react-router-dom';
import Icon from '../components/Icon';
import ThemeToggle from '../components/ThemeToggle';

const nav = [
  { to: '/dashboard', icon: 'dashboard', label: 'Overview' },
  { to: '/candidates', icon: 'person_search', label: 'Candidate Search' },
  { to: '/talent-dna', icon: 'fingerprint', label: 'Talent DNA' },
  { to: '/knowledge-graph', icon: 'account_tree', label: 'Candidate Graph' },
];

function NavItem({ to, icon, label }: { to: string; icon: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2 rounded-lg text-label-md font-medium transition-colors duration-200 ${
          isActive
            ? 'bg-primary-container text-on-primary-container border-l-2 border-primary font-semibold'
            : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high border-l-2 border-transparent'
        }`
      }
    >
      <Icon name={icon} size={20} />
      <span>{label}</span>
    </NavLink>
  );
}

export default function AppLayout() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-surface text-on-surface">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 border-r border-outline-variant bg-surface-container flex flex-col py-stack-md z-30">
        <Link to="/" className="px-6 mb-8 block">
          <h1 className="text-headline-md font-bold tracking-tight">India Runs</h1>
          <p className="text-label-md text-primary opacity-80">Talent Intelligence</p>
        </Link>

        <nav className="flex-1 px-3 space-y-1 overflow-y-auto custom-scrollbar">
          {nav.map((n) => (
            <NavItem key={n.to} {...n} />
          ))}
        </nav>
      </aside>

      {/* Top bar */}
      <header className="fixed top-0 right-0 left-64 h-16 bg-surface-container border-b border-outline-variant flex items-center justify-between px-container-padding z-20">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const q = new FormData(e.currentTarget).get('q') as string;
            navigate(`/candidates${q?.trim() ? `?q=${encodeURIComponent(q.trim())}` : ''}`);
          }}
          className="flex items-center gap-4 flex-1 max-w-xl"
        >
          <div className="relative w-full">
            <Icon
              name="search"
              className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant"
              size={20}
            />
            <input
              name="q"
              className="w-full bg-surface-container-low border border-outline-variant rounded-full py-1.5 pl-10 pr-4 text-body-md placeholder:text-outline focus:outline-none focus:border-primary transition-colors"
              placeholder="Search candidates by skill, role, or company…"
              type="text"
            />
          </div>
        </form>
        <ThemeToggle />
      </header>

      {/* Content */}
      <main className="pl-64 pt-16 min-h-screen">
        <Outlet />
      </main>
    </div>
  );
}
