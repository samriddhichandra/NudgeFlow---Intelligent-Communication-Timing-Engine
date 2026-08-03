"use client";

import { useState } from "react";
import { getRecommendation, RecommendationResponse } from "@/lib/api";

function formatDateTime(iso: string) {
  try {
    return new Date(iso).toLocaleString(undefined, {
      weekday: "short",
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export default function RecommendationCard() {
  const [userId, setUserId] = useState("user_001");
  const [data, setData] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchRecommendation() {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const result = await getRecommendation(userId);
      setData(result);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load recommendation"
      );
    } finally {
      setLoading(false);
    }
  }

  const confidencePct = data ? Math.round(data.confidence * 100) : 0;

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-slate-900">
            Recommendation
          </h3>
          <p className="text-sm text-slate-500">
            Best time and channel to reach a user next.
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
          onClick={fetchRecommendation}
          className="btn-primary whitespace-nowrap"
          disabled={loading}
        >
          {loading ? "Loading..." : "Get Recommendation"}
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {data && (
        <div className="space-y-4 rounded-xl bg-gradient-to-br from-brand-50 to-indigo-50 p-5">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="label">Best Time</p>
              <p className="text-lg font-semibold text-slate-900">
                {formatDateTime(data.recommended_time)}
              </p>
            </div>
            <div>
              <p className="label">Best Channel</p>
              <p className="text-lg font-semibold text-slate-900">
                {data.channel}
              </p>
            </div>
          </div>

          <div>
            <p className="label">Confidence</p>
            <div className="flex items-center gap-3">
              <div className="h-2 w-full overflow-hidden rounded-full bg-white">
                <div
                  className="h-2 rounded-full bg-brand-600"
                  style={{ width: `${confidencePct}%` }}
                />
              </div>
              <span className="text-sm font-semibold text-slate-700">
                {confidencePct}%
              </span>
            </div>
          </div>

          <div>
            <p className="label">Explanation</p>
            <p className="text-sm leading-relaxed text-slate-700">
              {data.reason}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
