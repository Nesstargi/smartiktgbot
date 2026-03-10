import { useEffect, useState } from "react";
import { getProducts, createProduct, deleteProduct } from "../api/products.api";
import { getCategories } from "../api/categories.api";
import ProductTable from "../components/ProductTable";
import ProductForm from "../components/ProductForm";

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const loadAll = async () => {
    const [p, c] = await Promise.all([
      getProducts(),
      getCategories(),
    ]);
    setProducts(p);
    setCategories(c);
  };

  useEffect(() => {
    loadAll();
  }, []);

  const handleCreate = async (data) => {
    await createProduct(data);
    setShowForm(false);
    loadAll();
  };

  const handleDelete = async (id) => {
    await deleteProduct(id);
    loadAll();
  };

  return (
    <div>
      <h2>Товары</h2>

      <button onClick={() => setShowForm(!showForm)}>
        + Добавить товар
      </button>

      {showForm && (
        <ProductForm
          categories={categories}
          onSubmit={handleCreate}
        />
      )}

      <ProductTable
        products={products}
        onDelete={handleDelete}
      />
    </div>
  );
}
