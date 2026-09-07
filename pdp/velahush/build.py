import json, copy, random, string, re, os
S = os.path.dirname(os.path.abspath(__file__))
def load(name): return json.load(open(f"{S}/src/{name}.json"))
ALPH = string.ascii_letters + string.digits + "_-"
USED = set()
def uid():
    while True:
        u = "g" + "".join(random.choice(ALPH) for _ in range(9))
        if u not in USED:
            USED.add(u); return u

def find(n, pred):
    if pred(n): return n
    for c in n.get("childrens", []) or []:
        r = find(c, pred)
        if r: return r
    return None

# ---------- harvest templates from real exports ----------
hero = load("hero-buy-block")["component"]
header = load("header")["component"]
tests = load("three-tests")["component"]
sticky_tpl = json.loads(open(f"{S}/src/sticky-template.json").read())
LIB = {}
def strip(n):
    n = copy.deepcopy(n); n.pop("childrens", None); n.pop("_comments", None); return n
LIB["Section"] = strip(tests)
LIB["Row"] = strip(find(hero, lambda n: n["uid"] == "gHeRowPln2"))
LIB["Col"] = strip(find(hero, lambda n: n["tag"] == "Col"))
LIB["Text"] = strip(find(header, lambda n: n["tag"] == "Text"))
LIB["Heading"] = strip(find(header, lambda n: n["tag"] == "Heading"))
LIB["Button"] = strip(find(header, lambda n: n["tag"] == "Button"))
# library templates pasted from MCP results
for tag in ["Image", "Icon", "IconListV2", "Product", "ProductImagesV3", "ProductTitle", "ProductPrice", "ProductButton", "ProductVariants"]:
    LIB[tag] = json.load(open(f"{S}/lib/{tag}.json"))
    LIB[tag].pop("_comments", None)
LIB["Product"].pop("childrens", None)
sticky_root = sticky_tpl[0] if isinstance(sticky_tpl, list) else sticky_tpl
LIB["Sticky"] = strip(sticky_root)

def deep_set(d, path, value):
    keys = path.split(".")
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value

def mk(tag, children=None, **sets):
    n = copy.deepcopy(LIB[tag]); n["uid"] = uid()
    for k, v in sets.items():
        deep_set(n, k.replace("__", "."), v)
    if children is not None: n["childrens"] = children
    return n

FONT = {"value": "Archivo", "type": "google"}
INK = "#201e1d"; MUTED = "#605d5d"; BRAND = "#2f5db3"; BRAND_LIGHT = "#eaf0fb"; RED = "#d8321f"; CREAM = "#fff7d6"; PAPER = "#f3f2f2"

def typo(size, weight="400", color=INK, align="left", lh="1.5", transform="none", ls="normal", mobile=None):
    t = {"type": "paragraph-1",
         "attrs": {"color": color, "transform": transform, "textAlign": {"desktop": align}},
         "custom": {"fontSize": {"desktop": f"{size}px"}, "fontWeight": weight, "lineHeight": {"desktop": lh},
                    "letterSpacing": {"desktop": ls}, "fontFamily": FONT, "fontStyle": "normal",
                    "textShadow": {"enable": False}, "hasShadowText": False}}
    if mobile: t["custom"]["fontSize"]["mobile"] = f"{mobile}px"
    return t

def text(html, size=16, weight="400", color=INK, align="left", lh="1.5", transform="none", ls="normal", mb="0px", mobile=None, tag="div"):
    n = mk("Text")
    n["settings"]["text"] = html if html.startswith("<") else f"<p>{html}</p>"
    n["settings"]["htmlTag"] = tag
    n["styles"]["typo"] = typo(size, weight, color, align, lh, transform, ls, mobile)
    n["styles"]["textAlign"] = {"desktop": align}; n["styles"]["align"] = {"desktop": align}
    n["advanced"]["spacing-setting"] = {"desktop": {"margin": {"bottom": mb}}}
    return n

def heading(html, size=32, weight="800", color=INK, align="left", lh="1.2", htmlTag="h2", mb="0px", mobile=None, transform="none", ls="-0.02em"):
    n = mk("Heading")
    n["settings"]["text"] = html if html.startswith("<") else f"<p>{html}</p>"
    n["settings"]["htmlTag"] = htmlTag
    t = typo(size, weight, color, align, lh, transform, ls, mobile); t["type"] = "heading-1"
    n["styles"]["typo"] = t
    n["styles"]["textAlign"] = {"desktop": align}; n["styles"]["align"] = {"desktop": align}
    n["advanced"]["spacing-setting"] = {"desktop": {"margin": {"bottom": mb}}}
    return n

