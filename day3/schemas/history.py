from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from day3.schemas.base import NewsItemBase


class HistoryAddRequest(BaseModel):
    """
    历史记录添加请求参数
    """
    news_id: int = Field(..., description="新闻ID", alias="newsId")

class HistoryRequest(BaseModel):
    """
    历史记录响应参数
    """
    id: int = Field(..., description="历史记录ID")
    user_id: int = Field(..., description="用户ID", alias="userId")
    news_id: int = Field(..., description="新闻ID", alias="newsId")
    view_time: datetime = Field(..., description="查看时间", alias="viewTime")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class HistoryItemBase(NewsItemBase):
    view_time: datetime = Field(..., description="查看时间", alias="viewTime")
    history_id: int = Field(..., description="历史记录ID", alias="historyId")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class HistoryListResponse(BaseModel):
    """
    历史记录列表响应参数
    """
    list_data: list[HistoryItemBase] = Field(..., description="历史记录列表", alias="list")
    total: int = Field(..., description="总条数")
    has_more: bool = Field(..., alias="hasMore", description="是否有更多" )
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
