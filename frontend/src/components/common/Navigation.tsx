// Navigation Component
// src/components/common/Navigation.tsx

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Workbook } from '../../types';
import { Menu, X, Zap, BarChart3, Search, FileText, Network, CheckCircle, Rocket, Unlink } from 'lucide-react';
// TODO: Theme toggle temporarily disabled due to path resolution issues in OneDrive path
// import ThemeToggle from './ThemeToggle';

interface NavigationProps {
  workbook: Workbook;
}

export default function Navigation({ workbook }: NavigationProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  const location = useLocation();

  const links = [
    { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { path: '/understand', label: 'Understand', icon: Search },
    { path: '/document', label: 'Document', icon: FileText },
    { path: '/dependencies', label: 'Dependencies', icon: Network },
    { path: '/parity', label: 'Parity Lab', icon: CheckCircle },
    { path: '/modernize', label: 'Modernize', icon: Rocket },
    { path: '/traceability', label: 'Traceability', icon: Unlink },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-slate-900 border-b border-slate-700 sticky top-0 z-50 transition-colors">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            to="/dashboard"
            className="flex items-center gap-2 font-bold text-xl text-cyan-400 hover:text-cyan-300 transition-colors"
          >
            <Zap size={24} />
            <span>LegacyIQ</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {links.map((link) => {
              const IconComponent = link.icon;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`px-3 py-2 rounded-lg transition-colors text-sm font-medium flex items-center gap-1 ${
                    isActive(link.path)
                      ? 'bg-cyan-600 text-white'
                      : 'text-slate-300 hover:bg-slate-800'
                  }`}
                >
                  <IconComponent size={18} />
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* Workbook ID */}
          <div className="hidden lg:flex items-center gap-4">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>ID:</span>
              <code className="bg-slate-800 px-2 py-1 rounded text-slate-300">{workbook.workbook_id}</code>
            </div>
            {/* TODO: Theme toggle <ThemeToggle /> */}
          </div>

          {/* Mobile: Theme Toggle + Menu Button */}
          <div className="lg:hidden flex items-center gap-3">
            {/* TODO: Theme toggle <ThemeToggle /> */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-slate-300 hover:text-slate-100"
            >
              {mobileMenuOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden pb-4 border-t border-slate-200 dark:border-slate-700">
            {links.map((link) => {
              const IconComponent = link.icon;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                    isActive(link.path)
                      ? 'bg-cyan-600 text-white'
                      : 'text-slate-300 hover:bg-slate-800'
                  }`}
                >
                  <IconComponent size={18} />
                  {link.label}
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </nav>
  );
}