def col(children, **sets):
    n = mk("Col", children);
    for k, v in sets.items(): deep_set(n, k.replace("__", "."), v)
    return n

def row(cols, children_per_col, display="fill", mobile_cols=None, bg="transparent", pad=None, radius=None, border=None, gutter="8px", width="default", gap="8px", mb="0px", align_v="start", shadow=None, mobile_display=None):
    n = mk("Row")
    n["settings"]["layout"] = {"desktop": {"cols": cols, "display": display, "gap": gap}}
    if mobile_cols: n["settings"]["layout"]["mobile"] = {"cols": mobile_cols, "display": mobile_display or display}
    n["settings"]["verticalAlign"] = {"desktop": align_v}
    n["styles"]["width"] = {"desktop": width}
    n["styles"]["verticalGutter"] = {"desktop": gutter}
    n["styles"]["verticalGutterMobile"] = {"desktop": gutter}
    n["styles"]["background"] = {"desktop": {"type": "color", "color": bg, "image": {"src": "", "width": 0, "height": 0}, "size": "cover", "position": {"x": 50, "y": 50}, "repeat": "no-repeat", "attachment": "scroll"}}
    n["styles"].pop("padding", None)
    sp = {"desktop": {"margin": {"bottom": mb}}}
    if pad: sp["desktop"]["padding"] = {"top": pad[0], "right": pad[1], "bottom": pad[2], "left": pad[3]}
    n["advanced"]["spacing-setting"] = sp
    if radius:
        n["advanced"]["rounded"] = {"desktop": {"normal": {"btrr": radius, "bblr": radius, "bbrr": radius, "btlr": radius, "radiusType": "custom"}}}
    else:
        n["advanced"]["rounded"] = {"desktop": {"normal": {"btrr": "0px", "bblr": "0px", "bbrr": "0px", "btlr": "0px", "radiusType": "none"}}}
    if border:
        w, c = border
        n["advanced"]["border"] = {"desktop": {"normal": {"borderType": "style-1", "border": "solid", "width": f"{w} {w} {w} {w}", "color": c, "isCustom": True}}}
    else:
        n["advanced"]["border"] = {"desktop": {"normal": {"borderType": "none", "border": "none", "width": "1px 1px 1px 1px", "color": "line-3", "isCustom": True}}}
    if shadow:
        n["advanced"]["hasBoxShadow"] = {"desktop": {"normal": True}}
        n["advanced"]["boxShadow"] = {"desktop": {"normal": {"type": "shadow-1", "distance": "4px", "blur": "16px", "spread": "0px", "color": "rgba(0,0,0,0.08)", "angle": 90}}}
    else:
        n["advanced"]["hasBoxShadow"] = {"desktop": {"normal": False}}
        n["advanced"]["boxShadow"] = {"desktop": {"normal": {}}}
    n["childrens"] = [col(ch) for ch in children_per_col]
    return n

def section(children, bg=PAPER, pad=("48px", "48px"), cols=None, gutter="16px"):
    n = mk("Section")
    n["settings"]["layout"] = {"desktop": {"cols": [12], "display": "fill", "gap": "8px"}}
    n["styles"]["background"] = {"desktop": {"type": "color", "color": bg, "image": {"src": "", "width": 0, "height": 0}, "size": "cover", "position": {"x": 50, "y": 50}, "repeat": "no-repeat", "attachment": "scroll", "preload": False}}
    n["styles"]["verticalGutter"] = {"desktop": gutter}
    n["styles"]["verticalGutterMobile"] = {"desktop": "0px"}
    n["styles"]["enablePagePadding"] = {"desktop": True, "tablet": True, "mobile": True}
    n["advanced"]["spacing-setting"] = {"desktop": {"padding": {"top": pad[0], "bottom": pad[1]}}, "mobile": {"padding": {"top": "28px", "bottom": "28px"}}}
    n["advanced"]["border"] = {"desktop": {"normal": {"borderType": "none", "border": "none", "width": "1px 1px 1px 1px", "color": "line-3", "isCustom": True}}}
    n["childrens"] = [col(children)]
    return n

def container(children, bg="transparent", gutter="16px", pad=None, radius=None, border=None, shadow=None, width="1200px"):
    """Centered 1200px content row (Pattern 1)."""
    r = row([12], [children], bg=bg, gutter=gutter, pad=pad, radius=radius, border=border, shadow=shadow, width=width)
    r["styles"]["align"] = {"desktop": "center"}
    return r

