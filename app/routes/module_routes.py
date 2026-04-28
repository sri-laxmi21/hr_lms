from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.module_m import Module
from app.models.menu_m import Menu
from app.schema.module_schema import ModuleWithMenus
from app.schema.menu_schema import MenuTreeResponse
from app.dependencies import get_current_user
from app.models.user_m import User
from app.models.role_right_m import RoleRight

router = APIRouter(prefix="/modules", tags=["Modules"])

@router.get("/{module_id}", response_model=ModuleWithMenus)
def get_module_with_menus(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Fetch Module
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # 2. Get accessible menu IDs for current user
    accessible_menu_ids = (
        db.query(RoleRight.menu_id)
        .filter(
            RoleRight.role_id == current_user.role_id,
            RoleRight.can_view == True
        )
        .all()
    )
    menu_ids = [m[0] for m in accessible_menu_ids]

    # 3. Fetch menus for this module that user has access to
    module_menus = (
        db.query(Menu)
        .filter(
            Menu.module_id == module.id,
            Menu.id.in_(menu_ids),
            Menu.is_active == True
        )
        .order_by(Menu.menu_order)
        .all()
    )

    # 4. Build Tree
    menu_dict = {menu.id: MenuTreeResponse.from_orm(menu) for menu in module_menus}
    
    for menu_id, menu_data in menu_dict.items():
        menu_data.children = [
            child for child in menu_dict.values() 
            if child.parent_id == menu_id
        ]
    
    # Root menus for this module
    tree = [menu for menu in menu_dict.values() if menu.parent_id is None]

    # 5. Construct Response
    module_resp = ModuleWithMenus.from_orm(module)
    module_resp.menus = tree
    
    return module_resp
