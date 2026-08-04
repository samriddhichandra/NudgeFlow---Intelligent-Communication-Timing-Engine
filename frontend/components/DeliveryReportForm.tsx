"use client";

import { useState } from "react";
import { submitDeliveryReport, NudgeStatus } from "@/lib/api";

export default function DeliveryReportForm({
  onSubmitted,
}: {
  onSubmitted?: () => void;
}) {
  const [nudgeId, setNudgeId] = useState("");
  const [status, setStatus] = useState<NudgeStatus>("OPENED");
  const [meta, setMeta] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(nudgeId)) {
      setError("Enter a valid nudge UUID. Create a nudge first, then copy its Nudge ID here.");
      return;
    }
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      await submitDeliveryReport({
        nudge_id: nudgeId,
        status,
        meta: meta || undefined,
      });
      setMessage("Delivery report submitted.");
      onSubmitted?.();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to submit delivery report"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card flex h-full flex-col space-y-4">
      <div className="min-h-[58px]">
        <h3 className="text-base font-semibold text-slate-900">
          Submit Delivery Report
        </h3>
        <p className="text-sm text-slate-500">
          Update the status of a previously sent nudge using its Nudge ID.
        </p>
      </div>

      <div>
        <label className="label">Nudge ID</label>
        <input
          className="input"
          value={nudgeId}
          onChange={(e) => setNudgeId(e.target.value)}
          placeholder="UUID of an existing nudge"
          required
        />
      </div>

      <div>
        <label className="label">New Status</label>
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

      <div>
        <label className="label">Metadata (optional)</label>
        <input
          className="input"
          value={meta}
          onChange={(e) => setMeta(e.target.value)}
          placeholder="e.g. webhook_provider_id"
        />
      </div>

      <button type="submit" className="btn-primary !mt-auto w-full" disabled={loading}>
        {loading ? "Submitting..." : "Submit Report"}
      </button>

      {message && <p className="text-sm text-emerald-600">{message}</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
    </form>
  );
}