CDN = "https://cdn.shopify.com/s/files/1/1004/8402/2636/files/"
IMG = {
 "relief": CDN + "01-relief2-velahush.png?v=1788662292",
 "triple": CDN + "11-triple-mist-velahush_6517baa9-8138-444a-9af8-bd05de8cea03.png?v=1788662292",
 "six": CDN + "06-six-features-velahush_a2c98e3d-586c-44e2-b663-874deefeba0e.png?v=1788662292",
 "droplets": CDN + "05-droplets2-velahush.png?v=1788662292",
 "before_after": CDN + "10-before-after.png?v=1788633023",
 "collage": CDN + "07-collage.png?v=1788633023",
 "percent": CDN + "02-97-percent.png?v=1788633023",
 "results": CDN + "03-customer-results.png?v=1788633024",
 "five": CDN + "08-five-reasons.png?v=1788633024",
 "struggle": CDN + "09-no-more-struggling.png?v=1788633023",
 "commitment": CDN + "04-commitment.png?v=1788633023",
 "ultimate": CDN + "16-ultimate.png?v=1788633024",
}
def image(key, alt, radius="16px", width="100%", mb="0px"):
    n = mk("Image")
    src = IMG[key]
    n["settings"]["srcSet"] = {"desktop": {"src": src, "width": 1254, "height": 1254}}
    n["settings"]["image"] = {"src": src, "width": 1254, "height": 1254}
    n["settings"]["alt"] = alt
    n["settings"]["imageStyle"] = "rectangle"
    n["styles"]["shape"] = {"desktop": {"shape": "original", "shapeLinked": True, "width": width, "gap": "", "height": ""}}
    n["styles"]["borderRadius"] = {"radiusType": "rounded", "btrr": radius, "bblr": radius, "bbrr": radius, "btlr": radius}
    n["styles"]["align"] = {"desktop": "center"}
    n["advanced"]["spacing-setting"] = {"edited": ["desktop"], "desktop": {"margin": {"bottom": mb}}, "tablet": {"margin": {"bottom": mb}}, "mobile": {"margin": {"bottom": mb}}}
    return n

ICONS = json.load(open(f"{S}/lib/icons.json"))
def icon(name, color=BRAND, size="40px", align="center"):
    n = mk("Icon")
    n["settings"]["iconSvg"] = ICONS[name]
    n["styles"]["globalSize"] = {"desktop": {"width": size, "padding": {"type": "custom"}, "isDropDownWidth": True}}
    n["styles"]["iconWidth"] = {"desktop": size}
    n["styles"]["color"] = {"normal": color}
    n["styles"]["align"] = {"desktop": align}
    return n

def checklist(items, color=BRAND, size=16, mb="0px"):
    n = mk("IconListV2")
    n["settings"]["childItem"] = [f"<p>{i}</p>" for i in items]
    n["settings"]["childConfig"] = [ICONS["check-circle-filled"]] * len(items)
    n["settings"]["iconSvg"] = ICONS["check-circle-filled"]
    n["settings"]["iconType"] = "matching"
    n["settings"]["iconWidth"] = {"desktop": 22}
    n["settings"]["textTypo"] = typo(size, "500", INK)
    n["styles"]["iconColor"] = color
    n["styles"]["position"] = {"desktop": "baseline", "tablet": "baseline", "mobile": "baseline"}
    n["styles"]["verticalSpacing"] = {"desktop": "8px"}
    n["styles"]["horizontalSpacing"] = {"desktop": "10px"}
    n["advanced"]["spacing-setting"] = {"edited": ["desktop"], "desktop": {"margin": {"bottom": mb}}, "tablet": {"margin": {"bottom": mb}}, "mobile": {"margin": {"bottom": mb}}}
    return n

def button(label, link="#buy", bg=BRAND, color="#ffffff", full=True, size=17, pad=("16px", "28px", "16px", "28px"), align="center", radius="12px", mb="0px"):
    n = mk("Button")
    n["settings"]["label"] = f"<p>{label}</p>"
    n["settings"]["enableBtnLink"] = True
    n["settings"]["btnLink"] = {"type": "scroll-to", "link": link, "target": "_self"}
    n["styles"]["backgroundColorV2"] = {"normal": bg, "hover": "#244a90"}
    n["styles"]["textColor"] = {"normal": color, "hover": color}
    n["styles"]["typo"] = typo(size, "700", color, "center")
    n["styles"]["align"] = {"desktop": align}
    n["styles"]["globalSize"] = {"desktop": {"width": "100%" if full else "auto", "height": "Auto", "padding": {"type": "custom", "top": pad[0], "right": pad[1], "bottom": pad[2], "left": pad[3]}}}
    n["styles"]["roundedBtnV2"] = {"normal": {"btrr": radius, "bblr": radius, "bbrr": radius, "btlr": radius, "radiusType": "custom"}}
    n["advanced"]["spacing-setting"] = {"desktop": {"margin": {"bottom": mb}}}
    return n

