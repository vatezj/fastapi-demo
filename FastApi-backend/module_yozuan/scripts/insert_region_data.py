#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地区数据插入脚本
根据area-city.json文件插入地区数据到yozuan_task_region表
"""

import json
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config.database import ASYNC_SQLALCHEMY_DATABASE_URL


class RegionDataInserter:
    """地区数据插入器"""
    
    def __init__(self):
        self.engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def create_region_table(self):
        """创建地区表（如果不存在）"""
        async with self.engine.begin() as conn:
            # 创建地区表
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS yozuan_task_region (
                id INT PRIMARY KEY AUTO_INCREMENT COMMENT '地区ID',
                region_code VARCHAR(6) NOT NULL UNIQUE COMMENT '地区编码',
                region_name VARCHAR(50) NOT NULL COMMENT '地区名称',
                region_level VARCHAR(20) NOT NULL COMMENT '地区级别',
                parent_code VARCHAR(6) COMMENT '父级地区编码',
                center_coords VARCHAR(50) COMMENT '中心坐标',
                citycode VARCHAR(10) COMMENT '城市区号',
                status TINYINT DEFAULT 1 COMMENT '状态：1启用，0禁用',
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_region_code (region_code),
                INDEX idx_parent_code (parent_code),
                INDEX idx_region_level (region_level),
                INDEX idx_status (status)
            ) COMMENT '任务地区表';
            """
            await conn.execute(text(create_table_sql))
            print("✅ 地区表创建成功")
    
    async def insert_region_data(self, region_data):
        """插入地区数据"""
        async with self.async_session() as session:
            try:
                # 清空现有数据
                await session.execute(text("DELETE FROM yozuan_task_region"))
                print("🗑️  已清空现有地区数据")
                
                # 插入全国数据
                national_data = {
                    'region_code': '000000',
                    'region_name': '全国',
                    'region_level': 'country',
                    'parent_code': None,
                    'center_coords': None,
                    'citycode': None
                }
                
                insert_sql = """
                INSERT INTO yozuan_task_region 
                (region_code, region_name, region_level, parent_code, center_coords, citycode)
                VALUES (:region_code, :region_name, :region_level, :parent_code, :center_coords, :citycode)
                """
                
                await session.execute(text(insert_sql), national_data)
                print("✅ 插入全国数据")
                
                # 插入省份和城市数据
                for province in region_data:
                    # 插入省份
                    province_data = {
                        'region_code': province['adcode'],
                        'region_name': province['name'],
                        'region_level': province['level'],
                        'parent_code': None,
                        'center_coords': province['center'],
                        'citycode': province.get('citycode')
                    }
                    
                    await session.execute(text(insert_sql), province_data)
                    print(f"✅ 插入省份: {province['name']} ({province['adcode']})")
                    
                    # 插入城市
                    if 'districts' in province and province['districts']:
                        for city in province['districts']:
                            city_data = {
                                'region_code': city['adcode'],
                                'region_name': city['name'],
                                'region_level': city['level'],
                                'parent_code': province['adcode'],
                                'center_coords': city['center'],
                                'citycode': city.get('citycode')
                            }
                            
                            await session.execute(text(insert_sql), city_data)
                            print(f"  ✅ 插入城市: {city['name']} ({city['adcode']})")
                
                await session.commit()
                print("✅ 所有地区数据插入完成")
                
            except Exception as e:
                await session.rollback()
                print(f"❌ 插入数据失败: {str(e)}")
                raise
    
    async def verify_data(self):
        """验证插入的数据"""
        async with self.async_session() as session:
            # 统计各级别数据
            stats_sql = """
            SELECT 
                region_level,
                COUNT(*) as count
            FROM yozuan_task_region 
            GROUP BY region_level
            ORDER BY region_level
            """
            
            result = await session.execute(text(stats_sql))
            stats = result.fetchall()
            
            print("\n📊 数据统计:")
            for level, count in stats:
                print(f"  {level}: {count} 条")
            
            # 显示一些示例数据
            sample_sql = """
            SELECT region_code, region_name, region_level, parent_code
            FROM yozuan_task_region 
            WHERE region_level = 'city'
            LIMIT 5
            """
            
            result = await session.execute(text(sample_sql))
            samples = result.fetchall()
            
            print("\n📋 城市数据示例:")
            for code, name, level, parent in samples:
                print(f"  {code} - {name} ({level}) - 父级: {parent}")
    
    async def close(self):
        """关闭数据库连接"""
        await self.engine.dispose()


async def main():
    """主函数"""
    print("🚀 开始插入地区数据...")
    
    # 检查JSON文件是否存在
    json_file = Path(__file__).parent / "area-city.json"
    if not json_file.exists():
        print(f"❌ JSON文件不存在: {json_file}")
        return
    
    try:
        # 读取JSON数据
        with open(json_file, 'r', encoding='utf-8') as f:
            region_data = json.load(f)
        
        print(f"📖 读取到 {len(region_data)} 个省份数据")
        
        # 创建插入器
        inserter = RegionDataInserter()
        
        # 创建表
        await inserter.create_region_table()
        
        # 插入数据
        await inserter.insert_region_data(region_data)
        
        # 验证数据
        await inserter.verify_data()
        
        # 关闭连接
        await inserter.close()
        
        print("\n🎉 地区数据插入完成！")
        
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 