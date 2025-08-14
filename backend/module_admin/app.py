from fastapi import FastAPI
from config.env import AppConfig
from exceptions.handle import handle_exception
from .controller.cache_controller import cacheController
from .controller.captcha_controller import captchaController
from .controller.common_controller import commonController
from .controller.config_controller import configController
from .controller.dept_controller import deptController
from .controller.dict_controller import dictController
from .controller.log_controller import logController
from .controller.login_controller import loginController
from .controller.job_controller import jobController
from .controller.menu_controller import menuController
from .controller.notice_controller import noticeController
from .controller.online_controller import onlineController
from .controller.post_controler import postController
from .controller.role_controller import roleController
from .controller.server_controller import serverController
from .controller.user_controller import userController
from .controller.app_user_controller import app_user_admin_router
from module_generator.controller.gen_controller import genController

# 创建后台管理模块FastAPI应用
admin_app = FastAPI(
    title=f'{AppConfig.app_name} - 后台管理系统',
    description=f'{AppConfig.app_name}后台管理系统接口文档 - 面向系统管理员',
    version=AppConfig.app_version,
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
)

# 注册后台管理模块的路由
admin_app.include_router(loginController, tags=['登录模块'])
admin_app.include_router(captchaController, tags=['验证码模块'])
admin_app.include_router(userController, tags=['系统管理-用户管理'])
admin_app.include_router(roleController, tags=['系统管理-角色管理'])
admin_app.include_router(menuController, tags=['系统管理-菜单管理'])
admin_app.include_router(deptController, tags=['系统管理-部门管理'])
admin_app.include_router(postController, tags=['系统管理-岗位管理'])
admin_app.include_router(dictController, tags=['系统管理-字典管理'])
admin_app.include_router(configController, tags=['系统管理-参数管理'])
admin_app.include_router(noticeController, tags=['系统管理-通知公告管理'])
admin_app.include_router(logController, tags=['系统管理-日志管理'])
admin_app.include_router(onlineController, tags=['系统监控-在线用户'])
admin_app.include_router(jobController, tags=['系统监控-定时任务'])
admin_app.include_router(serverController, tags=['系统监控-菜单管理'])
admin_app.include_router(cacheController, tags=['系统监控-缓存监控'])
admin_app.include_router(commonController, tags=['通用模块'])
admin_app.include_router(genController, tags=['代码生成'])
admin_app.include_router(app_user_admin_router, tags=['APP用户管理'])

# 注册异常处理器到子应用
handle_exception(admin_app)
