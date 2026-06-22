"""Generate dashboard.png and chatbot.png preview assets for app/assets/."""

from PIL import Image, ImageDraw, ImageFont
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "app", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

W, H = 1280, 800

# ── colour palette (mirrors custom.css) ──────────────────────────────────────
BG        = (15,  17,  26)   # dark navy
SIDEBAR   = (22,  24,  38)
CARD      = (28,  32,  50)
ACCENT1   = (100, 210, 255)  # sky-blue
ACCENT2   = (130, 100, 255)  # violet
POSITIVE  = (72,  199, 142)
WARNING   = (255, 179,  71)
DANGER    = (255,  90,  90)
TEXT_PRI  = (230, 235, 255)
TEXT_SEC  = (130, 145, 175)
WHITE     = (255, 255, 255)
BORDER    = (45,  52,  80)

def _font(size, bold=False):
    """Best-effort font loader."""
    candidates = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    bold_candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
    ]
    pool = bold_candidates if bold else candidates
    for path in pool:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _card(draw, x, y, w, h, radius=10, fill=CARD, border=BORDER):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=border, width=1)


def _bar(draw, x, y, bar_w, bar_h, value, max_val, color):
    """Horizontal bar."""
    fill_w = int(bar_w * value / max(max_val, 1))
    draw.rounded_rectangle([x, y, x + bar_w, y + bar_h], radius=3, fill=SIDEBAR)
    draw.rounded_rectangle([x, y, x + fill_w, y + bar_h], radius=3, fill=color)


# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def make_dashboard():
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── sidebar ───────────────────────────────────────────────────────────────
    draw.rectangle([0, 0, 220, H], fill=SIDEBAR)
    draw.line([(220, 0), (220, H)], fill=BORDER, width=1)

    # app icon + title in sidebar
    draw.ellipse([18, 18, 50, 50], fill=ACCENT1)
    draw.text((58, 24), "AI Supply Chain", font=_font(13, bold=True), fill=TEXT_PRI)
    draw.text((58, 41), "Dashboard", font=_font(10), fill=TEXT_SEC)

    nav_items = [
        ("Dashboard + Chat", True),
        ("Data Upload",       False),
        ("Filters & Search",  False),
        ("Data Visualization",False),
        ("KPIs",              False),
        ("Demand Forecast",   False),
        ("Supplier Insights", False),
        ("Settings",          False),
    ]
    for i, (label, active) in enumerate(nav_items):
        y0 = 80 + i * 42
        if active:
            draw.rounded_rectangle([8, y0, 212, y0 + 34], radius=8, fill=CARD, outline=ACCENT1, width=1)
            draw.text((20, y0 + 9), label, font=_font(12, bold=True), fill=ACCENT1)
        else:
            draw.text((20, y0 + 9), label, font=_font(12), fill=TEXT_SEC)

    # ── top hero bar ──────────────────────────────────────────────────────────
    draw.rectangle([221, 0, W, 60], fill=(20, 23, 36))
    draw.text((240, 14), "📦  AI Supply Chain Dashboard", font=_font(18, bold=True), fill=TEXT_PRI)
    draw.text((240, 38), "Data-driven insights · Demand forecasting · Supplier intelligence",
              font=_font(10), fill=TEXT_SEC)

    # ── section header ────────────────────────────────────────────────────────
    draw.text((240, 74), "Dashboard + Chat Workspace", font=_font(14, bold=True), fill=TEXT_PRI)
    draw.line([(240, 94), (W - 20, 94)], fill=BORDER, width=1)

    # ── KPI cards ─────────────────────────────────────────────────────────────
    kpis = [
        ("Total Orders",    "12,847",  "+8.3%",  POSITIVE),
        ("Revenue",         "$4.2M",   "+12.1%", POSITIVE),
        ("On-Time Delivery","94.6%",   "+2.1%",  POSITIVE),
        ("Pending Issues",  "38",      "-5 today", WARNING),
    ]
    kpi_y = 110
    card_w = (W - 240 - 20 - 30) // 4
    for i, (label, val, delta, color) in enumerate(kpis):
        cx = 240 + i * (card_w + 10)
        _card(draw, cx, kpi_y, card_w, 90)
        draw.text((cx + 14, kpi_y + 12), label,  font=_font(10), fill=TEXT_SEC)
        draw.text((cx + 14, kpi_y + 30), val,    font=_font(20, bold=True), fill=TEXT_PRI)
        draw.text((cx + 14, kpi_y + 58), delta,  font=_font(10, bold=True), fill=color)

    # ── mini line chart (demand trend) ────────────────────────────────────────
    chart_x, chart_y, chart_w, chart_h = 240, 220, 560, 230
    _card(draw, chart_x, chart_y, chart_w, chart_h)
    draw.text((chart_x + 14, chart_y + 12), "Demand Forecast Trend",
              font=_font(12, bold=True), fill=TEXT_PRI)

    import math
    points_raw = [420, 460, 510, 490, 530, 570, 555, 610, 590, 640, 625, 680]
    n = len(points_raw)
    min_v, max_v = min(points_raw), max(points_raw)
    px_area = (chart_x + 20, chart_y + 40, chart_x + chart_w - 20, chart_y + chart_h - 30)
    pa_w = px_area[2] - px_area[0]
    pa_h = px_area[3] - px_area[1]

    # shaded area under line
    poly = []
    for i, v in enumerate(points_raw):
        px = px_area[0] + int(i / (n - 1) * pa_w)
        py = px_area[3] - int((v - min_v) / (max_v - min_v) * pa_h * 0.85)
        poly.append((px, py))
    poly_filled = poly + [(poly[-1][0], px_area[3]), (poly[0][0], px_area[3])]
    draw.polygon(poly_filled, fill=(100, 210, 255, 40))

    # draw line
    for i in range(len(poly) - 1):
        draw.line([poly[i], poly[i+1]], fill=ACCENT1, width=2)

    # dots
    for px, py in poly:
        draw.ellipse([px-3, py-3, px+3, py+3], fill=ACCENT1)

    # x-axis labels
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for i, m in enumerate(months):
        px = px_area[0] + int(i / (n - 1) * pa_w)
        draw.text((px - 8, px_area[3] + 4), m, font=_font(8), fill=TEXT_SEC)

    # ── supplier breakdown (right panel) ─────────────────────────────────────
    sp_x, sp_y, sp_w, sp_h = 820, 220, W - 840, 230
    _card(draw, sp_x, sp_y, sp_w, sp_h)
    draw.text((sp_x + 14, sp_y + 12), "Supplier Performance",
              font=_font(12, bold=True), fill=TEXT_PRI)

    suppliers = [
        ("Supplier A", 92, POSITIVE),
        ("Supplier B", 78, WARNING),
        ("Supplier C", 87, POSITIVE),
        ("Supplier D", 61, DANGER),
        ("Supplier E", 95, POSITIVE),
    ]
    for i, (name, score, color) in enumerate(suppliers):
        sy = sp_y + 42 + i * 34
        draw.text((sp_x + 14, sy), name, font=_font(10), fill=TEXT_SEC)
        _bar(draw, sp_x + 110, sy + 2, sp_w - 130, 14, score, 100, color)
        draw.text((sp_x + sp_w - 36, sy), f"{score}%", font=_font(10, bold=True), fill=TEXT_PRI)

    # ── data table preview ────────────────────────────────────────────────────
    tbl_x, tbl_y, tbl_w, tbl_h = 240, 470, W - 260, 290
    _card(draw, tbl_x, tbl_y, tbl_w, tbl_h)
    draw.text((tbl_x + 14, tbl_y + 12), "Recent Orders (preview)",
              font=_font(12, bold=True), fill=TEXT_PRI)

    cols_headers = ["Order ID", "Product", "Qty", "Status", "Delivery Date", "Supplier"]
    col_widths    = [90, 170, 60, 110, 130, 140]
    hdr_y = tbl_y + 38
    draw.rectangle([tbl_x + 10, hdr_y, tbl_x + tbl_w - 10, hdr_y + 26], fill=(35, 40, 62))
    cx = tbl_x + 18
    for hdr, cw in zip(cols_headers, col_widths):
        draw.text((cx, hdr_y + 6), hdr, font=_font(9, bold=True), fill=ACCENT1)
        cx += cw

    rows_data = [
        ("#ORD-4821", "Microchip X200",  "500",  "Shipped",   "2026-06-28", "Supplier A"),
        ("#ORD-4820", "Steel Rod 10mm",  "1200", "Processing","2026-07-02", "Supplier C"),
        ("#ORD-4819", "PCB Assembly",    "300",  "Delivered", "2026-06-20", "Supplier B"),
        ("#ORD-4818", "Aluminum Plate",  "750",  "Delayed",   "2026-07-10", "Supplier D"),
        ("#ORD-4817", "Sensor Module",   "200",  "Shipped",   "2026-06-25", "Supplier E"),
        ("#ORD-4816", "Cable Bundle",    "1000", "Processing","2026-07-05", "Supplier A"),
    ]
    status_colors = {"Shipped": POSITIVE, "Delivered": ACCENT1, "Processing": WARNING, "Delayed": DANGER}

    for r, row in enumerate(rows_data):
        ry = hdr_y + 26 + r * 30
        if r % 2 == 0:
            draw.rectangle([tbl_x + 10, ry, tbl_x + tbl_w - 10, ry + 29], fill=(32, 36, 55))
        rx = tbl_x + 18
        for c, (cell, cw) in enumerate(zip(row, col_widths)):
            color = status_colors.get(cell, TEXT_PRI) if c == 3 else TEXT_PRI
            draw.text((rx, ry + 8), cell, font=_font(9), fill=color)
            rx += cw

    img.save(os.path.join(ASSETS_DIR, "dashboard.png"), "PNG")
    print("✔  dashboard.png saved")


