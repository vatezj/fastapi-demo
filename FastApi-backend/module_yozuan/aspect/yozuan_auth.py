"""
游赚模块权限控制装饰器
参考 module_admin 的权限控制机制，为游赚模块后台管理接口提供权限验证
"""

from fastapi import Depends, HTTPException, status
from typing import List, Union
from exceptions.exception import PermissionException
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService


class CheckYozuanInterfaceAuth:
    """
    校验当前用户是否具有游赚模块相应的接口权限
    继承 module_admin 的权限体系，为游赚模块后台管理提供权限控制
    """

    def __init__(self, perm: Union[str, List], is_strict: bool = False):
        """
        校验当前用户是否具有游赚模块相应的接口权限

        :param perm: 权限标识，格式为 yozuan:模块:操作，例如 yozuan:task:list, yozuan:order:edit
        :param is_strict: 当传入的权限标识是list类型时，是否开启严格模式，开启表示会校验列表中的每一个权限标识，所有的校验结果都需要为True才会通过
        """
        self.perm = perm
        self.is_strict = is_strict

    def __call__(self, current_user: CurrentUserModel = Depends(LoginService.get_current_user)):
        """
        执行权限检查
        
        权限标识格式：
        - yozuan:task:list      - 游赚任务列表查看权限
        - yozuan:task:add       - 游赚任务新增权限
        - yozuan:task:edit      - 游赚任务编辑权限
        - yozuan:task:remove    - 游赚任务删除权限
        - yozuan:task:export    - 游赚任务导出权限
        - yozuan:order:list     - 游赚订单列表查看权限
        - yozuan:order:review   - 游赚订单审核权限
        - yozuan:user:list      - 游赚用户列表查看权限
        - yozuan:user:edit      - 游赚用户编辑权限
        - yozuan:finance:list   - 游赚财务列表查看权限
        - yozuan:finance:review - 游赚财务审核权限
        - yozuan:system:config  - 游赚系统配置权限
        """
        user_auth_list = current_user.permissions
        
        # 超级管理员拥有所有权限
        if '*:*:*' in user_auth_list:
            return True
            
        # 游赚模块超级管理员权限
        if 'yozuan:*:*' in user_auth_list:
            return True
        
        if isinstance(self.perm, str):
            if self.perm in user_auth_list:
                return True
        if isinstance(self.perm, list):
            if self.is_strict:
                if all([perm_str in user_auth_list for perm_str in self.perm]):
                    return True
            else:
                if any([perm_str in user_auth_list for perm_str in self.perm]):
                    return True
        
        raise PermissionException(data='', message=f'该用户无游赚模块接口权限: {self.perm}')


class CheckYozuanRoleAuth:
    """
    根据角色校验当前用户是否具有游赚模块相应的接口权限
    """

    def __init__(self, role_key: Union[str, List], is_strict: bool = False):
        """
        根据角色校验当前用户是否具有游赚模块相应的接口权限

        :param role_key: 角色标识，例如 admin, yozuan_admin, yozuan_finance
        :param is_strict: 当传入的角色标识是list类型时，是否开启严格模式，开启表示会校验列表中的每一个角色标识，所有的校验结果都需要为True才会通过
        """
        self.role_key = role_key
        self.is_strict = is_strict

    def __call__(self, current_user: CurrentUserModel = Depends(LoginService.get_current_user)):
        """
        执行角色权限检查
        
        角色标识说明：
        - admin         - 系统超级管理员（拥有所有权限）
        - yozuan_admin  - 游赚模块管理员（拥有游赚模块所有权限）
        - yozuan_finance - 游赚财务管理员（拥有财务相关权限）
        - yozuan_cs     - 游赚客服（拥有用户管理和订单处理权限）
        """
        user_role_list = current_user.user.role
        user_role_key_list = [role.role_key for role in user_role_list]
        
        # 系统超级管理员拥有所有权限
        if 'admin' in user_role_key_list:
            return True
            
        if isinstance(self.role_key, str):
            if self.role_key in user_role_key_list:
                return True
        if isinstance(self.role_key, list):
            if self.is_strict:
                if all([role_key_str in user_role_key_list for role_key_str in self.role_key]):
                    return True
            else:
                if any([role_key_str in user_role_key_list for role_key_str in self.role_key]):
                    return True
        
        raise PermissionException(data='', message=f'该用户无游赚模块角色权限: {self.role_key}')


class CheckYozuanFinanceAuth:
    """
    游赚财务权限专用检查器
    用于需要财务权限的敏感操作
    """
    
    def __call__(self, current_user: CurrentUserModel = Depends(LoginService.get_current_user)):
        """
        检查财务权限
        只有系统管理员、游赚管理员、游赚财务管理员才能进行财务操作
        """
        user_auth_list = current_user.permissions
        user_role_list = current_user.user.role
        user_role_key_list = [role.role_key for role in user_role_list]
        
        # 超级管理员
        if '*:*:*' in user_auth_list or 'admin' in user_role_key_list:
            return True
            
        # 游赚模块权限
        if 'yozuan:*:*' in user_auth_list or 'yozuan_admin' in user_role_key_list:
            return True
            
        # 财务专门权限
        if ('yozuan:finance:*' in user_auth_list or 
            'yozuan:finance:review' in user_auth_list or 
            'yozuan_finance' in user_role_key_list):
            return True
        
        raise PermissionException(data='', message='该用户无游赚财务管理权限')


class CheckYozuanSuperAuth:
    """
    游赚超级管理员权限检查器
    用于系统配置、敏感数据操作等高权限操作
    """
    
    def __call__(self, current_user: CurrentUserModel = Depends(LoginService.get_current_user)):
        """
        检查超级管理员权限
        只有系统管理员、游赚超级管理员才能进行系统级操作
        """
        user_auth_list = current_user.permissions
        user_role_list = current_user.user.role
        user_role_key_list = [role.role_key for role in user_role_list]
        
        # 超级管理员
        if '*:*:*' in user_auth_list or 'admin' in user_role_key_list:
            return True
            
        # 游赚超级管理员
        if 'yozuan:*:*' in user_auth_list or 'yozuan_admin' in user_role_key_list:
            return True
        
        raise PermissionException(data='', message='该用户无游赚超级管理员权限')
