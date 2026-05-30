#!/usr/bin/env python3
"""xs_lint — .xs 啟發式驗證（PostToolUse: Write|Edit）。

職責：被編輯檔為 *.xs 時，對「明顯結構問題」與「未知函數 token」提出**非阻斷式**警示。
限制：XS 無公開 grammar / 編譯器，此為啟發式檢查，非完整語法驗證（見 SPEC Out of Scope）。

零第三方相依（Python 3 stdlib only）。一律 exit 0（非阻斷）。
"""
from __future__ import annotations

import json
import re
import sys

# Windows console 預設可能非 UTF-8（cp950），中文警示會 UnicodeEncodeError。
# 防禦性轉 UTF-8（stdlib，3.7+）。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

# KNOWN_TOKENS：由 vscode-xs grammar(xs.tmLanguage.json) 的
# keyword.control / bif / sysfnc / variable.builtin / .field / .constant 五類名單
# 確定性生成（全部小寫；數字後綴如 Plot2 / OutputField12 在比對時正規化去尾數）。
# 來源為 2023 grammar 快照，定位是 Hook 的離線對照清單——刻意「寧放行不誤殺」：
# 名單過時頂多漏報未知 token，不會誤殺合法腳本。重生方式見 docs（grammar → 此清單）。
KNOWN_TOKENS: frozenset[str] = frozenset({
    "above", "absvalue", "acc", "addspread", "adi", "ado", "alert", "and", "angle", "ar",
    "arccosine", "arcsine", "arctangent", "array", "array_compare", "array_copy",
    "array_getmaxindex", "array_gettype", "array_setmaxindex", "array_setvalrange",
    "array_sort", "array_sum", "arrays", "atr", "average", "averageif", "avgdeviation",
    "avglist", "avgprice", "baradjusted", "barfreq", "barinterval", "barslast", "begin",
    "below", "bias", "biasdiff", "bollingerband", "bool", "br", "break", "buy", "c", "case",
    "cci", "ceiling", "close", "closed", "closeh", "closem", "closeq", "closew", "closey",
    "coefficientr", "combination", "commoditychannel", "condition", "correlation", "cos",
    "cosine", "cotangent", "countif", "countifarow", "covariance", "cover", "cross",
    "crosses", "crossover", "crossunder", "currentbar", "currentdate", "currenttime",
    "currenttimems", "d_value", "dataalign", "date", "dateadd", "datediff", "datetojulian",
    "datetostring", "datevalue", "dayofmonth", "dayofweek", "daystoexpiration", "default",
    "defaultbuyprice", "defaultsellprice", "dif", "directionmovement", "dmo", "double",
    "downto", "dpo", "dwlimit", "else", "ema", "emp", "encodedate", "encodetime", "end",
    "erc", "execoffset", "expvalue", "extremes", "extremesarray", "factorial", "false",
    "file", "filled", "filledavgprice", "filledrecordbs", "filledrecordcount",
    "filledrecorddate", "filledrecordisrealtime", "filledrecordprice", "filledrecordqty",
    "filledrecordtime", "filter", "float", "floor", "for", "formatdate", "formatmqy",
    "formattime", "fracportion", "friday", "getbaroffset", "getfield", "getfielddate",
    "getlasttradedate", "getquote", "h", "high", "highd", "highdays", "highest",
    "highestarray", "highestbar", "highh", "highm", "highq", "highw", "highy", "hl_osc",
    "hour", "if", "iff", "input", "inputs", "instr", "int", "intportion", "intrabarpersist",
    "ismarketprice", "juliantodate", "k_value", "keltnerlb", "keltnerma", "keltnerub", "l",
    "lastdayofmonth", "leftstr", "linearreg", "linearregangle", "linearregslope", "log",
    "low", "lowd", "lowdays", "lowerstr", "lowest", "lowestarray", "lowestbar", "lowh",
    "lowm", "lowq", "loww", "lowy", "ma_osc", "macd", "mam", "market", "maxbarsback",
    "maxlist", "maxlist2", "mi", "midstr", "millisecond", "minlist", "minlist2", "minute",
    "mo", "mod", "mom", "momentum", "monday", "month", "mtm", "mtm_ma", "neg", "noplot",
    "not", "nthdayofmonth", "nthextremes", "nthextremesarray", "nthhighest",
    "nthhighestarray", "nthhighestbar", "nthlowest", "nthlowestarray", "nthlowestbar",
    "nthmaxlist", "nthminlist", "numeric", "numericarray", "numericarrayref", "numericref",
    "numericseries", "numericsimple", "numtostr", "o", "ohlcperiodsago", "oi", "once",
    "open", "opend", "openh", "openinterest", "openm", "openq", "openw", "openy", "or",
    "outputfield", "over", "percentr", "permutation", "pi", "plot", "pos", "position",
    "power", "print", "psy", "q_ask", "q_askunits", "q_avgdealedshare", "q_avglongunits",
    "q_avgprice", "q_avgshortunits", "q_basis", "q_bestask1", "q_bestask2", "q_bestask3",
    "q_bestask4", "q_bestask5", "q_bestasksize", "q_bestasksize1", "q_bestasksize2",
    "q_bestasksize3", "q_bestasksize4", "q_bestasksize5", "q_bestbid1", "q_bestbid2",
    "q_bestbid3", "q_bestbid4", "q_bestbid5", "q_bestbidsize", "q_bestbidsize1",
    "q_bestbidsize2", "q_bestbidsize3", "q_bestbidsize4", "q_bestbidsize5", "q_bid",
    "q_bidaskdiff", "q_bidaskdiffratio", "q_bidaskflag", "q_bidunits",
    "q_boughtaverageatopen", "q_boughtlotsatopen", "q_boughttickatopen", "q_breakevenpoint",
    "q_cashdirect", "q_close1mago", "q_close1wago", "q_close1yago", "q_close3mago",
    "q_closeoflastyear", "q_contractratio", "q_cpoiratio", "q_cptraderatio",
    "q_culaskticks", "q_culbidticks", "q_culbuyticks", "q_culmatchticks", "q_culsellticks",
    "q_currentcapitalin100million", "q_currenteps", "q_currentroe", "q_currentsharecapital",
    "q_dailydownlimit", "q_dailyhigh", "q_dailylow", "q_dailyopen", "q_dailyuplimit",
    "q_dailyvolume", "q_dayamplitude", "q_delta", "q_downlimitsecs", "q_downsecurities",
    "q_expireddate", "q_financialstatementstime", "q_gamma", "q_grossmarginrate",
    "q_impliedvolatilityonbuy", "q_impliedvolatilityonsell", "q_insize", "q_intrinsicvalue",
    "q_ioofmoney", "q_last", "q_lasttradingdate", "q_leverage", "q_marketcapin100million",
    "q_matchunit", "q_mintradingshares", "q_netvaluepershare", "q_opeprofitmarginrate",
    "q_operevenuepershare", "q_orderratio", "q_outsize", "q_prematch1", "q_prematch2",
    "q_prematch3", "q_prematch4", "q_premiumratio", "q_pretotalvolume",
    "q_pricechangeratio", "q_profitability", "q_refprice", "q_remaindays",
    "q_remaintradingdays", "q_revenuegrowth", "q_revenuemonth", "q_revenueyoy", "q_rho",
    "q_soldaverageatopen", "q_soldlotsatopen", "q_soldtickatopen", "q_spread",
    "q_strikeprice", "q_sumasksize", "q_sumbidsize", "q_targetchange",
    "q_targetchangeratio", "q_targetprice", "q_theoreticalprice", "q_theta", "q_tickvolume",
    "q_timevalue", "q_totalamount", "q_totalticks", "q_uplimitsecs", "q_upsecurities",
    "q_vega", "q_volatility", "q_volatilitydiff", "q_volumeratio", "qoq",
    "raiseruntimeerror", "random", "range", "rateofchange", "rc", "repeat", "ret", "retmsg",
    "return", "retval", "rightstr", "round", "rsi", "rsquare", "rsv", "sar", "saturday",
    "second", "sell", "setbarback", "setbarfreq", "setinputname", "setoutputname",
    "setplotlabel", "setposition", "settotalbar", "short", "sign", "simplehighest",
    "simplelowest", "sin", "sine", "square", "squareroot", "standarddev", "stochastic",
    "string", "stringarray", "stringarrayref", "stringref", "stringseries", "stringsimple",
    "stringtodate", "stringtotime", "strlen", "strtonum", "sumlist", "summation",
    "summationif", "sunday", "swinghigh", "swinghighbar", "swinglow", "swinglowbar",
    "switch", "symbol", "symbolname", "tan", "tangent", "techscore", "text", "then",
    "thursday", "time", "timeadd", "timediff", "timeseriesforecast", "timetostring",
    "timevalue", "to", "trix", "true", "trueall", "trueany", "truecount", "truefalse",
    "truefalsearray", "truefalsearrayref", "truefalseref", "truefalseseries",
    "truefalsesimplevar", "truehigh", "truelow", "truerange", "tuesday", "typicalprice",
    "under", "until", "uplimit", "upperstr", "userid", "v", "va", "value", "vao", "var",
    "variable", "variables", "varianceps", "vars", "vhf", "volume", "vpt", "vr", "vva",
    "wad", "wednesday", "weekofmonth", "weekofyear", "weightedclose", "while", "xaverage",
    "xor", "year", "yoy",
})


