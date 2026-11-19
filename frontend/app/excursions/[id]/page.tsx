import { notFound } from "next/navigation";
import { api, CONTENT_TYPES, type Excursion } from "../../api";
import PanoramaViewer from "./panorama-viewer";

export default async function ExcursionCard({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!/^\d+$/.test(id)) notFound();
  const excursion = await api<Excursion>(`/excursions/${id}`);

  return (
    <article>
      <h1>{excursion.title}</h1>
      <PanoramaViewer src={excursion.media_url} />
      <p>{excursion.description}</p>
      <p>
        {excursion.subject}, {excursion.grade} клас, {excursion.topic}. {CONTENT_TYPES[excursion.content_type]}.
      </p>
      <p className="attribution">
        Автор: {excursion.author}. Ліцензія:{" "}
        {excursion.license_url ? <a href={excursion.license_url}>{excursion.license}</a> : excursion.license}.{" "}
        <a href={excursion.page_url}>Сторінка файлу у Wikimedia Commons</a>
      </p>
    </article>
  );
}
