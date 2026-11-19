import { notFound } from "next/navigation";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export type Excursion = {
  id: number;
  title: string;
  description: string;
  content_type: string;
  page_url: string;
  media_url: string;
  license: string;
  license_url: string | null;
  author: string;
  subject: string;
  grade: number;
  topic: string;
};

export type Topic = Pick<Excursion, "subject" | "grade" | "topic">;

export type Page = { items: Excursion[]; total: number; page: number; size: number };

export const CONTENT_TYPES: Record<string, string> = {
  "360_photo": "Сферична панорама 360°",
  partial_panorama: "Часткова панорама",
};

export async function api<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}/api${path}`, { cache: "no-store" });
  if (response.status === 404 || response.status === 422) notFound();
  if (!response.ok) throw new Error(`API ${response.status}: ${path}`);
  return response.json();
}
