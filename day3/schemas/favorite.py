from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from day3.schemas.base import NewsItemBase


class IsFavorite(BaseModel):
    is_favorite: bool = Field(..., description="是否收藏", alias="isFavorite")

class FavoriteAddRequest(BaseModel):
    """
    收藏请求参数
    """
    news_id: int = Field(..., description="新闻ID", alias="newsId")

class FavoriteItemBase(NewsItemBase):
    favorite_time: datetime = Field(..., description="收藏时间", alias="favoriteTime")
    favorite_id: int = Field(..., description="收藏ID", alias="favoriteId")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class FavoriteListResponse(BaseModel):
    """
    收藏列表响应参数
    """
    list_data: list[FavoriteItemBase] = Field(..., description="收藏列表", alias="list")
    total: int = Field(..., description="总条数")
    has_more: bool = Field(..., alias="hasMore", description="是否有更多" )
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )