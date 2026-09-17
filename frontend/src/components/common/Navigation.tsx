// Navigation Component
// src/components/common/Navigation.tsx

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Workbook } from '../../types';
import { Menu, X } from 'lucide-react';

interface NavigationProps {
  workbook: Workbook;
}

export default function Navigation({ workbook }: NavigationProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  const location = useLocation();

  const links = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/understand', label: 'Understand', icon: '🔍' },
    { path: '/document', label: 'Document', icon: '📋' },
    { path: '/dependencies', label: 'Dependencies', icon: '🗺️' },
    { path: '/parity', label: 'Parity Lab', icon: '✅' },
    { path: '/modernize', label: 'Modernize', icon: '🚀' },
    { path: '/traceability', label: 'Traceability', icon: '🔗' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-slate-900 border-b border-slate-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            to="/dashboard"
            className="flex items-center gap-2 font-bold text-xl text-cyan-400 hover:text-cyan-300 transition-colors"
          >
            <span>⚡</span>
            <span>LegacyIQ</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {links.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3 py-2 rounded-lg transition-colors text-sm font-medium ${
                  isActive(link.path)
                    ? 'bg-cyan-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <span className="mr-1">{link.icon}</span>
                {link.label}
              </Link>
            ))}
          </div>

          {/* Workbook ID */}
          <div className="hidden lg:flex items-center gap-2 text-xs text-slate-400">
            <span>ID:</span>
            <code className="bg-slate-800 px-2 py-1 rounded">{workbook.workbook_id}</code>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-slate-400 hover:text-slate-300"
          >
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden pb-4 border-t border-slate-700">
            {links.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`block px-4 py-2 rounded-lg transition-colors ${
                  isActive(link.path)
                    ? 'bg-cyan-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <span className="mr-2">{link.icon}</span>
                {link.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}
