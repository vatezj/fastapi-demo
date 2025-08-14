# -*- coding: utf-8 -*-
"""
APP后台管理接口控制器测试
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from module_app.controller.admin_interface_controller import admin_interface_router
from module_app.entity.vo.app_user_vo import (
    AppAddUserModel, AppEditUserModel, AppUserStatusModel, AppResetPasswordModel
)


class TestAdminInterfaceController:
    """APP后台管理接口控制器测试类"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(admin_interface_router)
        return TestClient(app)

    @pytest.fixture
    def mock_current_user(self):
        """模拟当前用户"""
        user = Mock()
        user.user_name = "admin"
        user.user_id = 1
        user.admin = True
        
        current_user = Mock()
        current_user.user = user
        current_user.permissions = ["app:user:list", "app:user:add", "app:user:edit", "app:user:remove"]
        
        return current_user

    @pytest.fixture
    def mock_app_user_service(self):
        """模拟APP用户服务"""
        service = Mock()
        service.get_user_list = AsyncMock()
        service.get_user_detail = AsyncMock()
        service.create_user = AsyncMock()
        service.update_user = AsyncMock()
        service.delete_user = AsyncMock()
        service.change_user_status = AsyncMock()
        service.reset_user_password = AsyncMock()
        return service

    @pytest.fixture
    def mock_login_log_service(self):
        """模拟登录日志服务"""
        service = Mock()
        service.get_login_log_list = AsyncMock()
        service.clear_login_log = AsyncMock()
        return service

    def test_get_app_user_list_success(self, client, mock_current_user, mock_app_user_service):
        """测试获取APP用户列表成功"""
        # 模拟服务返回数据
        mock_app_user_service.get_user_list.return_value = {
            "total": 1,
            "rows": [{"user_id": 1, "user_name": "testuser"}],
            "page_num": 1,
            "page_size": 10
        }
        
        with patch('module_app.controller.admin_interface_controller.AppUserService', mock_app_user_service):
            with patch('module_app.controller.admin_interface_controller.LoginService.get_current_user', return_value=mock_current_user):
                response = client.get("/admin/user/list?page_num=1&page_size=10")
                
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200
                assert "获取APP用户列表成功" in data["msg"]

    def test_get_app_user_list_with_filters(self, client, mock_current_user, mock_app_user_service):
        """测试带过滤条件获取APP用户列表"""
        mock_app_user_service.get_user_list.return_value = {
            "total": 0,
            "rows": [],
            "page_num": 1,
            "page_size": 10
        }
        
        with patch('module_app.controller.admin_interface_controller.AppUserService', mock_app_user_service):
            with patch('module_app.controller.admin_interface_controller.LoginService.get_current_user', return_value=mock_current_user):
                response = client.get("/admin/user/list?page_num=1&page_size=10&status=0&sex=0")
                
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200

    def test_get_app_user_detail_success(self, client, mock_current_user, mock_app_user_service):
        """测试获取APP用户详情成功"""
        mock_app_user_service.get_user_detail.return_value = {
            "user_id": 1,
            "user_name": "testuser",
            "nick_name": "测试用户"
        }
        
        with patch('module_app.controller.admin_interface_controller.AppUserService', mock_app_user_service):
            with patch('module_app.controller.admin_interface_controller.LoginService.get_current_user', return_value=mock_current_user):
                response = client.get("/admin/user/1")
                
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200
                assert "获取APP用户详情成功" in data["msg"]

    def test_add_app_user_success(self, client, mock_current_user, mock_app_user_service):
        """测试新增APP用户成功"""
        user_data = {
            "user_name": "newuser",
            "nick_name": "新用户",
            "password": "password123",
            "email": "new@example.com",
            "phone": "13800138001"
        }
        
        mock_app_user_service.create_user.return_value = {
            "code": 200,
            "msg": "用户创建成功",
            "data": {"user_id": 2}
        }
        
        with patch('module_app.controller.admin_interface_controller.AppUserService', mock_app_user_service):
            with patch('module_app.controller.admin_interface_controller.LoginService.get_current_user', return_value=mock_current_user):
                response = client.post("/admin/user/add", json=user_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200
                assert "新增APP用户成功" in data["msg"]

    def test_edit_app_user_success(self, client, mock_current_user, mock_app_user_service):
        """测试编辑APP用户成功"""
        user_data = {
            "user_id": 1,
            "nick_name": "更新后的昵称",
            "email": "updated@example.com"
        }
        
        mock_app_user_service.update_user.return_value = {
            "code": 200,
            "msg": "用户更新成功"
        }
        
        with patch('module_app.controller.admin_interface_controller.AppUserService', mock_app_user_service):
            with patch('module_app.controller.admin_interface_controller.LoginService.get_current_user', return_value=mock_current_user):
                response = client.put("/admin/user/edit", json=user_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200
                assert "编辑APP用户成功" in data["msg"]

    def test_delete_app_user_success(self, client, mock_current_user, mock_app_user_service):
        """测试删除APP用户成功"""
        user_ids = [1, 2, 3]
        
        mock_app_user_service.delete_user.return_value = {
            "code": 200,
            "msg": "用户删除成功"
        }
        
        with patch('module_app.controller.admin_interface_controller.AppUserService', mock_app_user_service):
            with patch('module_app.controller.admin_interface_controller.LoginService.get_current_user', return_value=mock_current_user):
                response = client.delete("/admin/user/delete", json=user_ids)
                
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200
                assert "删除APP用户成功" in data["msg"]

    def test_change_user_status_success(self, client, mock_current_user, mock_app_user_service):
        """测试修改用户状态成功"""
        status_data = {
            "user_id": 1,
            "status": "1"
        }
        
        mock_app_user_service.change_user_status.return_value = {
            "code": 200,
            "msg": "状态修改成功"
        }
        
        with patch('module_app.controller.admin_interface_controller.AppUserService', mock_app_user_service):
            with patch('module_app.controller.admin_interface_controller.LoginService.get_current_user', return_value=mock_current_user):
                response = client.put("/admin/user/status", json=status_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200
                assert "修改APP用户状态成功" in data["msg"]

    def test_reset_user_password_success(self, client, mock_current_user, mock_app_user_service):
        """测试重置用户密码成功"""
        password_data = {
            "user_id": 1,
            "new_password": "newpassword123"
        }
        
        mock_app_user_service.reset_user_password.return_value = {
            "code": 200,
            "msg": "密码重置成功"
        }
        
        with patch('module_app.controller.admin_interface_controller.AppUserService', mock_app_user_service):
            with patch('module_app.controller.admin_interface_controller.LoginService.get_current_user', return_value=mock_current_user):
                response = client.put("/admin/user/reset-password", json=password_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200
                assert "重置APP用户密码成功" in data["msg"]

    def test_get_login_log_list_success(self, client, mock_current_user, mock_login_log_service):
        """测试获取登录日志列表成功"""
        mock_login_log_service.get_login_log_list.return_value = {
            "total": 1,
            "rows": [{"log_id": 1, "user_name": "testuser"}],
            "page_num": 1,
            "page_size": 10
        }
        
        with patch('module_app.controller.admin_interface_controller.AppLoginLogService', mock_login_log_service):
            with patch('module_app.controller.admin_interface_controller.LoginService.get_current_user', return_value=mock_current_user):
                response = client.get("/admin/login-log/list?page_num=1&page_size=10")
                
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200
                assert "获取APP登录日志列表成功" in data["msg"]

    def test_clear_login_log_success(self, client, mock_current_user, mock_login_log_service):
        """测试清空登录日志成功"""
        mock_login_log_service.clear_login_log.return_value = {
            "code": 200,
            "msg": "日志清空成功"
        }
        
        with patch('module_app.controller.admin_interface_controller.AppLoginLogService', mock_login_log_service):
            with patch('module_app.controller.admin_interface_controller.LoginService.get_current_user', return_value=mock_current_user):
                response = client.delete("/admin/login-log/clear")
                
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200
                assert "清空APP登录日志成功" in data["msg"]

    def test_get_stats_overview_success(self, client, mock_current_user):
        """测试获取统计概览成功"""
        with patch('module_app.controller.admin_interface_controller.LoginService.get_current_user', return_value=mock_current_user):
            response = client.get("/admin/stats/overview")
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert "获取APP统计概览成功" in data["msg"]
            assert "total_users" in data["data"]
            assert "active_users" in data["data"]
            assert "today_new_users" in data["data"]
            assert "total_login_logs" in data["data"]

    def test_permission_denied(self, client):
        """测试权限不足的情况"""
        # 不提供权限验证，应该返回401
        response = client.get("/admin/user/list")
        assert response.status_code == 401

    def test_invalid_page_params(self, client, mock_current_user, mock_app_user_service):
        """测试无效的分页参数"""
        mock_app_user_service.get_user_list.return_value = {
            "total": 0,
            "rows": [],
            "page_num": 1,
            "page_size": 10
        }
        
        with patch('module_app.controller.admin_interface_controller.AppUserService', mock_app_user_service):
            with patch('module_app.controller.admin_interface_controller.LoginService.get_current_user', return_value=mock_current_user):
                # 测试无效的页码
                response = client.get("/admin/user/list?page_num=0&page_size=10")
                assert response.status_code == 422  # 参数验证失败
                
                # 测试无效的页面大小
                response = client.get("/admin/user/list?page_num=1&page_size=0")
                assert response.status_code == 422  # 参数验证失败
                
                # 测试过大的页面大小
                response = client.get("/admin/user/list?page_num=1&page_size=101")
                assert response.status_code == 422  # 参数验证失败


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
