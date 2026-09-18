import React from 'react';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon, Settings } from 'lucide-react';

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex items-center gap-1 bg-slate-800 rounded-lg p-1 border border-slate-700">
      {/* Light Theme */}
      <button
        onClick={() => setTheme('light')}
        title="Light theme"
        className={`p-2 rounded transition-colors ${
          theme === 'light'
            ? 'bg-slate-600 text-yellow-300'
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <Sun size={18} />
      </button>

      {/* Dark Theme */}
      <button
        onClick={() => setTheme('dark')}
        title="Dark theme"
        className={`p-2 rounded transition-colors ${
          theme === 'dark'
            ? 'bg-slate-600 text-blue-300'
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <Moon size={18} />
      </button>

      {/* System Theme */}
      <button
        onClick={() => setTheme('system')}
        title="System theme"
        className={`p-2 rounded transition-colors ${
          theme === 'system'
            ? 'bg-slate-600 text-cyan-300'
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <Settings size={18} />
      </button>
    </div>
  );
}
