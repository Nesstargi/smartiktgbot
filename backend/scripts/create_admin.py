from backend.database import SessionLocal
from backend.models.user import User
from backend.models.role import Role
from backend.models.user_role import UserRole
from backend.models.user_permission import UserPermission
from backend.core.security import hash_password
from backend.core.deps import ALL_PERMISSIONS

email = "egor.sadovodovv@gmail.com"
password = "tujh1996A"

db = SessionLocal()

user = User(email=email, hashed_password=hash_password(password), is_active=True)
db.add(user)
db.commit()
db.refresh(user)

admin_role = db.query(Role).filter(Role.name == "admin").first() or Role(name="admin")
super_role = db.query(Role).filter(Role.name == "super_admin").first() or Role(
    name="super_admin"
)

db.add(admin_role)
db.add(super_role)
db.commit()

db.add(UserRole(user_id=user.id, role_id=admin_role.id))
db.add(UserRole(user_id=user.id, role_id=super_role.id))

for perm in ALL_PERMISSIONS:
    db.add(UserPermission(user_id=user.id, permission=perm))

db.commit()

print("Super admin created:", email)
