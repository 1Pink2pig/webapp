from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from datetime import datetime
from collections import defaultdict

router = APIRouter()


def _parse_month_str(month_str: str):
    """Parse 'YYYY-MM' into a datetime representing the first day of that month (UTC).
    Returns None if input falsy.
    """
    if not month_str:
        return None
    try:
        return datetime.strptime(month_str, "%Y-%m")
    except Exception:
        return None


def _next_month(dt: datetime):
    """Return datetime for first day of next month."""
    year = dt.year + (dt.month // 12)
    month = dt.month % 12 + 1
    return datetime(year, month, 1)


@router.post("/stats")
def admin_stats(startMonth: str = None, endMonth: str = None, regionKeyword: str = None, db: Session = Depends(get_db)):
    """Return aggregated statistics grouped by month (YYYY-MM) and region.

    Request shape (form/query or json fields accepted by FastAPI):
      - startMonth: 'YYYY-MM' (inclusive)
      - endMonth: 'YYYY-MM' (inclusive)
      - regionKeyword: substring match on Need.region

    Response shape:
      {"code":200, "msg":"ok", "data": { list: [...], totalNeed, totalServiceSuccess }}
    """

    now = datetime.utcnow()
    # parse inputs
    start_dt = _parse_month_str(startMonth)
    end_dt = _parse_month_str(endMonth)

    # default: last 6 months (including current month)
    if not start_dt or not end_dt:
        # start = first day of month, 5 months ago
        end_month_dt = datetime(now.year, now.month, 1)
        # compute start 5 months before
        month_offset = (end_month_dt.month - 1) - 5
        year = end_month_dt.year + (month_offset // 12)
        month = (month_offset % 12) + 1
        start_month_dt = datetime(year, month, 1)
        start_dt = start_month_dt
        end_dt = end_month_dt

    # inclusive end -> make end_next = first day of month after end
    end_next = _next_month(end_dt)

    # Query needs in the date range
    need_q = db.query(models.Need).filter(models.Need.create_time >= start_dt, models.Need.create_time < end_next)
    svc_q = db.query(models.Service).filter(models.Service.create_time >= start_dt, models.Service.create_time < end_next, models.Service.status == 1)

    if regionKeyword:
        kw = f"%{regionKeyword}%"
        need_q = need_q.filter(models.Need.region.ilike(kw))
        # join need for service to filter by region
        svc_q = svc_q.join(models.Need).filter(models.Need.region.ilike(kw))

    needs = need_q.all()
    services = svc_q.all()

    # aggregate by month and region
    grouped = defaultdict(lambda: {"monthNeedCount": 0, "monthServiceSuccessCount": 0})

    def month_str_from_dt(dt: datetime):
        return dt.strftime("%Y-%m")

    for n in needs:
        m = month_str_from_dt(n.create_time)
        key = (m, (n.region or ""))
        grouped[key]["monthNeedCount"] += 1

    for s in services:
        # try to get region via related need; fallback to empty
        region = ""
        try:
            if s.need and getattr(s.need, 'region', None):
                region = s.need.region
        except Exception:
            region = ""
        m = month_str_from_dt(s.create_time)
        key = (m, (region or ""))
        grouped[key]["monthServiceSuccessCount"] += 1

    # produce list entries
    results = []
    for (m, region), vals in grouped.items():
        results.append({
            "month": m,
            "region": region,
            "monthNeedCount": vals.get("monthNeedCount", 0),
            "monthServiceSuccessCount": vals.get("monthServiceSuccessCount", 0),
            "cumulativeNeedCount": 0,
            "cumulativeServiceSuccessCount": 0
        })

    # ensure months in range exist even if 0 - collect all months between start_dt and end_dt
    months = []
    cur = datetime(start_dt.year, start_dt.month, 1)
    while cur <= end_dt:
        months.append(cur.strftime("%Y-%m"))
        cur = _next_month(cur)

    # ensure that for each month and region present in grouped we keep entries; also if no regions exist, create a month-level zero row
    if not results:
        # return empty structure
        return {"code": 200, "msg": "ok", "data": {"list": [], "totalNeed": 0, "totalServiceSuccess": 0}}

    # sort results by month then region
    results.sort(key=lambda x: (x["month"], x["region"]))

    # compute cumulative per month (sum across regions)
    month_totals = {m: {"need": 0, "service": 0} for m in months}
    for r in results:
        if r["month"] in month_totals:
            month_totals[r["month"]]["need"] += r["monthNeedCount"]
            month_totals[r["month"]]["service"] += r["monthServiceSuccessCount"]
        else:
            month_totals[r["month"]] = {"need": r["monthNeedCount"], "service": r["monthServiceSuccessCount"]}

    # cumulative accumulation
    cum_need = 0
    cum_service = 0
    cum_map = {}
    for m in sorted(months, key=lambda x: datetime.strptime(x, "%Y-%m")):
        cum_need += month_totals.get(m, {}).get("need", 0)
        cum_service += month_totals.get(m, {}).get("service", 0)
        cum_map[m] = {"need": cum_need, "service": cum_service}

    # assign cumulative to each result item by its month
    for r in results:
        cm = cum_map.get(r["month"], {"need": 0, "service": 0})
        r["cumulativeNeedCount"] = cm["need"]
        r["cumulativeServiceSuccessCount"] = cm["service"]

    total_need = sum(r["monthNeedCount"] for r in results)
    total_service = sum(r["monthServiceSuccessCount"] for r in results)

    return {"code": 200, "msg": "ok", "data": {"list": results, "totalNeed": total_need, "totalServiceSuccess": total_service}}

