"use client";

import { useState } from "react";
import { getAnalytics, AnalyticsResponse } from "@/lib/api";

const BUCKET_ORDER = [
  "6AM-9AM",
  "9AM-12PM",
  "12PM-3PM",
  "3PM-6PM",
  "6PM-9PM",
  "9PM-12AM",
  "12AM-6AM",
];

function BarRow({
  label,
  value,
  max,
}: {
  label: string;
  value: number;
  max: number;
}) {
  const pct = max > 0 ? Math.max(4, (Math.max(value, 0) / max) * 100) : 0;
  const negative = value < 0;
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs text-slate-600">
        <span className="font-medium">{label}</span>
        <span>{value.toFixed(2)}</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-2 rounded-full ${
            negative ? "bg-red-400" : "bg-brand-500"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function AnalyticsSection() {
  const [userId, setUserId] = useState("user_001");
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchAnalytics() {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const result = await getAnalytics(userId);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  }

  const bucketEntries = data
    ? BUCKET_ORDER.filter((b) => b in data.engagement_by_bucket).map((b) => [
        b,
        data.engagement_by_bucket[b],
      ] as [string, number])
    : [];
  const maxBucket = bucketEntries.length
    ? Math.max(...bucketEntries.map(([, v]) => Math.abs(v)), 0.01)
    : 0.01;

  const channelEntries = data ? Object.entries(data.engagement_by_channel) : [];
  const maxChannel = channelEntries.length
    ? Math.max(...channelEntries.map(([, v]) => Math.abs(v)), 0.01)
    : 0.01;

  return (
    <div className="card space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Analytics</h3>
          <p className="text-sm text-slate-500">
            Engagement breakdown by time bucket and channel.
          </p>
        </div>
      </div>

      <div className="flex gap-2">
        <input
          className="input"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="user_001"
        />
        <button
          onClick={fetchAnalytics}
          className="btn-primary whitespace-nowrap"
          disabled={loading}
        >
          {loading ? "Loading..." : "Load Analytics"}
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {data && (
        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-3">
            <p className="text-sm font-semibold text-slate-800">
              Engagement by Time Bucket
            </p>
            <div className="space-y-3">
              {bucketEntries.map(([bucket, score]) => (
                <BarRow key={bucket} label={bucket} value={score} max={maxBucket} />
              ))}
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-sm font-semibold text-slate-800">
              Engagement by Channel
            </p>
            <div className="space-y-3">
              {channelEntries.map(([channel, score]) => (
                <BarRow
                  key={channel}
                  label={channel}
                  value={score}
                  max={maxChannel}
                />
              ))}
              {channelEntries.length === 0 && (
                <p className="text-sm text-slate-400">No nudge history yet.</p>
              )}
            </div>
          </div>

          <div className="md:col-span-2 rounded-xl bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-800">
              Recommendation Summary
            </p>
            <p className="mt-1 text-sm text-slate-600">
              Total nudges analyzed:{" "}
              <span className="font-medium">{data.total_nudges}</span>
            </p>
            {data.recommendation ? (
              <p className="mt-1 text-sm text-slate-600">
                Best window is <strong>{data.recommendation.channel}</strong> around{" "}
                <strong>
                  {new Date(data.recommendation.recommended_time).toLocaleString()}
                </strong>{" "}
                with {Math.round(data.recommendation.confidence * 100)}% confidence.
              </p>
            ) : (
              <p className="mt-1 text-sm text-slate-400">
                Not enough data to generate a recommendation yet.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
