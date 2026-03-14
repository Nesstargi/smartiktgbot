import { useEffect, useMemo, useState } from "react";

import { getApiErrorMessage } from "../api/axios";
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

const CATEGORY_PAGE_SIZE = 8;
const SUBCATEGORY_PAGE_SIZE = 8;
const PRODUCT_PAGE_SIZE = 10;

function canPreview(value) {
  return !!value && (value.startsWith("/") || value.startsWith("http"));
}

function getResultsLabel(itemsLength, total, page, pageSize) {
  if (total === 0 || itemsLength === 0) return "Ничего не найдено";

  const start = page * pageSize + 1;
  const end = page * pageSize + itemsLength;
  return `Показано ${start}-${end} из ${total}`;
}

export default function CatalogPage() {
  const [categoryOptions, setCategoryOptions] = useState([]);
  const [subcategoryOptions, setSubcategoryOptions] = useState([]);
  const [optionsError, setOptionsError] = useState("");

  const [categories, setCategories] = useState([]);
  const [categoriesTotal, setCategoriesTotal] = useState(0);
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [categoryError, setCategoryError] = useState("");
  const [categoryName, setCategoryName] = useState("");
  const [categorySearchInput, setCategorySearchInput] = useState("");
  const [categorySearchQuery, setCategorySearchQuery] = useState("");
  const [categoryPage, setCategoryPage] = useState(0);

  const [subcategories, setSubcategories] = useState([]);
  const [subcategoriesTotal, setSubcategoriesTotal] = useState(0);
  const [subcategoriesLoading, setSubcategoriesLoading] = useState(true);
  const [subcategoryError, setSubcategoryError] = useState("");
  const [subcategoryName, setSubcategoryName] = useState("");
  const [subcategoryCategoryId, setSubcategoryCategoryId] = useState("");
  const [subcategoryImageUrl, setSubcategoryImageUrl] = useState("");
  const [subcategorySearchInput, setSubcategorySearchInput] = useState("");
  const [subcategorySearchQuery, setSubcategorySearchQuery] = useState("");
  const [subcategoryFilterCategoryId, setSubcategoryFilterCategoryId] = useState("");
  const [subcategoryPage, setSubcategoryPage] = useState(0);

  const [products, setProducts] = useState([]);
  const [productsTotal, setProductsTotal] = useState(0);
  const [productsLoading, setProductsLoading] = useState(true);
  const [productError, setProductError] = useState("");
  const [productForm, setProductForm] = useState({
    name: "",
    description: "",
    subcategory_id: "",
    image_file_id: "",
  });
  const [productSearchInput, setProductSearchInput] = useState("");
  const [productSearchQuery, setProductSearchQuery] = useState("");
  const [productFilterSubcategoryId, setProductFilterSubcategoryId] = useState(
    () => localStorage.getItem("catalog_product_filter_subcategory_id") || "",
  );
  const [productPage, setProductPage] = useState(0);

  const [catalogReload, setCatalogReload] = useState(0);

  const categoryMap = useMemo(
    () => new Map(categoryOptions.map((item) => [item.id, item.name])),
    [categoryOptions],
  );
  const subcategoryMap = useMemo(
    () => new Map(subcategoryOptions.map((item) => [item.id, item])),
    [subcategoryOptions],
  );

  const categoryResultsLabel = useMemo(
    () => getResultsLabel(categories.length, categoriesTotal, categoryPage, CATEGORY_PAGE_SIZE),
    [categories.length, categoriesTotal, categoryPage],
  );
  const subcategoryResultsLabel = useMemo(
    () => getResultsLabel(
      subcategories.length,
      subcategoriesTotal,
      subcategoryPage,
      SUBCATEGORY_PAGE_SIZE,
    ),
    [subcategories.length, subcategoriesTotal, subcategoryPage],
  );
  const productResultsLabel = useMemo(
    () => getResultsLabel(products.length, productsTotal, productPage, PRODUCT_PAGE_SIZE),
    [products.length, productsTotal, productPage],
  );

  useEffect(() => {
    localStorage.setItem(
      "catalog_product_filter_subcategory_id",
      productFilterSubcategoryId,
    );
  }, [productFilterSubcategoryId]);

  useEffect(() => {
    let cancelled = false;

    async function loadReferenceData() {
      setOptionsError("");
      try {
        const [categoriesResult, subcategoriesResult] = await Promise.all([
          getCategories(),
          getAllSubcategories(),
        ]);

        if (!cancelled) {
          setCategoryOptions(categoriesResult.items || []);
          setSubcategoryOptions(subcategoriesResult.items || []);
        }
      } catch (error) {
        if (!cancelled) {
          setOptionsError(getApiErrorMessage(error, "Не удалось загрузить справочные данные каталога"));
        }
      }
    }

    loadReferenceData();
    return () => {
      cancelled = true;
    };
  }, [catalogReload]);

  useEffect(() => {
    if (
      subcategoryCategoryId
      && !categoryOptions.some((item) => item.id === Number(subcategoryCategoryId))
    ) {
      setSubcategoryCategoryId("");
    }

    if (
      subcategoryFilterCategoryId
      && !categoryOptions.some((item) => item.id === Number(subcategoryFilterCategoryId))
    ) {
      setSubcategoryFilterCategoryId("");
    }

    if (
      productForm.subcategory_id
      && !subcategoryOptions.some((item) => item.id === Number(productForm.subcategory_id))
    ) {
      setProductForm((prev) => ({ ...prev, subcategory_id: "" }));
    }

    if (
      productFilterSubcategoryId
      && !subcategoryOptions.some((item) => item.id === Number(productFilterSubcategoryId))
    ) {
      setProductFilterSubcategoryId("");
    }
  }, [
    categoryOptions,
    productFilterSubcategoryId,
    productForm.subcategory_id,
    subcategoryCategoryId,
    subcategoryFilterCategoryId,
    subcategoryOptions,
  ]);

  useEffect(() => {
    let cancelled = false;

    async function loadCategories() {
      setCategoriesLoading(true);
      setCategoryError("");
      try {
        const result = await getCategories({
          q: categorySearchQuery || undefined,
          limit: CATEGORY_PAGE_SIZE,
          offset: categoryPage * CATEGORY_PAGE_SIZE,
        });

        if (!cancelled) {
          setCategories(result.items || []);
          setCategoriesTotal(result.total || 0);
        }
      } catch (error) {
        if (!cancelled) {
          setCategories([]);
          setCategoriesTotal(0);
          setCategoryError(getApiErrorMessage(error, "Не удалось загрузить категории"));
        }
      } finally {
        if (!cancelled) {
          setCategoriesLoading(false);
        }
      }
    }

    loadCategories();
    return () => {
      cancelled = true;
    };
  }, [catalogReload, categoryPage, categorySearchQuery]);

  useEffect(() => {
    let cancelled = false;

    async function loadSubcategories() {
      setSubcategoriesLoading(true);
      setSubcategoryError("");
      try {
        const result = await getAllSubcategories({
          q: subcategorySearchQuery || undefined,
          category_id: subcategoryFilterCategoryId || undefined,
          limit: SUBCATEGORY_PAGE_SIZE,
          offset: subcategoryPage * SUBCATEGORY_PAGE_SIZE,
        });

        if (!cancelled) {
          setSubcategories(result.items || []);
          setSubcategoriesTotal(result.total || 0);
        }
      } catch (error) {
        if (!cancelled) {
          setSubcategories([]);
          setSubcategoriesTotal(0);
          setSubcategoryError(getApiErrorMessage(error, "Не удалось загрузить подкатегории"));
        }
      } finally {
        if (!cancelled) {
          setSubcategoriesLoading(false);
        }
      }
    }

    loadSubcategories();
    return () => {
      cancelled = true;
    };
  }, [catalogReload, subcategoryFilterCategoryId, subcategoryPage, subcategorySearchQuery]);

  useEffect(() => {
    let cancelled = false;

    async function loadProducts() {
      setProductsLoading(true);
      setProductError("");
      try {
        const result = await getProducts({
          q: productSearchQuery || undefined,
          subcategory_id: productFilterSubcategoryId || undefined,
          limit: PRODUCT_PAGE_SIZE,
          offset: productPage * PRODUCT_PAGE_SIZE,
        });

        if (!cancelled) {
          setProducts(result.items || []);
          setProductsTotal(result.total || 0);
        }
      } catch (error) {
        if (!cancelled) {
          setProducts([]);
          setProductsTotal(0);
          setProductError(getApiErrorMessage(error, "Не удалось загрузить товары"));
        }
      } finally {
        if (!cancelled) {
          setProductsLoading(false);
        }
      }
    }

    loadProducts();
    return () => {
      cancelled = true;
    };
  }, [catalogReload, productFilterSubcategoryId, productPage, productSearchQuery]);

  const refreshCatalog = () => {
    setCatalogReload((prev) => prev + 1);
  };

  const onCategorySearchSubmit = (e) => {
    e.preventDefault();
    setCategoryPage(0);
    setCategorySearchQuery(categorySearchInput.trim());
  };

  const onClearCategorySearch = () => {
    setCategorySearchInput("");
    setCategorySearchQuery("");
    setCategoryPage(0);
  };

  const onSubcategorySearchSubmit = (e) => {
    e.preventDefault();
    setSubcategoryPage(0);
    setSubcategorySearchQuery(subcategorySearchInput.trim());
  };

  const onClearSubcategoryFilters = () => {
    setSubcategorySearchInput("");
    setSubcategorySearchQuery("");
    setSubcategoryFilterCategoryId("");
    setSubcategoryPage(0);
  };

  const onProductSearchSubmit = (e) => {
    e.preventDefault();
    setProductPage(0);
    setProductSearchQuery(productSearchInput.trim());
  };

  const onClearProductFilters = () => {
    setProductSearchInput("");
    setProductSearchQuery("");
    setProductFilterSubcategoryId("");
    setProductPage(0);
  };

  const onCreateCategory = async (e) => {
    e.preventDefault();
    if (!categoryName.trim()) return;

    setCategoryError("");
    try {
      await createCategory({ name: categoryName.trim() });
      setCategoryName("");
      setCategoryPage(0);
      refreshCatalog();
    } catch (error) {
      setCategoryError(getApiErrorMessage(error, "Не удалось создать категорию"));
    }
  };

  const onRenameCategory = async (item) => {
    const name = window.prompt("Новое имя категории", item.name);
    if (!name || name === item.name) return;

    setCategoryError("");
    try {
      await updateCategory(item.id, { name });
      refreshCatalog();
    } catch (error) {
      setCategoryError(getApiErrorMessage(error, "Не удалось обновить категорию"));
    }
  };

  const onDeleteCategory = async (item) => {
    if (!window.confirm(`Удалить категорию "${item.name}"?`)) return;

    setCategoryError("");
    try {
      await deleteCategory(item.id);
      if (categories.length === 1 && categoryPage > 0) {
        setCategoryPage((prev) => prev - 1);
      }
      refreshCatalog();
    } catch (error) {
      setCategoryError(getApiErrorMessage(error, "Не удалось удалить категорию"));
    }
  };

  const onCreateSubcategory = async (e) => {
    e.preventDefault();
    if (!subcategoryName.trim() || !subcategoryCategoryId) return;

    setSubcategoryError("");
    try {
      await createSubcategory({
        name: subcategoryName.trim(),
        category_id: Number(subcategoryCategoryId),
        image_url: subcategoryImageUrl.trim() || null,
      });
      setSubcategoryName("");
      setSubcategoryImageUrl("");
      setSubcategoryPage(0);
      refreshCatalog();
    } catch (error) {
      setSubcategoryError(getApiErrorMessage(error, "Не удалось создать подкатегорию"));
    }
  };

  const onRenameSubcategory = async (item) => {
    const name = window.prompt("Новое имя подкатегории", item.name);
    if (!name || name === item.name) return;

    setSubcategoryError("");
    try {
      await updateSubcategory(item.id, { name });
      refreshCatalog();
    } catch (error) {
      setSubcategoryError(getApiErrorMessage(error, "Не удалось обновить подкатегорию"));
    }
  };

  const onEditSubcategoryImage = async (item) => {
    const imageUrl = window.prompt("Ссылка на фото", item.image_url ?? "") ?? item.image_url;

    setSubcategoryError("");
    try {
      await updateSubcategory(item.id, { image_url: imageUrl });
      refreshCatalog();
    } catch (error) {
      setSubcategoryError(getApiErrorMessage(error, "Не удалось обновить изображение"));
    }
  };

  const onUploadSubcategoryImage = async (item, imageUrl) => {
    setSubcategoryError("");
    try {
      await updateSubcategory(item.id, { image_url: imageUrl || null });
      refreshCatalog();
    } catch (error) {
      setSubcategoryError(getApiErrorMessage(error, "Не удалось обновить изображение"));
    }
  };

  const onDeleteSubcategory = async (item) => {
    if (!window.confirm(`Удалить подкатегорию "${item.name}"?`)) return;

    setSubcategoryError("");
    try {
      await deleteSubcategory(item.id);
      if (subcategories.length === 1 && subcategoryPage > 0) {
        setSubcategoryPage((prev) => prev - 1);
      }
      refreshCatalog();
    } catch (error) {
      setSubcategoryError(getApiErrorMessage(error, "Не удалось удалить подкатегорию"));
    }
  };

  const onCreateProduct = async (e) => {
    e.preventDefault();
    if (!productForm.name.trim() || !productForm.subcategory_id) return;

    setProductError("");
    try {
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
      setProductPage(0);
      refreshCatalog();
    } catch (error) {
      setProductError(getApiErrorMessage(error, "Не удалось создать товар"));
    }
  };

  const onEditProduct = async (item) => {
    const name = window.prompt("Название", item.name) ?? item.name;
    const description =
      window.prompt("Описание", item.description ?? "") ?? item.description;

    setProductError("");
    try {
      await updateProduct(item.id, { name, description });
      refreshCatalog();
    } catch (error) {
      setProductError(getApiErrorMessage(error, "Не удалось обновить товар"));
    }
  };

  const onUploadProductImage = async (item, imageFileId) => {
    setProductError("");
    try {
      await updateProduct(item.id, { image_file_id: imageFileId || null });
      refreshCatalog();
    } catch (error) {
      setProductError(getApiErrorMessage(error, "Не удалось обновить изображение товара"));
    }
  };

  const onDeleteProduct = async (item) => {
    if (!window.confirm(`Удалить товар "${item.name}"?`)) return;

    setProductError("");
    try {
      await deleteProduct(item.id);
      if (products.length === 1 && productPage > 0) {
        setProductPage((prev) => prev - 1);
      }
      refreshCatalog();
    } catch (error) {
      setProductError(getApiErrorMessage(error, "Не удалось удалить товар"));
    }
  };

  return (
    <section>
      <h2 className="page-title">Каталог</h2>
      {optionsError && <p className="error-text">{optionsError}</p>}

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

          <div className="list-toolbar">
            <form className="inline-form" onSubmit={onCategorySearchSubmit}>
              <input
                value={categorySearchInput}
                onChange={(e) => setCategorySearchInput(e.target.value)}
                placeholder="Поиск категории"
              />
              <button type="submit">Найти</button>
              <button
                type="button"
                onClick={onClearCategorySearch}
                disabled={!categorySearchInput && !categorySearchQuery}
              >
                Сбросить
              </button>
            </form>
            <p className="muted">{categoriesLoading ? "Загрузка..." : categoryResultsLabel}</p>
          </div>

          {categoryError && <p className="error-text">{categoryError}</p>}

          {categoriesLoading ? (
            <p className="muted">Загрузка...</p>
          ) : categories.length === 0 ? (
            <p className="muted">Категории не найдены.</p>
          ) : (
            <div className="table-wrap">
              <table className="table table-compact">
                <tbody>
                  {categories.map((item) => (
                    <tr key={item.id}>
                      <td data-label="Категория">{item.name}</td>
                      <td className="actions" data-label="Действия">
                        <button onClick={() => onRenameCategory(item)}>Изменить</button>
                        <button onClick={() => onDeleteCategory(item)}>Удалить</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="pagination-controls">
            <button
              type="button"
              onClick={() => setCategoryPage((prev) => prev - 1)}
              disabled={categoryPage === 0}
            >
              Назад
            </button>
            <span className="muted">Страница {categoryPage + 1}</span>
            <button
              type="button"
              onClick={() => setCategoryPage((prev) => prev + 1)}
              disabled={(categoryPage + 1) * CATEGORY_PAGE_SIZE >= categoriesTotal}
            >
              Вперёд
            </button>
          </div>
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
              disabled={categoryOptions.length === 0}
            >
              <option value="">Выберите категорию</option>
              {categoryOptions.map((item) => (
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
                decoding="async"
                width={160}
                style={{ width: 160, border: "1px solid #111" }}
              />
            )}
            <button type="submit">Добавить</button>
          </form>

          <div className="list-toolbar">
            <form className="inline-form" onSubmit={onSubcategorySearchSubmit}>
              <input
                value={subcategorySearchInput}
                onChange={(e) => setSubcategorySearchInput(e.target.value)}
                placeholder="Поиск подкатегории"
              />
              <button type="submit">Найти</button>
            </form>

            <div className="inline-form">
              <select
                value={subcategoryFilterCategoryId}
                onChange={(e) => {
                  setSubcategoryFilterCategoryId(e.target.value);
                  setSubcategoryPage(0);
                }}
              >
                <option value="">Все категории</option>
                {categoryOptions.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={onClearSubcategoryFilters}
                disabled={!subcategorySearchInput && !subcategorySearchQuery && !subcategoryFilterCategoryId}
              >
                Сбросить
              </button>
            </div>
          </div>

          <p className="muted">{subcategoriesLoading ? "Загрузка..." : subcategoryResultsLabel}</p>
          {subcategoryError && <p className="error-text">{subcategoryError}</p>}

          {subcategoriesLoading ? (
            <p className="muted">Загрузка...</p>
          ) : subcategories.length === 0 ? (
            <p className="muted">Подкатегории не найдены.</p>
          ) : (
            <div className="table-wrap">
              <table className="table table-compact">
                <tbody>
                  {subcategories.map((item) => (
                    <tr key={item.id}>
                      <td data-label="Фото">
                        {item.image_url ? (
                          <img
                            src={buildMediaUrl(item.image_url)}
                            alt={item.name}
                            loading="lazy"
                            decoding="async"
                            width={72}
                            height={72}
                            style={{
                              width: 72,
                              height: 72,
                              objectFit: "cover",
                              border: "1px solid #111",
                            }}
                          />
                        ) : (
                          "-"
                        )}
                      </td>
                      <td data-label="Название">{item.name}</td>
                      <td className="muted" data-label="Категория">
                        {categoryMap.get(item.category_id) ?? "-"}
                      </td>
                      <td className="actions" data-label="Действия">
                        <button onClick={() => onRenameSubcategory(item)}>Имя</button>
                        <UploadField
                          compact
                          label="Загрузить фото"
                          onUploaded={(url) => onUploadSubcategoryImage(item, url)}
                        />
                        <button onClick={() => onEditSubcategoryImage(item)}>URL</button>
                        <button onClick={() => onDeleteSubcategory(item)}>Удалить</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="pagination-controls">
            <button
              type="button"
              onClick={() => setSubcategoryPage((prev) => prev - 1)}
              disabled={subcategoryPage === 0}
            >
              Назад
            </button>
            <span className="muted">Страница {subcategoryPage + 1}</span>
            <button
              type="button"
              onClick={() => setSubcategoryPage((prev) => prev + 1)}
              disabled={(subcategoryPage + 1) * SUBCATEGORY_PAGE_SIZE >= subcategoriesTotal}
            >
              Вперёд
            </button>
          </div>
        </article>
      </div>

      <article className="card">
        <h3>Товары</h3>

        <div className="list-toolbar">
          <form className="inline-form" onSubmit={onProductSearchSubmit}>
            <input
              placeholder="Поиск по названию или описанию"
              value={productSearchInput}
              onChange={(e) => setProductSearchInput(e.target.value)}
            />
            <button type="submit">Найти</button>
          </form>

          <div className="inline-form">
            <select
              value={productFilterSubcategoryId}
              onChange={(e) => {
                setProductFilterSubcategoryId(e.target.value);
                setProductPage(0);
              }}
            >
              <option value="">Все подкатегории</option>
              {subcategoryOptions.map((item) => (
                <option key={item.id} value={item.id}>
                  {categoryMap.get(item.category_id) ?? "-"} / {item.name}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={onClearProductFilters}
              disabled={!productSearchInput && !productSearchQuery && !productFilterSubcategoryId}
            >
              Сбросить
            </button>
          </div>
        </div>

        <p className="muted">{productsLoading ? "Загрузка..." : productResultsLabel}</p>

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
              decoding="async"
              width={160}
              style={{ width: 160, border: "1px solid #111" }}
            />
          )}
          <select
            value={productForm.subcategory_id}
            onChange={(e) =>
              setProductForm((prev) => ({ ...prev, subcategory_id: e.target.value }))
            }
            disabled={subcategoryOptions.length === 0}
          >
            <option value="">Выберите подкатегорию</option>
            {subcategoryOptions.map((item) => (
              <option key={item.id} value={item.id}>
                {categoryMap.get(item.category_id) ?? "-"} / {item.name}
              </option>
            ))}
          </select>
          <button type="submit">Добавить товар</button>
        </form>

        {productError && <p className="error-text">{productError}</p>}

        {productsLoading ? (
          <p className="muted">Загрузка...</p>
        ) : products.length === 0 ? (
          <p className="muted">Товары не найдены.</p>
        ) : (
          <div className="table-wrap">
            <table className="table table-compact">
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
                {products.map((item) => {
                  const subcategory = subcategoryMap.get(item.subcategory_id);
                  const categoryNameForItem = subcategory
                    ? categoryMap.get(subcategory.category_id)
                    : "-";

                  return (
                    <tr key={item.id}>
                      <td data-label="Фото">
                        {canPreview(item.image_file_id) ? (
                          <img
                            src={buildMediaUrl(item.image_file_id)}
                            alt={item.name}
                            loading="lazy"
                            decoding="async"
                            width={72}
                            height={72}
                            style={{
                              width: 72,
                              height: 72,
                              objectFit: "cover",
                              border: "1px solid #111",
                            }}
                          />
                        ) : (
                          "-"
                        )}
                      </td>
                      <td data-label="Название">{item.name}</td>
                      <td data-label="Подкатегория">
                        {categoryNameForItem} / {subcategory?.name ?? "-"}
                      </td>
                      <td data-label="Описание">{item.description || "-"}</td>
                      <td data-label="image_file_id">{item.image_file_id || "-"}</td>
                      <td className="actions" data-label="Действия">
                        <button onClick={() => onEditProduct(item)}>Изменить</button>
                        <UploadField
                          compact
                          label="Загрузить фото"
                          onUploaded={(url) => onUploadProductImage(item, url)}
                        />
                        <button onClick={() => onDeleteProduct(item)}>Удалить</button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        <div className="pagination-controls">
          <button
            type="button"
            onClick={() => setProductPage((prev) => prev - 1)}
            disabled={productPage === 0}
          >
            Назад
          </button>
          <span className="muted">Страница {productPage + 1}</span>
          <button
            type="button"
            onClick={() => setProductPage((prev) => prev + 1)}
            disabled={(productPage + 1) * PRODUCT_PAGE_SIZE >= productsTotal}
          >
            Вперёд
          </button>
        </div>
      </article>
    </section>
  );
}
