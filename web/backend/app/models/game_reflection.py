# -*- coding: utf-8 -*-
"""
游戏感悟功能 - 数据模型（Pydantic）
对应技术方案文档第三章
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ThemeEnum(str, Enum):
    """主题分类枚举"""
    WARMUP = "warmup"        # 🔥 热身
    AIM = "aim"              # 🎯 对枪/瞄准
    MOVE = "move"            # 🏃 身法/移动
    MIND = "mind"            # 🧠 意识/决策
    MAP = "map"              # 🗺️ 地图理解
    AGENT = "agent"          # 🎭 英雄/角色
    MINDSET = "mindset"      # 💡 心态/其他


class GameEnum(str, Enum):
    """游戏枚举"""
    VALORANT = "valorant"
    APEX = "apex"
    CS2 = "cs2"


# 主题中文名映射
THEME_NAMES = {
    "warmup": "热身",
    "aim": "对枪/瞄准",
    "move": "身法/移动",
    "mind": "意识/决策",
    "map": "地图理解",
    "agent": "英雄/角色",
    "mindset": "心态/其他",
}

# 主题图标映射
THEME_ICONS = {
    "warmup": "🔥",
    "aim": "🎯",
    "move": "🏃",
    "mind": "🧠",
    "map": "🗺️",
    "agent": "🎭",
    "mindset": "💡",
}

# 主题颜色映射
THEME_COLORS = {
    "warmup": "#ef4444",
    "aim": "#3b82f6",
    "move": "#10b981",
    "mind": "#a855f7",
    "map": "#f59e0b",
    "agent": "#ec4899",
    "mindset": "#6b7280",
}


class GameReflectionBase(BaseModel):
    """游戏感悟基础模型"""
    title: str = Field(..., description="感悟标题", max_length=200)
    content: str = Field(..., description="感悟内容 (Markdown)")
    theme: ThemeEnum = Field(..., description="主题分类")
    game: GameEnum = Field(default=GameEnum.VALORANT, description="游戏")
    mode: Optional[str] = Field(None, description="模式: ranked/deathmatch/custom/warmup")
    map_name: Optional[str] = Field(None, description="地图")
    agent_name: Optional[str] = Field(None, description="英雄/角色")
    scenario: Optional[str] = Field(None, description="场景描述")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    warmup_item: Optional[str] = Field(None, description="热身项目名称 (仅 warmup 主题)")


class GameReflectionCreate(GameReflectionBase):
    """创建感悟请求模型"""
    date: str = Field(..., description="日期 YYYY-MM-DD")


class GameReflectionUpdate(BaseModel):
    """更新感悟请求模型（只传需要更新的字段）"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    theme: Optional[ThemeEnum] = None
    game: Optional[GameEnum] = None
    mode: Optional[str] = None
    map_name: Optional[str] = None
    agent_name: Optional[str] = None
    scenario: Optional[str] = None
    tags: Optional[List[str]] = None
    warmup_item: Optional[str] = None


class GameReflectionResponse(GameReflectionBase):
    """感悟响应模型"""
    id: str
    date: str
    theme_name: str = ""
    theme_icon: str = ""
    theme_color: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __init__(self, **data):
        super().__init__(**data)
        # 自动填充主题中文名、图标、颜色
        self.theme_name = THEME_NAMES.get(self.theme.value, "")
        self.theme_icon = THEME_ICONS.get(self.theme.value, "")
        self.theme_color = THEME_COLORS.get(self.theme.value, "")


class GameReflectionStats(BaseModel):
    """感悟统计数据模型"""
    total_count: int = 0
    today_count: int = 0
    consecutive_days: int = 0
    theme_count: int = 0
    theme_distribution: dict = Field(default_factory=dict)


class WarmupItemBase(BaseModel):
    """热身项目基础模型"""
    name: str = Field(..., description="项目名称")
    type: str = Field(default="other", description="项目类型: tracking/reaction/other")
    description: Optional[str] = Field(None, description="项目描述")


class WarmupItemCreate(WarmupItemBase):
    """创建热身项目请求模型"""
    pass


class WarmupItemResponse(WarmupItemBase):
    """热身项目响应模型"""
    id: str
    created_at: Optional[datetime] = None
    reflections: List[GameReflectionResponse] = Field(default_factory=list)
