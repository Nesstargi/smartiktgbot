export default function ProductTable({ products, onDelete }) {
  return (
    <table style={{ width: "100%", borderCollapse: "collapse" }}>
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
            <td>
              {p.image && (
                <img
                  src={p.image}
                  alt=""
                  style={{ width: 60, height: 60, objectFit: "cover" }}
                />
              )}
            </td>
            <td>{p.name}</td>
            <td>{p.price}</td>
            <td>{p.category?.name}</td>
            <td>{p.subcategory?.name}</td>
            <td>
              <button onClick={() => onDelete(p.id)}>🗑 Удалить</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
