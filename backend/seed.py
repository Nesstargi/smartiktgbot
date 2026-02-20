from backend.database import SessionLocal, engine
from backend.models import Category, SubCategory, Product, Base

FILE_ID = (
    "AgACAgIAAxkBAAOKaZh0XQI3oEY21r1vJLeKsO3C9goAAjMXaxsLr8BItaq_BIQ8QA0BAAMCAAN4AAM6BA"
)

# пересоздание таблиц (ОСТОРОЖНО: удаляет данные)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# =========================
# КАТЕГОРИИ
# =========================
cat1 = Category(name="Смартфоны")
cat2 = Category(name="Ноутбуки")
cat3 = Category(name="Бытовая техника")

db.add_all([cat1, cat2, cat3])
db.commit()

# =========================
# ПОДКАТЕГОРИИ
# =========================
# Смартфоны
sub1 = SubCategory(name="Android", category_id=cat1.id)
sub2 = SubCategory(name="iPhone", category_id=cat1.id)

# Ноутбуки
sub3 = SubCategory(name="Для работы", category_id=cat2.id)
sub4 = SubCategory(name="Игровые", category_id=cat2.id)

# Бытовая техника
sub5 = SubCategory(name="Кухня", category_id=cat3.id)
sub6 = SubCategory(name="Дом", category_id=cat3.id)

db.add_all([sub1, sub2, sub3, sub4, sub5, sub6])
db.commit()

# =========================
# ТОВАРЫ
# =========================

products = [
    # ---------- Android ----------
    Product(
        name="Xiaomi Redmi 12",
        description="6.8'' | 128GB | 5000mAh",
        subcategory_id=sub1.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Samsung Galaxy A15",
        description="6.6'' | 128GB | AMOLED",
        subcategory_id=sub1.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Realme C55",
        description="6.7'' | 64GB | NFC",
        subcategory_id=sub1.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Tecno Spark 20",
        description="6.6'' | 128GB | 5000mAh",
        subcategory_id=sub1.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Infinix Note 30",
        description="6.7'' | 256GB | FastCharge",
        subcategory_id=sub1.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Poco X5",
        description="AMOLED | 5G | Snapdragon",
        subcategory_id=sub1.id,
        image_file_id=FILE_ID,
    ),
    # ---------- iPhone ----------
    Product(
        name="iPhone 11",
        description="128GB | FaceID | iOS",
        subcategory_id=sub2.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="iPhone 12",
        description="OLED | A14 | 5G",
        subcategory_id=sub2.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="iPhone 13",
        description="A15 | Dual Camera",
        subcategory_id=sub2.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="iPhone SE 2022",
        description="Compact | TouchID",
        subcategory_id=sub2.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="iPhone 14",
        description="OLED | A16",
        subcategory_id=sub2.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="iPhone 15",
        description="USB-C | Titanium",
        subcategory_id=sub2.id,
        image_file_id=FILE_ID,
    ),
    # ---------- Для работы ----------
    Product(
        name="Lenovo ThinkBook",
        description="Intel i5 | 16GB RAM | SSD",
        subcategory_id=sub3.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="HP ProBook",
        description="Business class | SSD",
        subcategory_id=sub3.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="ASUS VivoBook",
        description="Slim | SSD | IPS",
        subcategory_id=sub3.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Acer Aspire",
        description="Intel i3 | Office",
        subcategory_id=sub3.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Dell Inspiron",
        description="Workstation | SSD",
        subcategory_id=sub3.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Huawei MateBook",
        description="Metal body | Fast зарядка",
        subcategory_id=sub3.id,
        image_file_id=FILE_ID,
    ),
    # ---------- Игровые ----------
    Product(
        name="ASUS TUF Gaming",
        description="RTX 3060 | i7 | 144Hz",
        subcategory_id=sub4.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Acer Nitro 5",
        description="RTX | Gaming design",
        subcategory_id=sub4.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="MSI Katana",
        description="RTX 3050 | RGB",
        subcategory_id=sub4.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Lenovo Legion",
        description="Gaming series | Cooling",
        subcategory_id=sub4.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="HP Omen",
        description="High performance | RTX",
        subcategory_id=sub4.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Gigabyte G5",
        description="i7 | RTX | 144Hz",
        subcategory_id=sub4.id,
        image_file_id=FILE_ID,
    ),
    # ---------- Кухня ----------
    Product(
        name="Микроволновка LG",
        description="20л | Grill | Digital",
        subcategory_id=sub5.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Холодильник Samsung",
        description="No Frost | Digital",
        subcategory_id=sub5.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Плита Bosch",
        description="Электро | Таймер",
        subcategory_id=sub5.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Чайник Xiaomi",
        description="Smart | App control",
        subcategory_id=sub5.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Кофемашина DeLonghi",
        description="Espresso | Cappuccino",
        subcategory_id=sub5.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Блендер Philips",
        description="Turbo | Steel",
        subcategory_id=sub5.id,
        image_file_id=FILE_ID,
    ),
    # ---------- Дом ----------
    Product(
        name="Пылесос Dyson",
        description="Wireless | Cyclone",
        subcategory_id=sub6.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Робот-пылесос Xiaomi",
        description="Smart | Mapping",
        subcategory_id=sub6.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Утюг Philips",
        description="Steam | Anti-scale",
        subcategory_id=sub6.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Кондиционер LG",
        description="Inverter | Smart",
        subcategory_id=sub6.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Обогреватель Ballu",
        description="Eco | Safety",
        subcategory_id=sub6.id,
        image_file_id=FILE_ID,
    ),
    Product(
        name="Очиститель воздуха Xiaomi",
        description="HEPA | Smart",
        subcategory_id=sub6.id,
        image_file_id=FILE_ID,
    ),
]

db.add_all(products)
db.commit()
db.close()

print("✅ База успешно заполнена тестовыми данными с file_id")