# ═══════════════════════════════════════════════════════════════════════════════
#  CHATBOT
# ═══════════════════════════════════════════════════════════════════════════════
def make_chatbot():
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── sidebar (same as dashboard) ───────────────────────────────────────────
    draw.rectangle([0, 0, 220, H], fill=SIDEBAR)
    draw.line([(220, 0), (220, H)], fill=BORDER, width=1)
    draw.ellipse([18, 18, 50, 50], fill=ACCENT2)
    draw.text((58, 24), "AI Supply Chain", font=_font(13, bold=True), fill=TEXT_PRI)
    draw.text((58, 41), "Chatbot", font=_font(10), fill=TEXT_SEC)

    nav_items = [
        ("Dashboard + Chat", False),
        ("Data Upload",       False),
        ("Filters & Search",  False),
        ("Data Visualization",False),
        ("KPIs",              False),
        ("Demand Forecast",   False),
        ("Supplier Insights", False),
        ("Settings",          False),
    ]
    for i, (label, active) in enumerate(nav_items):
        y0 = 80 + i * 42
        dot_color = ACCENT2 if i == 0 else TEXT_SEC
        draw.text((20, y0 + 9), label, font=_font(12), fill=dot_color)

    # active indicator on Dashboard + Chat (chatbot tab is active)
    draw.rounded_rectangle([8, 80, 212, 114], radius=8, fill=CARD, outline=ACCENT2, width=1)
    draw.text((20, 89), "Dashboard + Chat", font=_font(12, bold=True), fill=ACCENT2)

    # ── top hero bar ──────────────────────────────────────────────────────────
    draw.rectangle([221, 0, W, 60], fill=(20, 23, 36))
    draw.text((240, 14), "📦  AI Supply Chain Dashboard", font=_font(18, bold=True), fill=TEXT_PRI)
    draw.text((240, 38), "Data-driven insights · Demand forecasting · Supplier intelligence",
              font=_font(10), fill=TEXT_SEC)

    # ── tab bar ───────────────────────────────────────────────────────────────
    draw.rectangle([221, 60, W, 100], fill=(22, 25, 40))
    draw.rounded_rectangle([240, 66, 380, 96], radius=8, fill=CARD)
    draw.text((270, 74), "Dashboard", font=_font(12), fill=TEXT_SEC)
    draw.rounded_rectangle([385, 66, 490, 96], radius=8, fill=ACCENT2)
    draw.text((404, 74), "Chatbot", font=_font(12, bold=True), fill=WHITE)

    # ── chat window ───────────────────────────────────────────────────────────
    chat_x = 240
    chat_y = 108
    chat_w = W - 260
    chat_h = H - 108 - 10
    _card(draw, chat_x, chat_y, chat_w, chat_h, radius=12)

    # header
    draw.text((chat_x + 16, chat_y + 14), "🤖  AI Supply Chain Assistant",
              font=_font(13, bold=True), fill=TEXT_PRI)
    draw.text((chat_x + 16, chat_y + 34), "Ask anything about your inventory, orders, forecasts or suppliers.",
              font=_font(9), fill=TEXT_SEC)
    draw.line([(chat_x + 10, chat_y + 52), (chat_x + chat_w - 10, chat_y + 52)],
              fill=BORDER, width=1)

    # chat messages
    messages = [
        ("user",  "What is the current on-time delivery rate for Supplier A?"),
        ("bot",   "Supplier A currently has a 94.6% on-time delivery rate this quarter, which is above the fleet average of 89.2%. Their last 3 shipments all arrived within the expected window."),
        ("user",  "Show me the top 3 delayed orders and their estimated arrival dates."),
        ("bot",   "Here are the top 3 delayed orders:\n1. #ORD-4818 – Aluminum Plate – ETA: 2026-07-10 (3 days late)\n2. #ORD-4809 – Copper Wire – ETA: 2026-07-08 (1 day late)\n3. #ORD-4795 – Sensor Kit – ETA: 2026-07-12 (5 days late)"),
        ("user",  "What is the demand forecast for next month?"),
        ("bot",   "Demand forecast for July 2026 predicts a 12.4% increase over June, driven primarily by Microchip and Sensor Module categories. Recommended reorder quantities have been flagged in the Demand Forecast view."),
    ]

    msg_y = chat_y + 62
    bubble_max_w = chat_w - 60
    for role, text in messages:
        is_user = role == "user"
        lines = text.split("\n")
        line_h = 16
        bubble_h = 14 + len(lines) * line_h + 10

        if is_user:
            bx = chat_x + chat_w - bubble_max_w // 2 - 40
            bw = bubble_max_w // 2
            draw.rounded_rectangle([bx, msg_y, bx + bw, msg_y + bubble_h],
                                    radius=10, fill=(50, 55, 90), outline=ACCENT2, width=1)
            for li, line in enumerate(lines):
                draw.text((bx + 12, msg_y + 10 + li * line_h), line,
                          font=_font(10), fill=TEXT_PRI)
        else:
            bx = chat_x + 10
            bw = int(bubble_max_w * 0.72)
            draw.rounded_rectangle([bx, msg_y, bx + bw, msg_y + bubble_h],
                                    radius=10, fill=CARD, outline=ACCENT1, width=1)
            # bot avatar
            draw.ellipse([bx - 18, msg_y + 4, bx - 4, msg_y + 18], fill=ACCENT1)
            for li, line in enumerate(lines):
                draw.text((bx + 12, msg_y + 10 + li * line_h), line,
                          font=_font(10), fill=TEXT_PRI)

        msg_y += bubble_h + 10
        if msg_y > chat_y + chat_h - 100:
            break

    # ── input bar ─────────────────────────────────────────────────────────────
    input_y = chat_y + chat_h - 58
    draw.line([(chat_x + 10, input_y - 8), (chat_x + chat_w - 10, input_y - 8)],
              fill=BORDER, width=1)
    draw.rounded_rectangle([chat_x + 10, input_y, chat_x + chat_w - 80, input_y + 42],
                            radius=8, fill=(28, 32, 52), outline=BORDER, width=1)
    draw.text((chat_x + 24, input_y + 12), "Ask about inventory, orders, forecasts…",
              font=_font(10), fill=TEXT_SEC)
    # send button
    send_bx = chat_x + chat_w - 72
    draw.rounded_rectangle([send_bx, input_y, send_bx + 56, input_y + 42],
                            radius=8, fill=ACCENT2)
    draw.text((send_bx + 14, input_y + 12), "Send", font=_font(11, bold=True), fill=WHITE)

    img.save(os.path.join(ASSETS_DIR, "chatbot.png"), "PNG")
    print("✔  chatbot.png saved")


if __name__ == "__main__":
    make_dashboard()
    make_chatbot()
    print(f"\nAssets written to: {ASSETS_DIR}")
