"use client";

import { useState } from "react";
import { createNudge, NudgeChannel, NudgeStatus } from "@/lib/api";

export default function NudgeForm({ onCreated }: { onCreated?: () => void }) {
  const [userId, setUserId] = useState("user_001");
  const [channel, setChannel] = useState<NudgeChannel>("WHATSAPP");
  const [sentTime, setSentTime] = useState("");
  const [status, setStatus] = useState<NudgeStatus>("DELIVERED");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [createdNudgeId, setCreatedNudgeId] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);
    setCreatedNudgeId(null);
    try {
      const nudge = await createNudge({
        user_id: userId,
        channel,
        sent_time: sentTime
          ? new Date(sentTime).toISOString()
          : new Date().toISOString(),
        status,
      });
      setCreatedNudgeId(nudge.id);
      setMessage("Nudge recorded successfully.");
      onCreated?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create nudge");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card flex h-full flex-col space-y-4">
      <div className="min-h-[58px]">
        <h3 className="text-base font-semibold text-slate-900">Create Nudge</h3>
        <p className="text-sm text-slate-500">
          Record a communication attempt sent to a user.
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
        <label className="label">Channel</label>
        <select
          className="input"
          value={channel}
          onChange={(e) => setChannel(e.target.value as NudgeChannel)}
        >
          <option value="WHATSAPP">WhatsApp</option>
          <option value="EMAIL">Email</option>
          <option value="SMS">SMS</option>
          <option value="PUSH">Push</option>
        </select>
      </div>

      <div>
        <label className="label">Sent Time</label>
        <input
          type="datetime-local"
          className="input"
          value={sentTime}
          onChange={(e) => setSentTime(e.target.value)}
        />
      </div>

      <div>
        <label className="label">Status</label>
        <select
          className="input"
          value={status}
          onChange={(e) => setStatus(e.target.value as NudgeStatus)}
        >
          <option value="DELIVERED">Delivered</option>
          <option value="OPENED">Opened</option>
          <option value="CLICKED">Clicked</option>
          <option value="REPLIED">Replied</option>
          <option value="FAILED">Failed</option>
        </select>
      </div>

      <button type="submit" className="btn-primary !mt-auto w-full" disabled={loading}>
        {loading ? "Saving..." : "Create Nudge"}
      </button>

      {message && <p className="text-sm text-emerald-600">{message}</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {createdNudgeId && (
        <div className="rounded-xl border border-brand-500/20 bg-brand-50 p-3 text-sm text-slate-700">
          <p className="font-semibold text-slate-900">Nudge ID created</p>
          <p className="mt-1 break-all font-mono text-xs text-slate-600">
            {createdNudgeId}
          </p>
          <p className="mt-2 text-xs text-slate-500">
            Copy this ID into the Delivery Report form when a provider outcome arrives.
          </p>
        </div>
      )}
    </form>
  );
}