# ---------- product elements ----------
MAIN_PID = "gid://shopify/Product/15272587166060"; MAIN_HANDLE = "velahush-pet-odor-gun"
PODS_PID = "gid://shopify/Product/15272607285612"; PODS_HANDLE = "velahush-refill-pods-3-pack"

def product(cols, children_per_col, pid=MAIN_PID, handle=MAIN_HANDLE, status="dynamic", title="VelaHush™ Pet Odor Gun", gutter="12px", gap="4%", mobile_cols=None):
    n = mk("Product")
    n["settings"]["layout"] = {"desktop": {"cols": cols, "display": "fill"}, "mobile": {"cols": mobile_cols or [12], "display": "fill"}}
    n["settings"]["productSetting"] = {"productId": pid, "productHandle": handle, "productStatus": status, "productTitle": title, "hasPreSelected": True}
    n["settings"]["isSyncProduct"] = True
    n["styles"]["width"] = {"desktop": "default"}
    n["styles"]["verticalGutter"] = {"desktop": gutter}
    n["styles"]["verticalGutterMobile"] = {"desktop": gutter}
    n["styles"]["columnGap"] = {"desktop": gap}
    n["advanced"]["spacing-setting"] = {"desktop": {"margin": {"bottom": "0px"}}}
    n["advanced"]["d"] = {"desktop": True, "tablet": True, "mobile": True}
    n["childrens"] = [col(ch) for ch in children_per_col]
    return n

def product_images(position="bottom-center"):
    n = mk("ProductImagesV3")
    n["styles"]["position"] = {"desktop": position, "mobile": "bottom-center" if position != "only-feature" else "only-feature"}
    n["styles"]["ftCorner"] = {"btrr": "16px", "bblr": "16px", "bbrr": "16px", "btlr": "16px", "radiusType": "custom"}
    n["styles"]["corner"] = {"btrr": "8px", "bblr": "8px", "bbrr": "8px", "btlr": "8px", "radiusType": "custom"}
    n["styles"]["shapeForBottom"] = {"desktop": {"shape": "square", "shapeValue": "1/1", "width": "16.66%", "shapeLinked": True}}
    n["settings"]["ftNavigationPosition"] = {"desktop": "inside"}
    n["settings"]["ftDotStyle"] = {"desktop": "none", "mobile": "inside"}
    n["settings"]["ftClickOpenLightBox"] = {"desktop": "popup"}
    n["settings"]["priority"] = True
    n["advanced"]["spacing-setting"] = {"desktop": {"margin": {"bottom": "0px"}}}
    return n

def product_title(size=30, mobile=24):
    n = mk("ProductTitle")
    n["settings"]["htmlTag"] = "h1"
    n["styles"]["typo"] = {"type": "heading-2", "attrs": {"transform": "none", "color": INK}, "custom": {"fontSize": {"desktop": f"{size}px", "mobile": f"{mobile}px"}, "fontWeight": "800", "lineHeight": {"desktop": "1.2"}, "letterSpacing": {"desktop": "-0.02em"}, "fontFamily": FONT, "fontStyle": "normal"}}
    n["styles"]["hasLineClamp"] = {"desktop": False}
    n["styles"]["color"] = {"normal": INK}
    return n

def product_price(kind="regular", size=26, color=INK, weight="800", align="left"):
    n = mk("ProductPrice")
    n["settings"]["priceType"] = kind
    n["styles"]["typo"] = {"type": "subheading-2", "attrs": {"color": color}, "default": {"type": "subheading-2"}, "custom": {"fontSize": {"desktop": f"{size}px"}, "fontWeight": weight, "lineHeight": "1.2", "letterSpacing": {"desktop": "normal"}, "fontFamily": FONT, "fontStyle": "normal"}}
    n["styles"]["color"] = {"normal": color}
    n["styles"]["lineColor"] = color
    n["styles"]["textAlign"] = {"desktop": align}
    return n

def price_row(size=26, compare_size=18):
    r = row([12], [[]], display="fit", gutter="0px")
    r["settings"]["layout"] = {"desktop": {"cols": [6, 6], "display": "fit", "gap": "10px"}}
    r["settings"]["verticalAlign"] = {"desktop": "center"}
    r["childrens"] = [col([product_price("regular", size)]), col([product_price("compare", compare_size, MUTED, "500")])]
    return r

