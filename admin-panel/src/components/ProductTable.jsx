export default function ProductTable({ products, onDelete }) {
  return (
    <div className="table-wrap">
      <table className="table table-compact">
        <thead>
          <tr>
            <th>Фото</th>
            <th>Название</th>
            <th>Цена</th>
            <th>Категория</th>
            <th>Подкатегория</th>
            <th>Действия</th>
          </tr>
        </thead>

        <tbody>
          {products.map((p) => (
            <tr key={p.id}>
              <td data-label="Фото">
                {p.image && (
                  <img
                    src={p.image}
                    alt=""
                    loading="lazy"
                    decoding="async"
                    width={60}
                    height={60}
                    style={{ width: 60, height: 60, objectFit: "cover" }}
                  />
                )}
              </td>
              <td data-label="Название">{p.name}</td>
              <td data-label="Цена">{p.price}</td>
              <td data-label="Категория">{p.category?.name}</td>
              <td data-label="Подкатегория">{p.subcategory?.name}</td>
              <td data-label="Действия" className="actions">
                <button onClick={() => onDelete(p.id)}>🗑 Удалить</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
