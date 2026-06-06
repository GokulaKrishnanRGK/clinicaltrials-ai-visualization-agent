import "../styles/components/JsonPanel.css";

type JsonPanelProps = {
  title: string;
  value: unknown;
};

export function JsonPanel({ title, value }: JsonPanelProps) {
  return (
    <section className="json-panel">
      <header>
        <h2>{title}</h2>
      </header>
      <pre>{JSON.stringify(value, null, 2)}</pre>
    </section>
  );
}
