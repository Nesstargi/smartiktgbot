export default function CategorySelect({
  categories,
  value,
  onChange,
}) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">Выбери категорию</option>
      {categories.map((c) => (
        <option key={c.id} value={c.id}>
          {c.name}
        </option>
      ))}
    </select>
  );
}