def read_event() -> dict:
    """從 stdin 讀 PostToolUse 事件 JSON；失敗則回空 dict。"""
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def get_target_path(event: dict) -> str | None:
    """取被編輯檔路徑；非 *.xs 回 None。"""
    path = (event.get("tool_input") or {}).get("file_path")
    if isinstance(path, str) and path.lower().endswith(".xs"):
        return path
    return None


def strip_comments(src: str) -> str:
    """移除註解與字串字面量，避免其內文字干擾結構/ token 檢查。

    處理：區塊註解 {...}（簡化非貪婪，不處理深層巢狀）、行註解 //、雙引號字串。
    字串一併移除，否則 Alert("...begin...") 之類會虛增 begin/end 計數或誤判 token。
    """
    src = re.sub(r"\{[^{}]*\}", " ", src)  # 區塊註解（簡化，不處理深層巢狀）
    src = re.sub(r"//[^\n]*", " ", src)  # 行註解
    src = re.sub(r'"[^"]*"', " ", src)  # 雙引號字串字面量
    return src


def check_structure(code: str) -> list[str]:
    """結構檢查：begin/end 配對、if 是否缺 then。回警示清單。"""
    warnings: list[str] = []
    lower = code.lower()

    n_begin = len(re.findall(r"\bbegin\b", lower))
    n_end = len(re.findall(r"\bend\b", lower))
    if n_begin != n_end:
        warnings.append(f"begin / end 不成對（begin={n_begin}, end={n_end}）")

    n_if = len(re.findall(r"\bif\b", lower))
    n_then = len(re.findall(r"\bthen\b", lower))
    if n_if > n_then:
        warnings.append(f"有 if 缺對應 then（if={n_if}, then={n_then}）")

    return warnings


