import { useEffect, useMemo, useState } from "react";

import {
  createCategory,
  deleteCategory,
  getCategories,
  updateCategory,
} from "../api/categories.api";
import {
  createProduct,
  deleteProduct,
  getProducts,
  updateProduct,
} from "../api/products.api";
import {
  createSubcategory,
  deleteSubcategory,
  getAllSubcategories,
  updateSubcategory,
} from "../api/subcategories.api";
import UploadField from "../components/UploadField";
import { buildMediaUrl } from "../utils/media";

function canPreview(value) {
  return !!value && (value.startsWith("/") || value.startsWith("http"));
}

export default function CatalogPage() {
  const [categories, setCategories] = useState([]);
  const [subcategories, setSubcategories] = useState([]);
  const [products, setProducts] = useState([]);

  const [categoryName, setCategoryName] = useState("");
  const [subcategoryName, setSubcategoryName] = useState("");
  const [subcategoryCategoryId, setSubcategoryCategoryId] = useState("");
  const [subcategoryImageUrl, setSubcategoryImageUrl] = useState("");

  const [productForm, setProductForm] = useState({
    name: "",
    description: "",
    subcategory_id: "",
    image_file_id: "",
  });
  const [productFilterSubcategoryId, setProductFilterSubcategoryId] = useState(() => localStorage.getItem("catalog_product_filter_subcategory_id") || "");

  const categoryMap = useMemo(
    () => new Map(categories.map((item) => [item.id, item.name])),
    [categories],
  );

  const filteredProducts = useMemo(() => {
    if (!productFilterSubcategoryId) return products;
    return products.filter(
      (item) => item.subcategory_id === Number(productFilterSubcategoryId),
    );
  }, [products, productFilterSubcategoryId]);

  const loadAll = async () => {
    const [c, s, p] = await Promise.all([
      getCategories(),
      getAllSubcategories(),
      getProducts(),
    ]);

    setCategories(c);
    setSubcategories(s);
    setProducts(p);
  };

  useEffect(() => {
    loadAll();
  }, []);

  useEffect(() => {
    localStorage.setItem(
      "catalog_product_filter_subcategory_id",
      productFilterSubcategoryId,
    );
  }, [productFilterSubcategoryId]);

  const onCreateCategory = async (e) => {
    e.preventDefault();
    if (!categoryName.trim()) return;

    await createCategory({ name: categoryName.trim() });
    setCategoryName("");
    await loadAll();
  };

  const onRenameCategory = async (item) => {
    const name = window.prompt("Новое имя категории", item.name);
    if (!name || name === item.name) return;

    await updateCategory(item.id, { name });
    await loadAll();
  };

  const onCreateSubcategory = async (e) => {
    e.preventDefault();
    if (!subcategoryName.trim() || !subcategoryCategoryId) return;

    await createSubcategory({
      name: subcategoryName.trim(),
      category_id: Number(subcategoryCategoryId),
      image_url: subcategoryImageUrl.trim() || null,
    });
    setSubcategoryName("");
    setSubcategoryImageUrl("");
    await loadAll();
  };

  const onRenameSubcategory = async (item) => {
    const name = window.prompt("Новое имя подкатегории", item.name);
    if (!name || name === item.name) return;

    await updateSubcategory(item.id, { name });
    await loadAll();
  };

  const onEditSubcategoryImage = async (item) => {
    const image_url = window.prompt("Ссылка на фото", item.image_url ?? "") ?? item.image_url;
    await updateSubcategory(item.id, { image_url });
    await loadAll();
  };

  const onUploadSubcategoryImage = async (item, image_url) => {
    await updateSubcategory(item.id, { image_url: image_url || null });
    await loadAll();
  };

  const onCreateProduct = async (e) => {
    e.preventDefault();
    if (!productForm.name.trim() || !productForm.subcategory_id) return;

    await createProduct({
      name: productForm.name.trim(),
      description: productForm.description.trim() || null,
      subcategory_id: Number(productForm.subcategory_id),
      image_file_id: productForm.image_file_id.trim() || null,
    });

    setProductForm({
      name: "",
      description: "",
      subcategory_id: "",
      image_file_id: "",
    });
    await loadAll();
  };

  const onEditProduct = async (item) => {
    const name = window.prompt("Название", item.name) ?? item.name;
    const description =
      window.prompt("Описание", item.description ?? "") ?? item.description;

    await updateProduct(item.id, { name, description });
    await loadAll();
  };

  const onUploadProductImage = async (item, image_file_id) => {
    await updateProduct(item.id, { image_file_id: image_file_id || null });
    await loadAll();
  };

  return (
    <section>
      <h2 className="page-title">Каталог</h2>

      <div className="panel-grid">
        <article className="card">
          <h3>Категории</h3>
          <form className="inline-form" onSubmit={onCreateCategory}>
            <input
              value={categoryName}
              onChange={(e) => setCategoryName(e.target.value)}
              placeholder="Новая категория"
            />
            <button type="submit">Добавить</button>
          </form>

          <table className="table">
            <tbody>
              {categories.map((item) => (
                <tr key={item.id}>
                  <td>{item.name}</td>
                  <td className="actions">
                    <button onClick={() => onRenameCategory(item)}>Изменить</button>
                    <button onClick={() => deleteCategory(item.id).then(loadAll)}>
                      Удалить
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>

        <article className="card">
          <h3>Подкатегории</h3>
          <form className="stack-form" onSubmit={onCreateSubcategory}>
            <input
              value={subcategoryName}
              onChange={(e) => setSubcategoryName(e.target.value)}
              placeholder="Новая подкатегория"
            />
            <select
              value={subcategoryCategoryId}
              onChange={(e) => setSubcategoryCategoryId(e.target.value)}
            >
              <option value="">Выберите категорию</option>
              {categories.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
            <input
              placeholder="URL фото подкатегории"
              value={subcategoryImageUrl}
              onChange={(e) => setSubcategoryImageUrl(e.target.value)}
            />
            <UploadField
              label="Загрузить фото подкатегории"
              onUploaded={(url) => setSubcategoryImageUrl(url || "")}
            />
            {canPreview(subcategoryImageUrl) && (
              <img
                src={buildMediaUrl(subcategoryImageUrl)}
                alt="Предпросмотр"
                style={{ width: 160, border: "1px solid #111" }}
              />
            )}
            <button type="submit">Добавить</button>
          </form>

          <table className="table">
            <tbody>
              {subcategories.map((item) => (
                <tr key={item.id}>
                  <td>
                    {item.image_url ? (
                      <img
                        src={buildMediaUrl(item.image_url)}
                        alt={item.name}
                        style={{ width: 72, height: 72, objectFit: "cover", border: "1px solid #111" }}
                      />
                    ) : (
                      "-"
                    )}
                  </td>
                  <td>{item.name}</td>
                  <td className="muted">{categoryMap.get(item.category_id) ?? "-"}</td>
                  <td className="actions">
                    <button onClick={() => onRenameSubcategory(item)}>Имя</button>
                    <UploadField
                      compact
                      label="Загрузить фото"
                      onUploaded={(url) => onUploadSubcategoryImage(item, url)}
                    />
                    <button onClick={() => onEditSubcategoryImage(item)}>URL</button>
                    <button onClick={() => deleteSubcategory(item.id).then(loadAll)}>
                      Удалить
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
      </div>

      <article className="card">
        <h3>Товары</h3>
        <div className="inline-form">
          <span className="muted">Показано: {filteredProducts.length} из {products.length}</span>
          <select
            value={productFilterSubcategoryId}
            onChange={(e) => setProductFilterSubcategoryId(e.target.value)}
          >
            <option value="">Все подкатегории</option>
            {subcategories.map((item) => (
              <option key={item.id} value={item.id}>
                {categoryMap.get(item.category_id) ?? "-"} / {item.name}
              </option>
            ))}
          </select>
          <button type="button" onClick={() => setProductFilterSubcategoryId("")}>
            Сбросить фильтр
          </button>
        </div>
        <form className="stack-form" onSubmit={onCreateProduct}>
          <input
            placeholder="Название"
            value={productForm.name}
            onChange={(e) =>
              setProductForm((prev) => ({ ...prev, name: e.target.value }))
            }
          />
          <textarea
            placeholder="Описание"
            value={productForm.description}
            onChange={(e) =>
              setProductForm((prev) => ({ ...prev, description: e.target.value }))
            }
            rows={3}
          />
          <input
            placeholder="image_file_id или URL"
            value={productForm.image_file_id}
            onChange={(e) =>
              setProductForm((prev) => ({ ...prev, image_file_id: e.target.value }))
            }
          />
          <UploadField
            onUploaded={(url) =>
              setProductForm((prev) => ({ ...prev, image_file_id: url || "" }))
            }
          />
          {canPreview(productForm.image_file_id) && (
            <img
              src={buildMediaUrl(productForm.image_file_id)}
              alt="Предпросмотр"
              style={{ width: 160, border: "1px solid #111" }}
            />
          )}
          <select
            value={productForm.subcategory_id}
            onChange={(e) =>
              setProductForm((prev) => ({ ...prev, subcategory_id: e.target.value }))
            }
          >
            <option value="">Выберите подкатегорию</option>
            {subcategories.map((item) => (
              <option key={item.id} value={item.id}>
                {categoryMap.get(item.category_id) ?? "-"} / {item.name}
              </option>
            ))}
          </select>
          <button type="submit">Добавить товар</button>
        </form>

        <table className="table">
          <thead>
            <tr>
              <th>Фото</th>
              <th>Название</th>
              <th>Подкатегория</th>
              <th>Описание</th>
              <th>image_file_id</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {filteredProducts.map((item) => {
              const sub = subcategories.find((s) => s.id === item.subcategory_id);
              const catName = sub ? categoryMap.get(sub.category_id) : "-";
              return (
                <tr key={item.id}>
                  <td>
                    {canPreview(item.image_file_id) ? (
                      <img
                        src={buildMediaUrl(item.image_file_id)}
                        alt={item.name}
                        style={{ width: 72, height: 72, objectFit: "cover", border: "1px solid #111" }}
                      />
                    ) : (
                      "-"
                    )}
                  </td>
                  <td>{item.name}</td>
                  <td>
                    {catName} / {sub?.name ?? "-"}
                  </td>
                  <td>{item.description || "-"}</td>
                  <td>{item.image_file_id || "-"}</td>
                  <td className="actions">
                    <button onClick={() => onEditProduct(item)}>Изменить</button>
                    <UploadField
                      compact
                      label="Загрузить фото"
                      onUploaded={(url) => onUploadProductImage(item, url)}
                    />
                    <button onClick={() => deleteProduct(item.id).then(loadAll)}>
                      Удалить
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </article>
    </section>
  );
}





