"use client";

import { useState } from "react";
import {
  createEvent,
  EventPriority,
  getEventRecommendation,
  RecommendationResponse,
} from "@/lib/api";

export default function EventForm({ onCreated }: { onCreated?: () => void }) {
  const [userId, setUserId] = useState("user_001");
  const [eventType, setEventType] = useState("cart_abandon");
  const [eventTime, setEventTime] = useState("");
  const [priority, setPriority] = useState<EventPriority>("MEDIUM");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [recommendation, setRecommendation] =
    useState<RecommendationResponse | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);
    setRecommendation(null);
    try {
      const event = await createEvent({
        user_id: userId,
        event_type: eventType,
        event_time: eventTime
          ? new Date(eventTime).toISOString()
          : new Date().toISOString(),
        priority,
      });
      const schedule = await getEventRecommendation(event.id);
      setRecommendation(schedule);
      setMessage("Event created and nudge schedule generated.");
      onCreated?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create event");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card flex h-full flex-col space-y-4">
      <div className="min-h-[58px]">
        <h3 className="text-base font-semibold text-slate-900">Create Event</h3>
        <p className="text-sm text-slate-500">
          Log a new user event that may trigger a nudge.
        </p>
      </div>

      <div>
        <label className="label">User ID</label>
        <input
          className="input"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          required
        />
      </div>

      <div>
        <label className="label">Event Type</label>
        <input
          className="input"
          value={eventType}
          onChange={(e) => setEventType(e.target.value)}
          placeholder="e.g. cart_abandon"
          required
        />
      </div>

      <div>
        <label className="label">Event Time</label>
        <input
          type="datetime-local"
          className="input"
          value={eventTime}
          onChange={(e) => setEventTime(e.target.value)}
        />
      </div>

      <div>
        <label className="label">Priority</label>
        <select
          className="input"
          value={priority}
          onChange={(e) => setPriority(e.target.value as EventPriority)}
        >
          <option value="LOW">LOW</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="HIGH">HIGH</option>
          <option value="CRITICAL">CRITICAL</option>
        </select>
      </div>

      <button type="submit" className="btn-primary !mt-auto w-full" disabled={loading}>
        {loading ? "Creating..." : "Create Event"}
      </button>

      {message && <p className="text-sm text-emerald-600">{message}</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {recommendation && (
        <div className="rounded-lg bg-brand-50 p-3 text-sm text-slate-700">
          <p className="font-semibold text-slate-900">Recommended next nudge</p>
          <p className="mt-1">
            {recommendation.channel} at{" "}
            {new Date(recommendation.recommended_time).toLocaleString()}.
          </p>
          <p className="mt-1 text-xs text-slate-500">{recommendation.reason}</p>
        </div>
      )}
    </form>
  );
}