def check_unknown_tokens(code: str) -> list[str]:
    """未知函數 token 檢查（依賴 KNOWN_TOKENS；未填則跳過）。

    啟發式：抓 `識別字(` 形式的呼叫名，比對 KNOWN_TOKENS（grammar 內建清單）。
    比對前正規化去尾數字（Plot2 → plot、OutputField12 → outputfield），對應 grammar
    裡的數字後綴函數族。未命中者**不武斷判錯**——XS 允許自訂函數，故警示語明示
    「可能為自訂函數或拼寫錯誤」，符合「寧放行不誤殺」的離線清單定位。
    """
    if not KNOWN_TOKENS:
        return []
    warnings: list[str] = []
    for name in sorted({m.lower() for m in re.findall(r"\b([A-Za-z_]\w*)\s*\(", code)}):
        if name in KNOWN_TOKENS:
            continue
        if re.sub(r"\d+$", "", name) in KNOWN_TOKENS:  # 去尾數字再比對（Plot2…）
            continue
        warnings.append(f"未收錄函數 token：{name}（可能為自訂函數或拼寫錯誤，請確認）")
    return warnings


def main() -> int:
    event = read_event()
    path = get_target_path(event)
    if path is None:
        return 0  # 非 .xs，靜默

    try:
        with open(path, encoding="utf-8-sig") as f:
            raw = f.read()
    except OSError:
        return 0  # 讀不到就不擾民

    code = strip_comments(raw)
    warnings = check_structure(code) + check_unknown_tokens(code)

    if warnings:
        print(f"⚠️ XS 檢查（{path}）：", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)
    return 0  # 永遠非阻斷


if __name__ == "__main__":
    sys.exit(main())