def product_button(label="Add to cart", layout="cart-price", size=18, pad="18px"):
    n = mk("ProductButton")
    n["settings"]["label"] = label
    n["settings"]["buttonLayout"] = layout
    n["settings"]["priceLayout"] = "price-only"
    n["settings"]["separator"] = "dot"
    n["settings"]["priceTypo"] = {"type": "paragraph-1", "attrs": {"color": "#ffffff"}, "custom": {"fontSize": {"desktop": f"{size}px"}, "fontWeight": "800", "lineHeight": "1.2", "letterSpacing": {"desktop": "normal"}, "fontFamily": FONT, "fontStyle": "normal"}}
    n["settings"]["compareAtPriceTypo"] = {"type": "paragraph-1", "attrs": {"color": "#ffffff"}}
    n["styles"]["enablePrice"] = layout != "cart-only"
    n["styles"]["enableSeparator"] = layout in ("cart-full", "cart-price-icon")
    n["styles"]["enableIcon"] = False
    n["styles"]["backgroundColorV2"] = {"normal": BRAND, "hover": "#244a90"}
    n["styles"]["textColor"] = {"normal": "#ffffff"}
    n["styles"]["typo"] = {"type": "paragraph-1", "attrs": {"color": "#ffffff"}, "custom": {"fontSize": {"desktop": f"{size}px"}, "fontWeight": "800", "lineHeight": "1.2", "letterSpacing": {"desktop": "normal"}, "fontFamily": FONT, "fontStyle": "normal"}}
    n["styles"]["roundedBtnV2"] = {"normal": {"btrr": "12px", "bblr": "12px", "bbrr": "12px", "btlr": "12px", "radiusType": "custom"}}
    n["styles"]["globalSize"] = {"desktop": {"width": "100%", "height": "Auto", "padding": {"type": "custom", "top": pad, "bottom": pad, "left": "24px", "right": "24px"}}}
    n["styles"]["align"] = {"desktop": "center"}
    return n

def product_variants(option_type="singleOption"):
    n = mk("ProductVariants")
    n["settings"]["optionType"] = option_type
    n["settings"]["label"] = True
    n["settings"]["price"] = True
    n["settings"]["showAsSwatches"] = True
    n["settings"]["hasPreSelected"] = True
    n["settings"]["layout"] = {"desktop": "vertical"}
    n["settings"]["variantPresets"] = [{"optionName": "base", "optionType": "rectangle_list", "presets": {
        "color": {"width": {"desktop": "45px"}, "height": "45px", "spacing": "8px"},
        "rectangle_list": {"width": {"desktop": ""}, "height": "52px", "spacing": "10px"},
        "image": {"width": {"desktop": "64px"}, "height": "64px", "spacing": "8px"},
        "image_shopify": {"width": {"desktop": "64px"}, "height": "64px", "spacing": "8px"},
        "dropdown": {"width": {"desktop": "100%"}, "height": "45px"}}}]
    n["styles"]["optionSpacing"] = "18px"
    n["styles"]["labelGap"] = "8px"
    n["styles"]["swatchHeight"] = {"desktop": "52px"}
    n["styles"]["swatchSpacing"] = "10px"
    n["styles"]["marginBottom"] = {"desktop": "0px"}
    n["styles"]["labelTypo"] = typo(14, "700", INK, transform="uppercase", ls="0.08em")
    n["styles"]["labelColor"] = INK
    n["styles"]["optionTypo"] = typo(15, "600", INK)
    n["styles"]["optionBgColor"] = {"normal": "#ffffff", "hover": "#ffffff", "active": BRAND_LIGHT}
    n["styles"]["optionTextColor"] = {"normal": INK, "hover": INK, "active": BRAND}
    n["styles"]["optionBorder"] = {
        "normal": {"borderType": "style-2", "border": "solid", "color": "#d9d6d6", "isCustom": True, "width": "1px 1px 1px 1px", "borderWidth": "1px"},
        "hover": {"borderType": "style-3", "border": "solid", "color": BRAND, "isCustom": True, "width": "1px 1px 1px 1px", "borderWidth": "1px"},
        "active": {"borderType": "style-3", "border": "solid", "color": BRAND, "isCustom": True, "width": "2px 2px 2px 2px", "borderWidth": "2px"}}
    n["styles"]["optionRounded"] = {"normal": {"btrr": "12px", "bblr": "12px", "bbrr": "12px", "btlr": "12px", "radiusType": "custom"}}
    n["advanced"]["spacing-setting"] = {"desktop": {"margin": {"bottom": "0px"}}}
    n["advanced"]["d"] = {"desktop": True, "tablet": True, "mobile": True}
    n["styles"]["width"] = {"desktop": "100%"}
    n["styles"]["fullWidth"] = {"desktop": True}
    n["styles"]["swatchWidth"] = {"desktop": "auto"}
    n["settings"]["combineWidth"] = {"desktop": "100%"}
    return n

