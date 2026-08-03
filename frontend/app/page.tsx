"use client";

import { useState } from "react";
import EventForm from "@/components/EventForm";
import NudgeForm from "@/components/NudgeForm";
import DeliveryReportForm from "@/components/DeliveryReportForm";
import RecommendationCard from "@/components/RecommendationCard";
import AnalyticsSection from "@/components/AnalyticsSection";

const features = [
  ["◷", "Find the moment", "Learn each customer’s most responsive time window."],
  ["⌁", "Close the loop", "Use delivery reports to make every next nudge smarter."],
  ["✦", "Act with confidence", "Make every decision explainable, not just automated."],
];

export default function Home() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  return (
    <main className={`app-shell theme-${theme} min-h-screen overflow-hidden`}>
      <div className="hero-grid pointer-events-none fixed inset-0 opacity-40" />
      <div className="pointer-events-none fixed left-[-14rem] top-24 h-[32rem] w-[32rem] rounded-full bg-cyan-400/15 blur-[120px]" />
      <div className="pointer-events-none fixed right-[-10rem] top-[-8rem] h-[34rem] w-[34rem] rounded-full bg-violet-500/20 blur-[120px]" />

      <div className="relative mx-auto max-w-7xl px-5 sm:px-8">
        <nav className="flex h-20 items-center justify-between border-b border-white/10">
          <a href="#top" className="brand-mark flex items-center gap-3 font-semibold tracking-tight">
            <span className="brand-icon grid h-9 w-9 place-items-center rounded-xl text-lg">✦</span>
            <span>Nudge<span className="brand-accent">Flow</span></span>
          </a>
          <div className="hidden items-center gap-7 text-sm text-slate-300 md:flex">
            <a className="transition hover:text-white" href="#how-it-works">How it works</a>
            <a className="transition hover:text-white" href="#workspace">Workspace</a>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            <button
              type="button"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="theme-toggle"
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
              title={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
            >
              <span aria-hidden="true">{theme === "dark" ? "☀" : "☾"}</span>
              <span className="hidden sm:inline">{theme === "dark" ? "Light" : "Dark"}</span>
            </button>
            <a href="#workspace" className="nav-cta rounded-full px-4 py-2 text-sm font-semibold">Open workspace</a>
          </div>
        </nav>

        <section id="top" className="grid items-center gap-14 pb-24 pt-16 lg:grid-cols-[1.05fr_.95fr] lg:pb-32 lg:pt-24">
          <div className="max-w-2xl">
            <div className="hero-badge mb-6 inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em]">
              <span className="badge-dot h-1.5 w-1.5 animate-pulse rounded-full" /> Intelligent timing engine
            </div>
            <h1 className="text-balance text-5xl font-semibold leading-[1.03] tracking-[-0.055em] text-white sm:text-6xl lg:text-7xl">
              Every nudge,<br />right on <span className="text-gradient">time.</span>
            </h1>
            <p className="mt-7 max-w-xl text-lg leading-8 text-slate-300">
              Turn customer events and delivery signals into the one moment they’re most likely to respond.
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <a href="#workspace" className="btn-hero">Try the engine <span>→</span></a>
              <a href="#how-it-works" className="btn-ghost">See how it works</a>
            </div>
            <div className="hero-meta mt-10 flex flex-wrap gap-x-7 gap-y-3 text-sm">
              <span className="flex items-center gap-2"><span className="text-emerald-300">●</span> Event-driven decisions</span>
              <span className="flex items-center gap-2"><span className="brand-accent">●</span> Multi-channel learning</span>
            </div>
          </div>

          <div className="relative mx-auto w-full max-w-lg animate-float">
            <div className="absolute -inset-6 rounded-[2.5rem] bg-gradient-to-br from-cyan-400/20 via-brand-500/20 to-violet-500/20 blur-2xl" />
            <div className="glass-panel relative overflow-hidden rounded-[2rem] p-5 sm:p-6">
              <div className="mb-7 flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">Live decision</p>
                  <p className="mt-1 font-semibold">Ananya • renewal due</p>
                </div>
                <span className="rounded-full bg-emerald-300/10 px-3 py-1 text-xs font-semibold text-emerald-300">98% ready</span>
              </div>
              <div className="rounded-2xl border border-cyan-200/15 bg-gradient-to-br from-cyan-300/10 to-brand-500/10 p-5">
                <p className="text-sm text-slate-300">Recommended next nudge</p>
                <div className="mt-3 flex items-end justify-between gap-4">
                  <div><p className="text-3xl font-semibold tracking-tight">7:00 PM</p><p className="mt-1 text-sm text-cyan-200">Today · WhatsApp</p></div>
                  <div className="grid h-14 w-14 place-items-center rounded-2xl bg-cyan-300 text-2xl text-slate-950 shadow-lg shadow-cyan-500/20">↗</div>
                </div>
              </div>
              <div className="mt-6">
                <div className="mb-3 flex items-center justify-between text-sm"><span className="text-slate-300">Engagement by hour</span><span className="font-semibold text-cyan-200">Highest response</span></div>
                <div className="flex h-24 items-end gap-2">
                  {[22, 32, 28, 42, 58, 84, 100, 67, 45, 34].map((height, index) => <span key={index} className={`flex-1 rounded-t-md bg-gradient-to-t from-brand-600 to-cyan-300 ${index === 6 ? "shadow-[0_0_18px_rgba(103,232,249,.65)]" : "opacity-60"}`} style={{ height: `${height}%` }} />)}
                </div>
                <div className="mt-2 flex justify-between text-[11px] text-slate-500"><span>9 AM</span><span>3 PM</span><span>7 PM</span><span>11 PM</span></div>
              </div>
              <div className="mt-6 flex items-center gap-3 border-t border-white/10 pt-5 text-sm text-slate-300"><span className="grid h-8 w-8 place-items-center rounded-full bg-violet-400/15 text-violet-200">✦</span> Based on 24 delivery signals in the last 30 days</div>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="border-y border-white/10 py-12 sm:py-16">
          <div className="mb-9 flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="eyebrow">A simple feedback loop</p><h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">From signal to better timing.</h2></div><p className="max-w-sm text-sm leading-6 text-slate-400">No black box. Each recommendation is grounded in an event, engagement history, and its delivery outcome.</p></div>
          <div className="grid gap-4 md:grid-cols-3">{features.map(([icon, title, description], index) => <article key={title} className="feature-card"><span className="mb-7 grid h-11 w-11 place-items-center rounded-xl bg-white/5 text-xl text-cyan-200">{icon}</span><p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300/80">0{index + 1}</p><h3 className="mt-2 text-xl font-semibold">{title}</h3><p className="mt-3 leading-6 text-slate-400">{description}</p></article>)}</div>
        </section>

        <section id="workspace" className="scroll-mt-8 py-16 sm:py-20">
          <div className="mb-9 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"><div><p className="eyebrow">Command center</p><h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Put the engine to work.</h2></div><p className="max-w-md text-sm leading-6 text-slate-400">Add a customer event, record outcomes, and view a recommendation driven by recent behavior.</p></div>
          <section className="grid gap-5 lg:grid-cols-3"><EventForm /><NudgeForm /><DeliveryReportForm /></section>
          <section className="mt-5"><RecommendationCard /></section>
          <section className="mt-5"><AnalyticsSection /></section>
        </section>

        <footer className="flex flex-col gap-2 border-t border-white/10 py-8 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between"><p>© 2026 NudgeFlow. Intelligent communication timing.</p><p>Built for thoughtful customer engagement.</p></footer>
      </div>
    </main>
  );
}
