from pydantic import BaseModel


class GrowthPoint(BaseModel):
    period: str          # "YYYY-MM"
    new_members: int
    cumulative: int


class MemberStatus(BaseModel):
    active: int
    inactive: int
    active_days: int


class BookingByStatus(BaseModel):
    status: str
    count: int


class BookingByDay(BaseModel):
    date: str             # "YYYY-MM-DD"
    count: int


class BookingStats(BaseModel):
    total: int
    by_status: list[BookingByStatus]
    by_day: list[BookingByDay]


class ServiceDistribution(BaseModel):
    service: str
    count: int


class DashboardAnalytics(BaseModel):
    member_growth: list[GrowthPoint]
    member_status: MemberStatus
    booking_stats: BookingStats
    service_distribution: list[ServiceDistribution]