import { useEffect, useState } from "react";

import { getCategories } from "../api/categories.api";
import { createProduct, deleteProduct, getProducts } from "../api/products.api";
import ProductForm from "../components/ProductForm";
import ProductTable from "../components/ProductTable";

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadAll() {
      const [productsResult, categoriesResult] = await Promise.all([
        getProducts(),
        getCategories(),
      ]);

      if (!cancelled) {
        setProducts(productsResult.items || []);
        setCategories(categoriesResult.items || []);
      }
    }

    loadAll();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleCreate = async (data) => {
    await createProduct(data);
    setShowForm(false);

    const productsResult = await getProducts();
    setProducts(productsResult.items || []);
  };

  const handleDelete = async (id) => {
    await deleteProduct(id);
    const productsResult = await getProducts();
    setProducts(productsResult.items || []);
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
