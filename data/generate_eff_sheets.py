# generate_eff_sheet.py
# Requires: pip install pandas

import math
import re
import sys
import itertools
import unicodedata
import pandas as pd


# --------- CONFIG ----------
# If you don't pass a path in command line, set it here:
INPUT_CSV = "fighters.csv"

# Output path (auto if empty)
OUTPUT_CSV = ""  # e.g. "computed_sheet.csv"

# Typo tolerance for fusion member matching (edit distance).
# 1 is enough to match "goh0n" -> "gohan" after 0->o normalization.
MAX_EDIT_DISTANCE = 1
# --------------------------


def normalize(s: str) -> str:
    """Lowercase, remove accents, replace 0->o, keep alnum/spaces, collapse spaces."""
    if s is None:
        return ""
    s = str(s).replace("0", "o")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def edit_distance(a: str, b: str) -> int:
    """Levenshtein distance (small + fast enough for this dataset)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    # DP with rolling rows
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            ins = cur[j - 1] + 1
            dele = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            cur.append(min(ins, dele, sub))
        prev = cur
    return prev[-1]


def best_previous_form_name(df: pd.DataFrame, prev_raw: str) -> str | None:
    """
    Resolve previous_form to an actual row name.
    - If exact match exists => use it
    - Else substring match on normalized names
    - Else (fallback) fuzzy match with edit distance on name tokens
    Choose the lowest form_level then lowest cost.
    """
    if prev_raw is None or (isinstance(prev_raw, float) and math.isnan(prev_raw)):
        return None

    prev_raw = str(prev_raw).strip()
    if prev_raw in set(df["name"]):
        return prev_raw

    p = normalize(prev_raw)
    if not p:
        return None

    # substring candidates
    cand = df[df["_norm_name"].str.contains(re.escape(p), na=False)]
    if not cand.empty:
        cand = cand.sort_values(["form_level", "cost"], ascending=[True, True])
        return cand.iloc[0]["name"]

    # fuzzy token match fallback
    best = None
    best_key = None  # (distance, form_level, cost)
    for _, r in df.iterrows():
        tokens = r["_norm_name"].split()
        d = min(edit_distance(p, t) for t in tokens) if tokens else edit_distance(p, r["_norm_name"])
        if d <= MAX_EDIT_DISTANCE:
            key = (d, int(r["form_level"]), float(r["cost"]))
            if best is None or key < best_key:
                best = r["name"]
                best_key = key
    return best


def member_candidates(df: pd.DataFrame, pattern_raw: str, min_form_level: int) -> list[str]:
    """
    Fusion member matching:
    - First try substring on normalized names
    - If none, try fuzzy token match (<= MAX_EDIT_DISTANCE)
    Return list of candidate row names with form_level >= min_form_level
    """
    p = normalize(pattern_raw)
    if not p:
        return []

    c1 = df[(df["form_level"] >= min_form_level) & (df["_norm_name"].str.contains(re.escape(p), na=False))]
    if not c1.empty:
        return c1["name"].tolist()

    # fuzzy token match
    out = []
    for _, r in df[df["form_level"] >= min_form_level].iterrows():
        tokens = r["_norm_name"].split()
        d = min(edit_distance(p, t) for t in tokens) if tokens else edit_distance(p, r["_norm_name"])
        if d <= MAX_EDIT_DISTANCE:
            out.append(r["name"])
    return out


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else INPUT_CSV
    df = pd.read_csv(csv_path)

    # Basic cleaning / defaults
    df["form_level"] = df["form_level"].fillna(0).astype(int)
    df["cost"] = df["cost"].fillna(0).astype(float)
    df["health"] = df["health"].fillna(0).astype(float)
    df["attack_power"] = df["attack_power"].fillna(0).astype(float)

    df["_norm_name"] = df["name"].map(normalize)

    # Row lookup
    rows_by_name = {r["name"]: r for _, r in df.iterrows()}

    # Memoization with manual dict (avoid recursion issues with pandas objects)
    memo: dict[str, float] = {}
    visiting: set[str] = set()

    def eff_cost(name: str) -> float:
        """
        Minimal effective cost to have THIS exact row active from scratch
        given the rules you described.
        """
        if name in memo:
            return memo[name]
        if name in visiting:
            # Cycle guard (shouldn't normally happen, but prevents infinite recursion)
            return math.inf
        visiting.add(name)

        r = rows_by_name.get(name)
        if r is None:
            visiting.remove(name)
            memo[name] = math.inf
            return math.inf

        is_fusion = not pd.isna(r.get("fusion_members"))
        L = int(r["form_level"])

        best = math.inf

        if not is_fusion:
            # Non-fusion
            if L == 0:
                best = float(r["cost"])
            else:
                base_name = best_previous_form_name(df, r.get("previous_form"))
                if base_name is not None:
                    base_cost = eff_cost(base_name)
                    if math.isfinite(base_cost):
                        best = base_cost + float(r["cost"])
        else:
            # Fusion
            members_raw = str(r["fusion_members"])
            members = [m.strip() for m in members_raw.split(";") if m.strip()]

            # Route 1: fuse directly into this form for free,
            # if every member can be at form_level >= L
            per_member_lists = []
            for pat in members:
                per_member_lists.append(member_candidates(df, pat, min_form_level=L))

            direct = math.inf
            if members and all(per_member_lists):
                # cartesian product over choices
                for combo in itertools.product(*per_member_lists):
                    # members must be distinct rows
                    if len(set(combo)) < len(combo):
                        continue
                    s = 0.0
                    ok = True
                    for n in combo:
                        c = eff_cost(n)
                        if not math.isfinite(c):
                            ok = False
                            break
                        s += c
                    if ok and s < direct:
                        direct = s

            best = min(best, direct)

            # Route 2: transform from previous fusion form (if it exists)
            prev_name = best_previous_form_name(df, r.get("previous_form"))
            if prev_name is not None:
                prev_cost = eff_cost(prev_name)
                if math.isfinite(prev_cost):
                    best = min(best, prev_cost + float(r["cost"]))

        visiting.remove(name)
        memo[name] = best
        return best

    # Build the requested sheet
    out = pd.DataFrame({
        "name": df["name"],
        "health": df["health"].astype(int),
        "attack": df["attack_power"].astype(int),
        "form_level": df["form_level"].astype(int),
        "fusion": df["fusion_members"].notna(),
    })

    eff_list = []
    for n in out["name"].tolist():
        v = eff_cost(n)
        eff_list.append(v if math.isfinite(v) else float("nan"))
    out["eff_cost"] = eff_list

    total = (df["health"] + df["attack_power"]).astype(float)
    out["total_per_eff"] = total / out["eff_cost"]
    out.loc[out["eff_cost"].isna() | (out["eff_cost"] <= 0), "total_per_eff"] = float("nan")

    # Reorder columns exactly as you asked
    out = out[["name", "total_per_eff", "eff_cost", "health", "attack", "form_level", "fusion"]]

    # Save
    out_path = OUTPUT_CSV.strip() or (csv_path.rsplit(".", 1)[0] + "_computed_sheet.csv")
    out.to_csv(out_path, index=False)

    # Small terminal preview
    print(f"Saved: {out_path}")
    print(out.sort_values(["eff_cost", "name"]).head(20).to_string(index=False))


if __name__ == "__main__":
    main()
