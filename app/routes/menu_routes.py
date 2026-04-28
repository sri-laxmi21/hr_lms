from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.menu_m import Menu
from app.models.module_m import Module
from app.schema.menu_schema import MenuCreate, MenuUpdate, MenuResponse, MenuTreeResponse
from app.schema.module_schema import ModuleWithMenus
from app.dependencies import require_org_admin, get_current_user
from app.models.user_m import User

router = APIRouter(prefix="/menus", tags=["Menus"])

# ---------------- CREATE MENU ----------------
@router.post("/", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
def create_menu(
    payload: MenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_admin)
):
    # Check if parent exists if parent_id is provided
    if payload.parent_id:
        parent_menu = db.query(Menu).filter(Menu.id == payload.parent_id).first()
        if not parent_menu:
            raise HTTPException(status_code=404, detail="Parent menu not found")
    
    new_menu = Menu(
        name=payload.name,
        display_name=payload.display_name,
        route=payload.route,
        icon=payload.icon,
        parent_id=payload.parent_id,
        menu_order=payload.menu_order,
        is_active=payload.is_active,
        created_by=current_user.email,
        modified_by=current_user.email
    )
    
    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)
    return new_menu

# ---------------- GET ALL MENUS (FLAT) ----------------
@router.get("/", response_model=List[MenuResponse])
def get_all_menus(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    menus = db.query(Menu).order_by(Menu.menu_order).all()
    return menus

# ---------------- GET MENUS BY MODULES (Grouped) ----------------
@router.get("/by-modules", response_model=List[ModuleWithMenus])
def get_menus_by_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.role_right_m import RoleRight
    
    # 1. Get all modules
    modules = db.query(Module).all()
    
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
    
    result = []
    
    # 3. For each module, build the tree
    for module in modules:
        # Fetch menus for this module that user has access to
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
        
        # Build tree for this module
        menu_dict = {menu.id: MenuTreeResponse.from_orm(menu) for menu in module_menus}
        
        for menu_id, menu_data in menu_dict.items():
            menu_data.children = [
                child for child in menu_dict.values() 
                if child.parent_id == menu_id
            ]
        
        # Root menus for this module
        tree = [menu for menu in menu_dict.values() if menu.parent_id is None]
        
        # Create response object
        module_resp = ModuleWithMenus.from_orm(module)
        module_resp.menus = tree
        result.append(module_resp)
        
    return result

# ---------------- GET MENU TREE ----------------
@router.get("/tree", response_model=List[MenuTreeResponse])
def get_menu_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all active menus
    all_menus = db.query(Menu).filter(Menu.is_active == True).order_by(Menu.menu_order).all()
    
    # Build tree structure
    menu_dict = {menu.id: menu for menu in all_menus}
    tree = []
    
    for menu in all_menus:
        menu_data = MenuTreeResponse.from_orm(menu)
        menu_data.children = []
        
        if menu.parent_id is None:
            tree.append(menu_data)
        else:
            if menu.parent_id in menu_dict:
                parent = next((m for m in tree if m.id == menu.parent_id), None)
                if parent:
                    parent.children.append(menu_data)
    
    return tree

# ---------------- GET USER MENUS (Based on Role Rights) ----------------
@router.get("/user-menus", response_model=List[MenuTreeResponse])
def get_user_menus(
    module_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.role_right_m import RoleRight
    
    # Get menus accessible by user's role
    accessible_menu_ids = (
        db.query(RoleRight.menu_id)
        .filter(
            RoleRight.role_id == current_user.role_id,
            RoleRight.can_view == True
        )
        .all()
    )
    
    menu_ids = [menu_id[0] for menu_id in accessible_menu_ids]
    
    if not menu_ids:
        return []
    
    # Get those menus
    query = db.query(Menu).filter(Menu.id.in_(menu_ids), Menu.is_active == True)
    
    if module_id:
        query = query.filter(Menu.module_id == module_id)
        
    accessible_menus = query.order_by(Menu.menu_order).all()
    
    # Build tree
    menu_dict = {menu.id: MenuTreeResponse.from_orm(menu) for menu in accessible_menus}
    
    for menu_id, menu_data in menu_dict.items():
        menu_data.children = [
            child for child in menu_dict.values() 
            if child.parent_id == menu_id
        ]
    
    # Return root menus
    tree = [menu for menu in menu_dict.values() if menu.parent_id is None]
    return tree

# ---------------- GET MENU BY ID ----------------
@router.get("/{menu_id}", response_model=MenuResponse)
def get_menu_by_id(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu

# ---------------- UPDATE MENU ----------------
@router.put("/{menu_id}", response_model=MenuResponse)
def update_menu(
    menu_id: int,
    payload: MenuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_admin)
):
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    update_data = payload.dict(exclude_unset=True)
    
    # Check parent_id validity if being updated
    if "parent_id" in update_data and update_data["parent_id"]:
        if update_data["parent_id"] == menu_id:
            raise HTTPException(status_code=400, detail="Menu cannot be its own parent")
        parent = db.query(Menu).filter(Menu.id == update_data["parent_id"]).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent menu not found")
    
    for key, value in update_data.items():
        setattr(menu, key, value)
    
    menu.modified_by = current_user.email
    
    db.commit()
    db.refresh(menu)
    return menu

# ---------------- DELETE MENU ----------------
@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_admin)
):
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # Check if menu has children
    children = db.query(Menu).filter(Menu.parent_id == menu_id).first()
    if children:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete menu with children. Delete children first."
        )
    
    db.delete(menu)
    db.commit()
    return None