# ---------- helpers for common blocks ----------
def eyebrow(t, align="left", color=BRAND): return text(t, 12, "700", color, align, "1.6", "uppercase", "0.14em")
def benefit_tile(icon_name, label):
    inner = row([12], [[icon(icon_name, BRAND, "44px"), text(label, 14, "600", BRAND, "center", "1.35")]],
                bg="#ffffff", pad=("18px", "8px", "16px", "8px"), radius="28px", border=("1.5px", BRAND), gutter="10px", width="100%")
    return inner

def strip_bar(t):
    r = row([12], [[text(t, 15, "800", "#ffffff", "left", "1.3", "uppercase", "0.04em")]], bg=BRAND, pad=("14px", "18px", "14px", "18px"), gutter="0px", width="100%")
    return r

# =====================================================================
# SECTION 1 — HERO BUY BOX
# =====================================================================
def s_hero():
    left = [product_images("bottom-center")]
    urgency = row([12], [[text(f'<p><span style="color:{RED}"><strong>LAUNCH OFFER:</strong></span> the <strong>Gun + 3 refill pods</strong> bundle is <span style="color:{RED}"><strong>$10.10 off</strong></span> while launch stock lasts. One-time purchase, pods are never on subscription.</p>', 15, "500", INK, "left", "1.5")]],
                  bg=CREAM, pad=("14px", "18px", "14px", "18px"), radius="12px", gutter="0px", width="100%")
    tiles = row([3, 3, 3, 3], [[benefit_tile("timer-bold", "Neutralizes<br>Odor Fast")],
                               [benefit_tile("drop-bold", "Reaches Deep<br>Fabric Fibers")],
                               [benefit_tile("car-bold", "Freshens Cars<br>&amp; Couches")],
                               [benefit_tile("paw-print-bold", "Safe Around<br>Pets &amp; Kids")]],
                mobile_cols=[6, 6], gutter="10px", gap="10px", width="100%")
    # add-on refill pods (its own Product context, static)
    addon_left = [text("<p><strong>+ Add refill pods, 3 pack</strong></p>", 16, "800", INK),
                  text("About two months of weekly use. No subscription, we email you before you run out.", 13, "400", MUTED, "left", "1.45"),
                  product_variants("singleOption")]
    addon_right = [price_row(22, 15), product_button("Add pods", "cart-only", 15, "12px")]
    addon_prod = product([8, 4], [addon_left, addon_right], pid=PODS_PID, handle=PODS_HANDLE, status="static", title="VelaHush Refill Pods, 3 Pack", gutter="8px", gap="3%", mobile_cols=[12])
    addon_prod["styles"]["width"] = {"desktop": "100%"}
    addon = row([12], [[addon_prod]], bg=BRAND_LIGHT, pad=("16px", "16px", "16px", "16px"), radius="12px", gutter="0px", width="100%", border=("1px", "#cbd7ee"))
    right = [
        text(f'<p><span style="color:{BRAND}">★★★★★</span> &nbsp;30-day money back · 90-day warranty · Ships from California</p>', 13, "600", MUTED, "left", "1.5"),
        product_title(),
        text("A cordless dry-mist gun that neutralizes pet odor <strong>inside</strong> your couch cushions, rugs and car seats, so the room smells like nothing at all, not like a candle trying to hide something.", 16, "400", INK, "left", "1.55"),
        checklist(["Neutralizes odor inside the fabric, not perfume sprayed over it",
                   "Dry mist: no soaked cushions, no wiping, sit down a minute later",
                   "Cordless and rechargeable, no cord to drag around the room",
                   "Works with our pods or any water-based enzyme cleaner"]),
        heading("The Complete Solution For Eliminating Pet Odor", 20, "800", INK, "center", "1.3", "h3", "4px", 18),
        tiles,
        urgency,
        text("Pick your setup, every gun ships with a pod", 13, "700", MUTED, "center", "1.4", "uppercase", "0.12em"),
        product_variants("singleOption"),
        addon,
        strip_bar("+ Free US shipping over $50"),
        strip_bar("+ 30-day money back, keep the pods"),
        product_button("Add to cart", "cart-price", 18, "18px"),
        text("Visa · Mastercard · Amex · PayPal · Apple Pay · Shop Pay · Klarna", 12, "600", MUTED, "center", "1.5", "none", "0.02em"),
    ]
    prod = product([6, 6], [left, right], gutter="12px", gap="4%")
    prod["uid"] = "gBuyBoxPrd"  # stable anchor for scroll-to buttons
    sec = section([container([prod], gutter="0px")], bg="#ffffff", pad=("32px", "48px"))
    sec["uid"] = "gBuyBoxSec"
    return sec

