import { useState, useEffect } from "react";
import CategorySelect from "./CategorySelect";
import { getSubcategoriesByCategory } from "../api/subcategories.api";
import { uploadApi } from "../api/upload.api";

export default function ProductForm({ categories, onSubmit }) {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [subcategoryId, setSubcategoryId] = useState("");
  const [subcategories, setSubcategories] = useState([]);
  const [image, setImage] = useState(null);

  useEffect(() => {
    if (!categoryId) return;

    const load = async () => {
      const data = await getSubcategoriesByCategory(categoryId);
      setSubcategories(data);
    };

    load();
  }, [categoryId]);

  const handleImageUpload = async (file) => {
    if (!file) return;

    const res = await uploadApi.uploadImage(file);
    // подстрой под формат ответа бэка
    setImage(res.data.file_url  || res.data.url || res.data.path);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    onSubmit({
      name,
      price,
      category_id: Number(categoryId),
      subcategory_id: Number(subcategoryId),
      image: image,
    });
  };

  return (
    <form onSubmit={handleSubmit} style={{ border: "1px solid #ccc", padding: 16 }}>
      <h3>Добавить товар</h3>

      <input
        placeholder="Название"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      <input
        placeholder="Цена"
        value={price}
        onChange={(e) => setPrice(e.target.value)}
      />

      <CategorySelect
        categories={categories}
        value={categoryId}
        onChange={setCategoryId}
      />

      <select value={subcategoryId} onChange={(e) => setSubcategoryId(e.target.value)}>
        <option value="">Выбери подкатегорию</option>
        {subcategories.map((s) => (
          <option key={s.id} value={s.id}>
            {s.name}
          </option>
        ))}
      </select>

      <input
        type="file"
        onChange={(e) => handleImageUpload(e.target.files[0])}
      />

      {image && <img src={image} style={{ width: 100, marginTop: 10 }} />}

      <button type="submit">Сохранить</button>
    </form>
  );
}