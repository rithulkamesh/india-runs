import { useEffect, useState } from 'react';
import Icon from './Icon';

function current(): 'dark' | 'light' {
  return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState<'dark' | 'light'>(current);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  return (
    <button
      onClick={() => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))}
      title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
      className="text-on-surface-variant hover:text-on-surface transition-colors p-1.5 rounded-lg hover:bg-surface-container-high"
    >
      <Icon name={theme === 'dark' ? 'light_mode' : 'dark_mode'} size={20} />
    </button>
  );
}
