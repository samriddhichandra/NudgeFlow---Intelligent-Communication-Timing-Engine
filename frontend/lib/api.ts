const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type EventPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type NudgeChannel = "WHATSAPP" | "EMAIL" | "SMS" | "PUSH";
export type NudgeStatus =
  | "DELIVERED"
  | "OPENED"
  | "CLICKED"
  | "REPLIED"
  | "FAILED";

export interface EventPayload {
  user_id: string;
  event_type: string;
  event_time: string;
  priority: EventPriority;
}

export interface NudgePayload {
  user_id: string;
  channel: NudgeChannel;
  sent_time: string;
  status: NudgeStatus;
}

export interface DeliveryReportPayload {
  nudge_id: string;
  status: NudgeStatus;
  meta?: string;
}

export interface RecommendationResponse {
  user_id: string;
  event_id: string | null;
  recommended_time: string;
  channel: string;
  confidence: number;
  reason: string;
}

export interface AnalyticsResponse {
  user_id: string;
  engagement_by_bucket: Record<string, number>;
  engagement_by_channel: Record<string, number>;
  total_nudges: number;
  recommendation: RecommendationResponse | null;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (Array.isArray(body.detail)) {
        detail = body.detail
          .map((issue: { loc?: string[]; msg?: string }) =>
            `${issue.loc?.slice(-1).join(".") || "Request"}: ${issue.msg || "Invalid value"}`
          )
          .join("; ");
      } else {
        detail = body.detail || detail;
      }
    } catch {
      // ignore
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function createEvent(payload: EventPayload) {
  const res = await fetch(`${API_BASE_URL}/api/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<EventPayload & { id: string }>(res);
}

export async function createNudge(payload: NudgePayload) {
  const res = await fetch(`${API_BASE_URL}/api/nudges`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<NudgePayload & { id: string }>(res);
}

export async function submitDeliveryReport(payload: DeliveryReportPayload) {
  const res = await fetch(`${API_BASE_URL}/api/delivery-reports`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<DeliveryReportPayload & { id: string }>(res);
}

export async function getRecommendation(userId: string) {
  const res = await fetch(`${API_BASE_URL}/api/recommendation/${userId}`);
  return handleResponse<RecommendationResponse>(res);
}

export async function getEventRecommendation(eventId: string) {
  const res = await fetch(`${API_BASE_URL}/api/events/${eventId}/recommendation`);
  return handleResponse<RecommendationResponse>(res);
}

export async function getAnalytics(userId: string) {
  const res = await fetch(`${API_BASE_URL}/api/users/${userId}/analytics`);
  return handleResponse<AnalyticsResponse>(res);
}
