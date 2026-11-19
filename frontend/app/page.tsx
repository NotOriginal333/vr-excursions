import Link from "next/link";
import { api, CONTENT_TYPES, type Page, type Topic } from "./api";

type SearchParams = Record<string, string>;

const FILTER_LABELS = { subject: "Усі предмети", grade: "Усі класи", topic: "Усі теми" } as const;

const unique = (values: string[]) => [...new Set(values)].sort((a, b) => a.localeCompare(b, "uk", { numeric: true }));

function pageLink(params: SearchParams, page: number) {
  return `/?${new URLSearchParams({ ...params, page: String(page) })}`;
}

export default async function Catalog({ searchParams }: { searchParams: Promise<SearchParams> }) {
  const params = await searchParams;
  const [page, topics] = await Promise.all([
    api<Page>(`/excursions?${new URLSearchParams(params)}`),
    api<Topic[]>("/topics"),
  ]);

  return (
    <>
      <form className="filters">
        <input name="q" placeholder="Пошук за назвою, описом, темою" defaultValue={params.q} />
        {(["subject", "grade", "topic"] as const).map((name) => (
          <select key={name} name={name} defaultValue={params[name] ?? ""}>
            <option value="">{FILTER_LABELS[name]}</option>
            {unique(topics.map((topic) => String(topic[name]))).map((value) => (
              <option key={value}>{value}</option>
            ))}
          </select>
        ))}
        <select name="content_type" defaultValue={params.content_type ?? ""}>
          <option value="">Усі типи</option>
          {Object.entries(CONTENT_TYPES).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <button>Знайти</button>
      </form>

      <p>Знайдено: {page.total}</p>
      <ul className="catalog">
        {page.items.map((excursion) => (
          <li key={excursion.id}>
            <Link href={`/excursions/${excursion.id}`}>{excursion.title}</Link>
            <span>
              {excursion.subject}, {excursion.grade} клас, {excursion.topic}
            </span>
          </li>
        ))}
      </ul>

      <nav className="pages">
        {page.page > 1 && <Link href={pageLink(params, page.page - 1)}>← Назад</Link>}
        {page.page * page.size < page.total && <Link href={pageLink(params, page.page + 1)}>Далі →</Link>}
      </nav>
    </>
  );
}
