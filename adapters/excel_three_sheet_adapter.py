import os
import time
from typing import Optional, Dict, Any, List

# Cache-busting version identifier - update when making changes
ADAPTER_VERSION = f"v2.1.0-{int(time.time())}"


def _as_pct(x):
    try:
        if x is None:
            return None
        s = str(x).strip()
        if s == "":
            return None
        v = float(s)
        return v / 100.0 if v > 1 else v
    except Exception:
        return None


def _norm_gross_net(x: Optional[str]) -> str:
    s = str(x or "").strip().lower()
    return "net" if s.startswith("n") else "gross"


def _class_from_fund(fund: Optional[str]) -> str:
    s = str(fund or "").lower()
    if "pro" in s:
        return "professional"
    if "retail" in s:
        return "retail"
    return "retail"


class ExcelLocalThreeSheet:
    """Minimal local Excel adapter for FeeSheet, InvestorSheet, CompanySheet.

    Reads a single Excel workbook with three sheets and resolves a merged payload
    suitable for the fee letter generator.
    """

    def __init__(self, path: Optional[str] = None):
        self.path = path or os.getenv("EXCEL_PATH")
        if not self.path:
            raise ValueError("EXCEL_PATH is not set. Please set the environment variable to the Excel file path.")

        try:
            import pandas as pd  # lazy import here
        except Exception as e:
            raise ImportError("pandas is required for Excel adapter. Please `pip install pandas openpyxl rapidfuzz`." ) from e

        self._pd = pd
        try:
            xls = pd.ExcelFile(self.path, engine="openpyxl")
            available = [str(s).strip() for s in xls.sheet_names]
            def pick(candidates):
                # case/space insensitive pick
                canon = {s.lower().replace(" ", ""): s for s in available}
                for c in candidates:
                    key = c.lower().replace(" ", "")
                    if key in canon:
                        return canon[key]
                return None
            fee_name = pick(["FeeSheet", "Fees", "Fee Sheet", "Fee_Data", "FeeData"]) or "FeeSheet"
            inv_name = pick(["InvestorSheet", "Investors", "InvestorData", "Investor Data"]) or "InvestorSheet"
            co_name  = pick(["CompanySheet", "Companies", "CompanyData", "Company Data"]) or "CompanySheet"
            self.fees = pd.read_excel(self.path, sheet_name=fee_name, engine="openpyxl")
            self.inv  = pd.read_excel(self.path, sheet_name=inv_name,  engine="openpyxl")
            self.cos  = pd.read_excel(self.path, sheet_name=co_name,   engine="openpyxl")
        except Exception as e:
            raise ValueError(f"Failed to read Excel at {self.path}: {e}")

        # Normalize headers: strip and canonicalize common variants (case-insensitive)
        def _canonize(df, mapping):
            norm_cols = {}
            for c in df.columns:
                key = str(c).strip().lower()
                canon = mapping.get(key)
                if canon:
                    norm_cols[c] = canon
            df.rename(columns=norm_cols, inplace=True)
            df.columns = [str(c).strip() for c in df.columns]

        # Attempt to auto-detect header rows if expected columns are missing (common when files have top banners)
        def _ensure_headers(df, expected_keywords):
            cols_lower = [str(c).strip().lower() for c in df.columns]
            # Heuristic: if columns look like generic names or expected keywords missing, try to find header row in first 10 rows
            generic = all(c.startswith("unnamed") or c.startswith("column") for c in cols_lower)
            missing = not any(ek in cols_lower for ek in expected_keywords)
            if generic or missing:
                try:
                    # search first 10 rows for a row that contains any expected keyword
                    max_rows = min(10, len(df))
                    for i in range(max_rows):
                        row_vals = [str(v).strip() for v in df.iloc[i].tolist()]
                        row_lower = [v.lower() for v in row_vals]
                        if any(ek in row_lower for ek in expected_keywords):
                            df.columns = row_vals
                            df.drop(index=list(range(i+1)), inplace=True)
                            # reset index
                            df.reset_index(drop=True, inplace=True)
                            return df
                except Exception:
                    return df
            return df

        # Apply header fixes first
        self.inv = _ensure_headers(self.inv, expected_keywords=["first name", "last name", "custodian client ref", "contact email"])
        self.fees = _ensure_headers(self.fees, expected_keywords=["custodian client ref", "subscription code", "gross/net", "fund"])
        self.cos = _ensure_headers(self.cos, expected_keywords=["company name", "current share price"]) 

        # Apply canonical mappings per sheet
        fee_map = {
            "custodian client ref": "Custodian Client Ref",
            "subscription code": "Subscription code",
            "subscription_code": "Subscription code",
            "fund": "Fund",
            "gross/net": "Gross/Net",
            "grossnet": "Gross/Net",
            "cc set up fee %": "CC Set up fee %",
            "cc setup fee %": "CC Set up fee %",
            "cc amc %": "CC AMC %",
            "cc carry %": "CC Carry %",
            "deposit #": "Deposit #",
            "deposit number": "Deposit #",
            "initial deposit date/reinvestment instruction date": "Initial Deposit date/Reinvestment instruction date",
        }
        inv_map = {
            "custodian client ref": "Custodian Client Ref",
            "account name": "Account Name",
            "salutation": "Salutation",
            "first name": "First Name",
            "last name": "Last Name",
            "contact email": "Contact email",
            "contact email address": "Contact email",
            "login email": "Login Email",
        }
        co_map = {
            "company name": "Company Name",
            "current share price": "Current Share Price",
            "company number": "Company Number",
            "share class": "Share Class",
        }

        _canonize(self.fees, fee_map)
        _canonize(self.inv, inv_map)
        _canonize(self.cos, co_map)

        # Resolve flexible column names for CompanySheet to handle slight header variations
        import re as _re

        def _norm_hdr(x: str) -> str:
            return _re.sub(r"[^a-z0-9]", "", str(x).strip().lower())

        def _pick_col(cols, preferred: list, must_contain_all: list = None):
            norm_map = {c: _norm_hdr(c) for c in cols}
            # 1) exact preferred keys
            for p in preferred:
                p_norm = _norm_hdr(p)
                for c, n in norm_map.items():
                    if n == p_norm:
                        return c
            # 2) contains all tokens
            if must_contain_all:
                tokens = [_norm_hdr(t) for t in must_contain_all]
                for c, n in norm_map.items():
                    if all(t in n for t in tokens):
                        return c
            # 3) best-effort: any header containing the first token
            if must_contain_all:
                t0 = _norm_hdr(must_contain_all[0])
                for c, n in norm_map.items():
                    if t0 in n:
                        return c
            return preferred[0] if preferred else next(iter(cols), None)

        # Cache detected column names for later use
        self._co_company_name_col = _pick_col(
            self.cos.columns,
            preferred=["Company Name"],
            must_contain_all=["company", "name"],
        )
        self._co_share_price_col = _pick_col(
            self.cos.columns,
            preferred=["Current Share Price"],
            must_contain_all=["share", "price"],
        )
        self._co_company_number_col = _pick_col(
            self.cos.columns,
            preferred=["Company Number"],
            must_contain_all=["company", "number"],
        )
        self._co_share_class_col = _pick_col(
            self.cos.columns,
            preferred=["Share Class"],
            must_contain_all=["share", "class"],
        )

        # Precompute full name for fuzzy
        self.inv["__full__"] = (
            self.inv.get("First Name", "").astype(str).str.strip()
            + " "
            + self.inv.get("Last Name", "").astype(str).str.strip()
        ).str.strip()

        # rapidfuzz optional
        try:
            from rapidfuzz import process, fuzz  # type: ignore
            self._rf_process = process
            self._rf_scorer = fuzz.WRatio
        except Exception:
            self._rf_process = None
            self._rf_scorer = None

    def _fuzzy_one(self, query: str, choices: list):
        if not self._rf_process:
            return None
        hit = self._rf_process.extractOne(query, choices, scorer=self._rf_scorer)
        return hit

    def find_investor_row(self, investor_query: str) -> Optional[Dict[str, Any]]:
        s = str(investor_query or "").strip().lower()
        
        # email exact
        if "@" in s and "Contact email" in self.inv.columns:
            m = self.inv[self.inv["Contact email"].astype(str).str.lower() == s]
            if not m.empty:
                return m.iloc[0].to_dict()

        # Custodian Client Ref exact
        if "Custodian Client Ref" in self.inv.columns:
            m = self.inv[self.inv["Custodian Client Ref"].astype(str).str.strip().str.lower() == s]
            if not m.empty:
                return m.iloc[0].to_dict()

        # Compressed exact/contains (remove spaces/punct) then fuzzy by full name then Account Name
        def _compress(x: str) -> str:
            import re
            return re.sub(r"[^a-z0-9]", "", str(x).lower())

        s_comp = _compress(s)
        if "__full__" in self.inv.columns:
            comp_col = self.inv["__full__"].astype(str).apply(_compress)
            
            # Try exact match first
            m = self.inv[comp_col == s_comp]
            if not m.empty:
                return m.iloc[0].to_dict()
            
            # Check for ambiguous partial matches (SAFETY CHECK)
            m = self.inv[comp_col.str.contains(s_comp, na=False)]
            if len(m) > 1:
                # Multiple matches found - this is dangerous!
                matches = []
                for _, row in m.iterrows():
                    full_name = row.get("__full__", row.get("Investor Name", "Unknown"))
                    matches.append(str(full_name))
                
                raise ValueError(f"Ambiguous investor name '{investor_query}'. Multiple matches found: {', '.join(matches[:5])}{'...' if len(matches) > 5 else ''}. Please provide a more specific name.")
            
            if not m.empty:
                return m.iloc[0].to_dict()

        # Try fuzzy matching with safety checks
        for col in ["__full__", "Account Name"]:
            if col not in self.inv.columns:
                continue
            
            # Get all potential fuzzy matches above threshold
            choices = self.inv[col].astype(str).tolist()
            if not choices:
                continue
                
            # Check for multiple high-confidence matches
            import rapidfuzz
            matches = rapidfuzz.process.extract(investor_query, choices, limit=5, scorer=rapidfuzz.fuzz.ratio)
            high_matches = [m for m in matches if m[1] >= 75]
            
            if len(high_matches) > 1:
                # Multiple high-confidence matches - ambiguous
                match_names = [m[0] for m in high_matches]
                raise ValueError(f"Ambiguous investor name '{investor_query}'. Multiple similar matches found: {', '.join(match_names)}. Please provide a more specific name.")
            
            # Single high-confidence match is safe
            if high_matches:
                hit = high_matches[0]
                idx = choices.index(hit[0])
                return self.inv.iloc[idx].to_dict()
                
        return None

    def find_fee_row(self, cust_ref: str, subscription_code: Optional[str] = None, investor_full_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if "Custodian Client Ref" not in self.fees.columns:
            return None
        rhs = str(cust_ref or "").strip().lower()
        df = self.fees[
            self.fees["Custodian Client Ref"].astype(str).str.strip().str.lower() == rhs
        ]
        # Fallback: link by investor full name when Custodian Client Ref does not match
        if df.empty and investor_full_name and "Investor name" in self.fees.columns:
            full = str(investor_full_name).strip()
            import re
            def _compress(x: str) -> str:
                return re.sub(r"[^a-z0-9]", "", str(x).lower())
            target = _compress(full)
            # Try exact/contains on compressed
            inv_col = self.fees["Investor name"].astype(str)
            comp = inv_col.map(_compress)
            df = self.fees[comp == target]
            if df.empty:
                df = self.fees[comp.str.contains(target, na=False)]
            # Try reversed name order
            if df.empty:
                parts = [p for p in re.split(r"\s+", full.strip()) if p]
                if len(parts) >= 2:
                    rev_target = _compress(" ".join(parts[::-1]))
                    df = self.fees[comp == rev_target]
                    if df.empty:
                        df = self.fees[comp.str.contains(rev_target, na=False)]
            # Try token inclusion (both first and last present in any order)
            if df.empty and len(parts) >= 2:
                f_tok = parts[0].lower()
                l_tok = parts[-1].lower()
                mask = inv_col.str.lower().str.contains(f_tok, na=False) & inv_col.str.lower().str.contains(l_tok, na=False)
                df = self.fees[mask]
            # DISABLED: Fuzzy matching is too dangerous for investor data
            # Risk of matching wrong investors (e.g., Alan Fox -> Alan Hickford)
            if df.empty and self._rf_process is not None:
                choices = inv_col.astype(str).tolist()
                hit = self._rf_process.extractOne(full, choices, scorer=self._rf_scorer)
                if hit:
                    print(f"⚠️  DISABLED fuzzy match for safety: '{full}' -> '{hit[0]}' (similarity: {hit[1]}%) - fuzzy matching disabled to prevent wrong investor data")
        if df.empty:
            return None
        # Some workbooks store ref as integer; ensure string compare on both sides already above
        if subscription_code is not None and "Subscription code" in self.fees.columns:
            rhs_sub = str(subscription_code).strip().lower()
            sub = df[
                df["Subscription code"].astype(str).str.strip().str.lower() == rhs_sub
            ]
            if not sub.empty:
                df = sub
        # Sort by date desc then Deposit # desc when present
        dt_col = "Initial Deposit date/Reinvestment instruction date"
        if dt_col in df.columns:
            with self._pd.option_context('mode.chained_assignment', None):
                df["_dt"] = self._pd.to_datetime(df[dt_col], errors="coerce")
            df = df.sort_values(by=["_dt", "Deposit #"], ascending=[False, False], na_position="last")
        elif "Deposit #" in df.columns:
            df = df.sort_values(by=["Deposit #"], ascending=False)
        return df.iloc[0].to_dict()

    def find_company_row(self, company_query: str) -> Optional[Dict[str, Any]]:
        name_col = getattr(self, "_co_company_name_col", None)
        if not name_col or name_col not in self.cos.columns:
            return None
        s = str(company_query or "").strip().lower()
        # direct exact match
        m = self.cos[self.cos[name_col].astype(str).str.strip().str.lower() == s]
        if not m.empty:
            return m.iloc[0].to_dict()
        # contains
        m = self.cos[self.cos[name_col].astype(str).str.lower().str.contains(s, na=False)]
        if not m.empty:
            return m.iloc[0].to_dict()
        # normalized comparison (remove legal suffixes)
        def _norm(n: str) -> str:
            x = str(n or "").lower().strip()
            for suf in [" limited", " ltd.", " ltd", " plc", " llp", " inc.", " inc", " corp.", " corp", " co.", " company"]:
                if x.endswith(suf):
                    x = x[: -len(suf)]
                    break
            x = " ".join(x.split())
            return x
        s_norm = _norm(company_query)
        self.cos["__norm__"] = self.cos[name_col].astype(str).map(_norm)
        m = self.cos[self.cos["__norm__"] == s_norm]
        if not m.empty:
            return m.iloc[0].to_dict()
        # compressed (remove spaces/punct)
        import re
        def _compress(x: str) -> str:
            return re.sub(r"[^a-z0-9]", "", str(x).lower())
        s_comp = _compress(company_query)
        comp_col = self.cos[name_col].astype(str).map(_compress)
        m = self.cos[comp_col == s_comp]
        if not m.empty:
            return m.iloc[0].to_dict()
        m = self.cos[comp_col.str.contains(s_comp, na=False)]
        if not m.empty:
            return m.iloc[0].to_dict()
        choices = self.cos[name_col].astype(str).tolist()
        hit = self._fuzzy_one(company_query, choices)
        if hit and hit[1] >= 75:
            idx = choices.index(hit[0])
            return self.cos.iloc[idx].to_dict()
        return None

    def resolve_payload(
        self,
        investor_query: str,
        company_query: str,
        amount: float,
        subscription_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        inv = self.find_investor_row(investor_query)
        if not inv:
            raise ValueError(f"Investor not found: {investor_query}")

        cust_ref = inv.get("Custodian Client Ref")
        full_name = (str(inv.get("First Name", "")).strip() + " " + str(inv.get("Last Name", "")).strip()).strip()
        fee = self.find_fee_row(cust_ref, subscription_code, investor_full_name=full_name)
        using_default_rates = False
        if not fee:
            # Create default fee structure when no fee data exists
            using_default_rates = True
            print(f"⚠️  No fee data found for {investor_query} (Custodian Client Ref: {cust_ref}). Using default rates.")
            fee = {
                "Custodian Client Ref": cust_ref,
                "Investor name": full_name,
                "Subscription code": f"{full_name.replace(' ', '')}-EIS-1",
                "Fund": "Retail",
                "Gross/Net": "Net",
                "CC Set up fee %": 0.015,  # 1.5% default
                "CC AMC %": 0.02,         # 2.0% default
                "CC Carry %": 0.20,       # 20% default
            }
        else:
            print(f"✅ Found fee data for {investor_query}: {fee}")

        co = self.find_company_row(company_query)
        if not co:
            raise ValueError(f"Company not found: {company_query}")

        investment_type = _norm_gross_net(fee.get("Gross/Net"))
        classification = _class_from_fund(fee.get("Fund"))

        # Coerce share price to float robustly (handles numeric or string formats)
        # Pull share-price using detected column
        sp_key = getattr(self, "_co_share_price_col", "Current Share Price")
        sp_raw = co.get(sp_key) if sp_key in co else co.get("Current Share Price")
        try:
            if isinstance(sp_raw, str):
                s = sp_raw.strip().lower().replace("£", "").replace(",", "").replace(" ", "")
                if s.endswith("p"):
                    s = s[:-1]
                sp_val = float(s)
            else:
                sp_val = float(sp_raw)
        except Exception:
            sp_val = 1.0

        # Extract fee percentages
        upfront_pct = _as_pct(fee.get("CC Set up fee %"))
        amc_pct = _as_pct(fee.get("CC AMC %"))
        performance_pct = _as_pct(fee.get("CC Carry %"))
        
        shaped = {
            "investor": {
                "Custodian Client Ref": inv.get("Custodian Client Ref"),
                "Account Name": inv.get("Account Name"),
                "Salutation": inv.get("Salutation") or "Dear",
                "First Name": inv.get("First Name") or "",
                "Last Name": inv.get("Last Name") or "",
                "Contact email": inv.get("Contact email") or inv.get("Login Email") or "",
            },
            "fee_context": {
                "subscription_reference": fee.get("Subscription code") or "",
                "fund": fee.get("Fund") or "",
                "classification": classification,  # retail/professional
                "investment_type": investment_type,  # gross/net
                "upfront_pct": upfront_pct,
                "amc_pct": amc_pct,
                "performance_pct": performance_pct,
            },
            "company": {
                "Company Name": co.get(self._co_company_name_col) if self._co_company_name_col in co else co.get("Company Name"),
                "Current Share Price": sp_val,
                "Share Class": co.get(self._co_share_class_col) if self._co_share_class_col in co else co.get("Share Class") or "Ordinary Share",
            },
            "amount": float(amount),
            "using_default_rates": using_default_rates,
        }
        return shaped


