"""Inventory health analytics."""

from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from app.repositories.analytics import AnalyticsRepository
from app.schemas.filters import AnalyticsFilter


class InventoryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = AnalyticsRepository(session)

    def snapshot(self) -> pd.DataFrame:
        return self.repo.fetch_inventory()

    def low_stock(self) -> pd.DataFrame:
        inv = self.snapshot()
        if inv.empty:
            return inv
        mask = inv["quantity_on_hand"] <= inv["reorder_level"]
        result: pd.DataFrame = inv.loc[mask].sort_values("quantity_on_hand").reset_index(drop=True)
        return result

    def velocity(self, filters: AnalyticsFilter | None = None) -> pd.DataFrame:
        """Units sold in filter window vs on-hand (all stores summed)."""
        lines = self.repo.fetch_order_lines(filters)
        inv = self.snapshot()
        if lines.empty:
            sold = pd.DataFrame(columns=["product_id", "qty_sold"])
        else:
            sold = lines.groupby("product_id", as_index=False).agg(qty_sold=("quantity", "sum"))
        if inv.empty:
            return sold
        stock = inv.groupby(["product_id", "sku", "product_name"], as_index=False).agg(
            quantity_on_hand=("quantity_on_hand", "sum")
        )
        out = stock.merge(sold, on="product_id", how="left")
        out["qty_sold"] = out["qty_sold"].fillna(0)
        cover: list[float | None] = []
        for on_hand, sold_qty in zip(
            out["quantity_on_hand"].tolist(), out["qty_sold"].tolist(), strict=True
        ):
            if sold_qty:
                cover.append(float(on_hand) / float(sold_qty))
            else:
                cover.append(None)
        out["days_of_cover_proxy"] = cover
        result: pd.DataFrame = out.sort_values("qty_sold", ascending=False).reset_index(drop=True)
        return result