# =====================================================================
# SECTION — problem (nose blindness) with real image
# =====================================================================
def s_problem():
    left = [image("before_after", "Before and after: the whole couch treated, not one spot")]
    right = [eyebrow("The moment nobody talks about"),
             heading("You stopped smelling it.<br>Your guests didn't.", 36, "800", INK, "left", "1.15", "h2", "8px", 28),
             text("Here's the unfair part: you go nose-blind to your own home in about a week. So the sofa, the rug, the throw blanket your dog claims, they keep getting stronger, and you're the last person to know.", 17, "400", INK, "left", "1.6"),
             text("Candles and plug-ins don't fix that. They add perfume on top and wear off by dinner. VelaHush sends a dry neutralizing mist <strong>into the fibers</strong> where the odor actually sits, so there's nothing left to cover up, and nothing for anyone to notice.", 17, "400", INK, "left", "1.6"),
             button("Fix the smell, not the air →", "#gBuyBoxSec", full=False, align="left")]
    r = row([6, 6], [left, right], gutter="14px", gap="5%", width="1200px", align_v="center")
    r["styles"]["align"] = {"desktop": "center"}
    return section([r], bg=PAPER)

def s_why_mist():
    left = [eyebrow("Why a mist reaches what a spray cannot"),
            heading("The difference is droplet size. That is the entire product.", 34, "800", INK, "left", "1.15", "h2", "8px", 26),
            text("A hand trigger throws large droplets. They land on top of the weave, pool where they hit, and soak into one patch. That is why you get a dark ring instead of an evenly treated cushion, and why you stop after four squeezes.", 17, "400", INK, "left", "1.6"),
            text("A powered nozzle breaks the same liquid into droplets small enough to drift down into the gaps between fibers, and light enough that the fabric never saturates. <strong>Same solution. Different delivery. That is what changes the result.</strong>", 17, "400", INK, "left", "1.6"),
            checklist(["One fill covers the whole couch, seat backs and arms included", "Dries in minutes, no wet rings to explain to anyone", "Then the rug, then the dog bed, then the car"])]
    right = [image("droplets", "Fine dry mist droplets reaching between fabric fibers")]
    r = row([6, 6], [left, right], gutter="14px", gap="5%", width="1200px", align_v="center")
    r["styles"]["align"] = {"desktop": "center"}
    return section([r], bg="#ffffff")

def s_infographics():
    head = [eyebrow("Why pet owners are switching", "center"),
            heading("Everything a trigger bottle can't do", 36, "800", INK, "center", "1.15", "h2", "8px", 28)]
    grid = row([6, 6], [[image("five", "Five reasons pet owners choose VelaHush"), image("struggle", "No more struggling with trigger spray bottles")],
                        [image("percent", "VelaHush results graphic"), image("results", "VelaHush customer results")]],
               gutter="16px", gap="16px", width="1200px")
    grid["styles"]["align"] = {"desktop": "center"}
    grid2 = row([12], [[image("ultimate", "VelaHush, the ultimate pet odor solution")]], width="1200px")
    grid2["styles"]["align"] = {"desktop": "center"}
    return section([container(head, gutter="8px"), grid, grid2], bg=PAPER, gutter="24px")

def s_final_cta():
    inner = [eyebrow("Thirty days to decide", "center", "#ffffff"),
             heading("The bottle under your sink is not the problem.", 36, "800", "#ffffff", "center", "1.15", "h2", "8px", 28),
             text("It never was. It just cannot reach a whole room, and a whole room is what actually smells. Pick a setup, fill it with whatever you already trust, and run the three tests yourself. You have thirty days to decide whether we were right.", 17, "400", "#ffffff", "center", "1.6"),
             button("Get VelaHush — from $49", "#gBuyBoxSec", bg="#ffffff", color=BRAND, full=False, align="center"),
             text("30-day money back · 90-day warranty · Free US shipping over $50", 13, "600", "#ffffff", "center", "1.5")]
    box = row([12], [inner], bg=BRAND, pad=("56px", "32px", "56px", "32px"), radius="24px", gutter="16px", width="1200px")
    box["styles"]["align"] = {"desktop": "center"}
    return section([box], bg="#ffffff")

# =====================================================================
# STICKY ADD TO CART (root = Sticky)
# =====================================================================
def s_sticky():
    left = [product_title(16, 15), price_row(18, 13)]
    left[0]["styles"]["hasLineClamp"] = {"desktop": True}; left[0]["styles"]["lineClamp"] = {"desktop": 1}
    right = [product_button("Add to cart", "cart-price", 15, "12px")]
    prod = product([7, 5], [left, right], gutter="4px", gap="3%", mobile_cols=[6, 6])
    prod["settings"]["verticalAlign"] = {"desktop": "center"}
    inner = row([12], [[prod]], width="1200px", pad=("10px", "0px", "10px", "0px"), gutter="0px")
    inner["styles"]["align"] = {"desktop": "center"}
    st = mk("Sticky")
    st["settings"]["position"] = {"desktop": "bottom"}
    st["settings"]["background"] = {"desktop": {"type": "color", "color": "#ffffff", "image": {"src": "", "width": 0, "height": 0}, "size": "cover", "position": {"x": 50, "y": 50}, "repeat": "no-repeat", "attachment": "scroll"}}
    st["settings"]["display"] = {"desktop": "always"}
    st["settings"]["isScrollToTop"] = False
    st["childrens"] = [col([inner])]
    return st

# =====================================================================
# COPIES of existing sections (re-uid'd, placeholders replaced by images)
# =====================================================================
def reuid(n):
    n["uid"] = uid()
    for c in n.get("childrens", []) or []: reuid(c)
    return n

def replace_placeholder(root, needle, img_key, alt):
    """Replace a Text placeholder ('photo: ...') by an Image element in place."""
    def walk(n):
        ch = n.get("childrens", []) or []
        for i, c in enumerate(ch):
            if c["tag"] == "Text" and needle in (c["settings"].get("text") or ""):
                ch[i] = image(img_key, alt, radius="16px"); return True
            if walk(c): return True
        return False
    ok = walk(root)
    assert ok, f"placeholder {needle!r} not found"

def copy_section(name, fixes=()):
    c = copy.deepcopy(load(name)["component"])
    for needle, key, alt in fixes: replace_placeholder(c, needle, key, alt)
    return reuid(c)

def build_all():
    random.seed(20260906)
    out = []
    out.append(("Hero buy box", s_hero()))
    out.append(("Trust marquee", copy_section("trust-marquee")))
    out.append(("Problem: nose blind", s_problem()))
    out.append(("How it works", copy_section("how-it-works", [
        ("hand clicking pod", "triple", "Step 1: click a refill pod into the VelaHush gun"),
        ("sweeping motion", "six", "Step 2: sweep the dry mist over cushions, rugs and car seats"),
        ("clean living room", "relief", "Step 3: walk away, it dries in seconds")])))
    out.append(("Why a mist", s_why_mist()))
    out.append(("Infographics", s_infographics()))
    out.append(("Three tests", copy_section("three-tests")))
    out.append(("Refills", copy_section("refills", [("photo: refill scent oil", "collage", "VelaHush refill pods in four scents")])))
    out.append(("Poster band", copy_section("poster-band")))
    out.append(("Comparison table", copy_section("comparison-table")))
    out.append(("What it is not", copy_section("what-it-is-not")))
    out.append(("Guarantee", copy_section("guarantee-and-warranty")))
    out.append(("FAQ", copy_section("faq")))
    out.append(("Final CTA", s_final_cta()))
    out.append(("Sticky add to cart", s_sticky()))
    # fix scroll anchors: buttons that point to '#how' etc in copied sections -> buy box
    def fix_links(n):
        s = n.get("settings", {})
        if n["tag"] == "Button" and isinstance(s.get("btnLink"), dict) and s["btnLink"].get("type") == "scroll-to":
            s["btnLink"]["link"] = "#gBuyBoxSec"
        for c in n.get("childrens", []) or []: fix_links(c)
    for _, sec in out: fix_links(sec)
    os.makedirs(f"{S}/build", exist_ok=True)
    for i, (name, sec) in enumerate(out, 1):
        json.dump(sec, open(f"{S}/build/{i:02d}.json", "w"))
    json.dump([{"order": i, "name": n, "file": f"{i:02d}.json"} for i, (n, _) in enumerate(out, 1)], open(f"{S}/build/index.json", "w"), indent=1)
    for i, (n, sec) in enumerate(out, 1):
        print(i, n, sec["tag"], len(json.dumps(sec)))

if __name__ == "__main__":
    build_all()
