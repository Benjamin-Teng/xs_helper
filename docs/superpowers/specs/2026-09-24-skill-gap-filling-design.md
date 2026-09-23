# XS skill 知識缺口盤點（缺口填補計畫的規格）

> 狀態：規格，供 [`../plans/2026-09-24-skill-gap-filling.md`](../plans/2026-09-24-skill-gap-filling.md) 引用。
> 來源：2026-09-24 盤點；官方範例庫 clone 為 sysjust-xq/XScript_Preset（commit d15a415）與 sysjust-xq/XQStrategy（commit c799745），不隨 repo 散佈。
> 缺口來由：v0.5.1 高強度測試中，依 skill 寫 20 支範例的 subagent 回報 reference 不足之處，再逐項對 xshelp 與官方範例庫查證。

調查時間：2026-09-24。一手來源：xshelp REST (`https://xshelp.xq.com.tw/XSHelp/rest?a=`) +
HTML 條目頁、離線副本 `canon_entries.json`（53 筆 DECLARATION/CONTROLFLOW/CONSTANT/SKIPWORD
條目全文，UTF-8）、官方 clone `XScript_Preset`（1419 檔）與 `XQStrategy`（4748 檔）。

---

## 1. `Rank`

**現況**：`builtin-functions.md` 只在 `NthMaxList`/`NthMinList` 提到 rank 字樣，`language.md`
§9.4 第 242 行只有一行「選股腳本專用，宣告排行作業」，無語法範例。`language.md` 第 268 行明列
待補。

**一手來源**：`canon_entries.json` 內 `DECLARATION/Rank` 條目全文（xshelp 一手，非摘要）：

```text
Rank 是一個選股腳本內才能使用的語法，主要是用來宣告腳本執行排行的作業。
Rank支援的屬性：pos（名次，1起）、range（排行%=pos/count*100）、
pr（Percentile Rank%=(N-pos)/(N-1)*100）、count（參與排行商品數）、
value（=retval）、avgvalue、medvalue、minvalue、maxvalue、Q1、Q3、isvalid。

範例：
Rank _bias10 begin
  retval = close - average(close, 10);
end;
if _bias10.pos[1] <> _bias10.pos then ret = 1;
```

官方 clone 交叉查證：`XScript_Preset` 與 `XQStrategy` 全庫搜尋 `Rank <name> begin` 宣告語法與
`.pos`/`.pr`/`.isvalid` 存取語法**皆 0 命中**（`_rank` 只是普通變數名，非本語法）。

**可補程度**：**可完整補**（xshelp 條目文字含完整屬性表＋一段範例，足以寫語法規則）；但**沒有
第二個官方庫範例可交叉驗證**，只有 xshelp 自帶的單一範例，語意上仍建議標「僅單一來源」。

**建議補在**：`language.md` §9.4 `Rank` 那行擴充為獨立小節（比照 `Default` 的處理方式），或在
`builtin-functions.md` 新增「排行語法」一節。

**工作量**：小。

---

## 2. `inputkind:=Dict/DateRange/SymbolPrice`、`quickedit`

**現況**：`language.md` 第 245–247 行只有三行摘要，無語法範例，未講型別回傳。

**一手來源**：`canon_entries.json` 四筆條目全文（xshelp 一手）：

- `inputkind`：`Dict` 範例 —
  `input: IndexPomUnit(1, "大盤融資單位", inputkind:=Dict(["金額",1],["張數",2]));`
  （宣告時給的預設值型別＝Dict 選項值的型別，可為數值或字串，讀值時就是一般 input 變數）。
- `daterange`：`input:FdifferenceDate(20180301,"...",inputkind:=daterange(20160301,20190301,"D"));`
  → **單一日期**變數（不是日期範圍兩個值），型別為 8 位數字 `YYYYMMDD`，第三參數是頻率字串
  （日/週/月/季/半年/年，範例用 `"D"`）。
- `symbolprice`：`input:OHLC_Opti(200,"價格：",inputkind:=SymbolPrice());` → 讓使用者在 UI 上選
  Open/High/Low/Close 其中一個，變數本身仍是數值（存的是選到的價格序列）。
- `quickedit`：只能搭配指標腳本的 `input`+`inputkind` 用，`quickedit:=true` 讓選項直接顯示在圖上
  可調，不影響變數型別/讀值方式，純 UI。範例：

  ```text
  input: IndexPomUnit(1, "...", inputkind:=Dict(["金額",1],["張數",2]), quickedit:=true);
  if IndexPomUnit = 1 then plot1(GetField("融資買進金額","D"))
  else if IndexPomUnit = 2 then plot1(GetField("融資買進張數","D"));
  ```

官方庫交叉查證：`grep -r "inputkind" official_src` **0 命中**（Preset/XQStrategy 都未用到，屬冷門
UI 語法，符合預期）。

**可補程度**：**可完整補**，四個條目都有完整語法＋範例；DateRange 是「一個日期，非範圍」這點
值得特別標出（原本問題假設它是兩個日期，經查證是錯的，只有一個 min、一個 max 供 UI 選取，變數
本身是單一日期值）。

**建議補在**：`language.md` §9.4 對應四行擴充；可能需要一個新的「UI 輸入宣告」小節。

**工作量**：小～中（四個條目要一起寫，且要澄清 DateRange 語意）。

---

## 3. `while` / `repeat…until` / `once` / `switch/case`

**現況**：`language.md` 第 103–106、213–218 行只有一行摘要，第 268 行明列「Preset 取樣未涵蓋，
需補真實範例」。

**一手來源**：官方庫真實範例（已用 grep 逐一撈出）：

**while**（`XScript_Preset/函數/交易相關/CalcVWAPDistribution.xs:43,48`）：

```text
while GetFieldDate("Date", "1")[idx] = lastdate begin
    ...
end;
while days < totaldays begin
    ...
end;
```

另一例（`.../趨勢分析/SwingHigh.xs:12`）：`while cnt < occur and now < Length` （單行無 begin/end）。

**repeat…until**（`XScript_Preset/選股/05.型態選股/突破整理格局.xs:12-18`）：

```text
repeat
 begin
 value1=simplehighest(high[1],period);
 value2=simplelowest(low[1],period);
 period=period+1;
 end;
until period >= rangemax or (value1 > value2 * (1 + limit1/100));
```

**once**（區塊條件式，`XScript_Preset/自動交易/0-基本語法/09-CancelAllOrders.xs:15-18`，唯一命中）：

```text
Once(Position = 0 and Filled = 0 and GetInfo("TradeMode") = 1) begin
    SetPosition(1, GetField("跌停價", "D"), label:="跌停價買進委託");
    _time = TimeAdd(CurrentTime, "M", _n);
end;
```

官方庫**只找到 `Once(判斷式) begin...end` 這一種寫法**，未找到「純區塊、無括號判斷式」的第二種
`Once` 用法；`canon_entries.json` 的 `Once` 條目本身也只示範 `Once(判斷式) Begin...End` 這一種，
文中提到的「另一種只需一次的效果」是用 `Var: FirstTime(False)` + `If` 手動模擬，**不是 Once 語法
本身的第二形式**。→ 原任務描述「once 的兩種用法：區塊 vs 條件式 `Once(...)`」查證結果是**只有一種
語法形式**（`Once(cond) begin...end`），另一種是「不用 Once、改用旗標變數」的替代寫法，不是 Once
的第二種語法。

**switch/case/default**（`XQStrategy/01台股的選股條件/04籌碼/大戶持股人數/連續N期大戶持股人數增加.xs:8-23`）：

```text
switch(value1)begin
  case 1: condition1 = TrueAll(...); value2 = ...;
  case 2: condition1 = TrueAll(...); value2 = ...;
  default : value1 = round(x/200,0);
  switch (value1) begin
    case 1: ...
    case 2: ...
    case 3: ...
    case 4: ...
    default: ...
  end;
```

（示範了 `switch` 可以巢狀，`case`/`default` 後面接運算式時不需要 begin/end 包多行也能單行寫）。
`canon_entries.json` 另有官方範例含 `Case 6 to 20:`（範圍寫法）。

**可補程度**：**可完整補**（while/repeat/switch 各有 ≥1 個官方庫真實檔案範例；once 只有 1 個
範例但夠寫語法規則，且能明確更正「兩種用法」的錯誤預設）。

**建議補在**：`language.md` §9.3（CONTROLFLOW）逐一加語法框＋官方庫出處檔名；並更新第 268 行
待補清單為已完成。

**工作量**：中（四個關鍵字，需引用檔案路徑＋整理程式碼片段）。

---

## 4. `Plot` 的 `checkbox:=`、`OutputField` 的 `order:=`

**現況**：`builtin-functions.md` 第 76 行 `Plot` 簽名寫成
`(order, value [, name [, checkbox]])`（把 checkbox 當**第 4 個位置參數**）；第 83 行 `OutputField`
簽名寫成 `(order, value [, decimals [, name]])`（把第一個位置參數命名為 `order`）。

**xshelp 一手來源**（REST `a=Plot` / `a=OutputField`，官方原文）：

- `Plot` 官方語法：

  ```text
  Plot(輸出序號，指標數值)
  Plot(輸出序號，指標數值，繪圖序列名稱)
  Plot(輸出序號，指標數值，繪圖序列名稱，checkbox:=1)
  ```

  → **checkbox 必須用 `checkbox:=` 具名參數語法**，不是單純第 4 個位置值；且官方稱第一參數為
  「輸出序號」，不是「order」。`canon_entries.json` 的 `checkbox` 條目範例也證實：
  `plot4(close,"收盤價",checkbox:=1);`。

- `OutputField` 官方語法：

  ```text
  OutputField(輸出序號, 數值)
  OutputField(輸出序號, 數值, 小數位數)
  OutputField(輸出序號, 數值, 小數位數, 輸出欄位名稱)
  ```

  官方本體條目**完全沒有 `order:=`**！`order:=` 是另一個**獨立的 DECLARATION 條目**
  （`canon_entries.json`／xshelp `a=order`）：

  ```text
  order 搭配 OutputField 使用，order 是用來指定排序選股結果區的欄位數值上/下序的函數。
  order:=-1 為由小到大排序；order:=1 為由大到小排序。
  範例：outputfield1(value1,"5日均量",order:=-1);
  ```

**矛盾具體列出**：

1. `builtin-functions.md` 把 `Plot` 的 `checkbox` 寫成第 4 個**位置**參數，實際上官方語法要求
   `checkbox:=` **具名**參數，且只能放在字串名稱之後（不能單純第四格填 0/1）。
2. `builtin-functions.md` 把 `OutputField` 第一個位置參數命名為「order」，這名字**和**
   `order:=`（獨立語法、控制排序方向的具名參數）**撞名但完全是兩件事**：前者是「輸出序號
   1~99，決定欄位顯示順序」，後者是「-1/1，決定該欄位數值排序方向」。目前的簽名寫法完全沒提到
   `order:=` 具名參數的存在，讀者容易把兩者搞混（尤其"order"這個詞被兩用）。

**可補程度**：**可完整補**，兩邊 xshelp 原文都拿到了，且官方庫也有大量 `checkbox:=0/1` 與少量
`axis:=` 實例可佐證具名參數寫法（見下一項）。

**建議補在**：`builtin-functions.md` 第 76、83 行簽名改寫，並在旁邊加註「`order:=` 是另一個獨立
排序具名參數，勿與第一參數的『輸出序號』混淆」。

**工作量**：小。

---

## 5. `Asc` `Desc` `axis`

**現況**：`language.md` 第 253 行標「xshelp 缺頁，用途待查證」。

**驗證結果（重新即時查證，2026-09-24）**：

- `curl https://xshelp.xq.com.tw/XSHelp/rest?a=Asc`／`Desc`／`axis` 三者 REST JSON 的
  `desc`/`fulldesc` 皆為 `null`，`categoryid` 都指向 `DECLARATION`。
- 直接抓 HTML 頁（`?HelpName=Asc&group=DECLARATION`）確認 `og:description` 為空字串、頁面本體
  無條目文字 —— **xshelp 這三個條目頁本身就是空的，不是離線副本抓漏**，語言.md 原判斷正確，
  維持「待查證」。

- **但 `axis` 在官方 clone 裡有大量實際用法可推定語意**（`Plot` 系列的具名參數，指定畫在哪條
  Y 軸）：

  ```text
  plot1(GetField("散戶買張"),"散戶買進(張)",axis:=1,ScaleLabel:=slfull,ScaleDecimal:=sd0);
  plot2(value4,"主力累計買賣超",checkbox:=1,axis:=2,...); //line，axis2
  plot3(value1,"買進",checkbox:=0,axis:=11,...); //line，axis11
  ```

  出現 `axis:=1`／`axis:=2`／`axis:=11` 等值，配合原始碼註解 `//bar，axis2`／`//line，axis11`，
  可判斷 `axis` 是 `Plot` 的具名參數，用來指定該序列畫在哪一條 Y 軸（值域似乎不只 0/1，可能是
  軸編號，含次座標軸 11 這種兩位數編號，精確編碼規則仍待查證）。
- `Array_Sort`/`Array_Sort2d` 的 `order` 參數（builtin-functions.md 244-245 行）**未在官方庫找到
  任何呼叫範例**，也搜尋不到 `Array_Sort(..., Asc)` 或 `..., Desc)` 這類寫法，所以 `Asc`/`Desc`
  是否為 `Array_Sort`/`OutputField order:=` 可用的具名常數，**仍無法從官方來源證實或證偽**。

**可補程度**：**`axis` 可部分補**（官方庫真實用法可寫出「axis:= 用於 Plot，指定畫在哪條 Y 軸，
常見值 1/2/11」，但精確編碼規則仍待查證）；**`Asc`/`Desc` 只能維持待查證**（xshelp 頁面確認為
空，官方庫零命中，只能實測或等 xshelp 補頁）。

**建議補在**：`language.md` 第 253 行拆成兩行——`axis` 移到有內容的一行並附官方庫出處；
`Asc`/`Desc` 維持待查證註記（更新查證時間戳，證明是「重新查過仍未解」而非「沒查過」）。

**工作量**：小。

---

## 6. reference 檔內既有「待補」清單逐條檢查

### 6-1 `builtin-functions.md` 第 301 行
>
> 各 bif 的多載細節（如 `Buy` 的 `price`/`label` 完整位置語意）以 xshelp 個別函數頁為準。

**判斷**：**可補，但工作量大**。xshelp REST 對每個函數名都能單獨查到完整 `fulldesc`（已用
`Plot`/`OutputField`/`GetBarOffset` 驗證格式一致、含完整語法變體與範例），逐一撈取可行，但
`builtin-functions.md` 覆蓋的 bif 數量大（表格內約上百個），逐條 fulldesc 化屬於「大」工作量，
建議只在使用者實際問到某函數多載時才 F3 現查（維持現行策略），不建議一次性全量蒸餾。

### 6-2 `fields.md` 第 211 行
>
> `QPRICE/QVOLUME/QFINANCE/QMARKET/QOPTION/QFIVE`、`TPRICE/TVOLUME/TCHIP/TBASIC/…` 完整中文清單
> 未收錄。

**查證**：直接用 `a=QPRICE` 查 REST **0 命中**（`QPRICE` 不是可搜尋的條目名稱，是欄位前綴代號，
不對應獨立 xshelp 頁）。改查 `a=報價` 命中 `GetQuote` 條目，`fulldesc` 內含報價欄位分類線索
（`q_欄位英文名稱` 的說明），但**沒有給出完整欄位清單**，真正完整清單可能只存在於 XQ 選股精靈
UI 或另一個尚未定位的 xshelp 頁面。

**判斷**：**只能部分補**（可以補上 `GetQuote`/`GetField` 系列的欄位前綴命名規則說明），完整欄位
清單需要進一步定位資料來源（可能不在 xshelp 條目頁，而在選股精靈 UI 或另一份 PDF/Excel），
超出本次盤點範圍，工作量標「大」且**來源待定位**。

### 6-3 `language.md` 第 265 行起「待補（後續蒸餾）」

內容：

```text
- [ ] 各型別關鍵字的精確語意差異（Simple vs Series vs Ref 的記憶體/求值模型）以 xshelp 校對補強。
```

**查證**：xshelp 對 `NumericSimple`/`NumericSeries`/`NumericRef` 等各有獨立條目（REST 可查到），
理論上可逐一撈取 fulldesc 比對差異。未在本次任務範圍內逐一查證（任務未列此為必查項），僅確認
**可補**（xshelp 有對應條目，非空），工作量中～大（需 6 個型別 x 3 種修飾詞交叉比對語意）。

### 6-4 `system-functions.md` 第 443 行
>
> `xshelp` 系統函數清單若有 Preset 未涵蓋者（如 `GetBarOffset`），交叉補上。

**查證**：`curl a=GetBarOffset` 確認條目存在，`categoryid` 對應 `Description: GENERALFUNC`
（一般函數），`fulldesc` 完整（含語法、範例）。**可完整補**——只是原本蒸餾時用 Preset 原始碼
反查函數清單，漏掉了「有 xshelp 條目、但 Preset 範例庫剛好沒呼叫到」的函數。真正修法應該是反過來
用 xshelp `GENERALFUNC`/`TRADEFUNC` 等分類頁窮舉，再對照 Preset 是否有範例，而非只靠 Preset
反推清單。

**工作量**：中（需要窮舉 xshelp 各函數分類頁，逐一核對 `builtin-functions.md`/`system-functions.md`
是否已收錄）。

---

## 7. language.md §2 命名限制「編譯器是否報錯待查證」

**查證**：xshelp 全站搜尋 `a=保留字`、`a=命名規則`、`a=變數名稱` 皆查無條目（與 `language.md`
原註記一致，重新查證仍是 0 筆）。REST 介面找不到任何命名規則／保留字專頁，唯一相關的是
`Bool/Int/Float/Double` 的「保留字」頁（已收錄於 §9.5），但那頁**只說明這 4 個字保留、未使用**，
沒有講「用關鍵字當變數名會不會編譯錯誤」這件事。

**判斷**：**沒有任何官方一手來源能回答這個問題**。xshelp 沒有語言規範/文法書頁面，官方 clone
（Preset/XQStrategy）是「範例庫」不是「反例庫」，无法用來證明某寫法會編譯失敗（沒出現不代表
禁止）。**只能在 XQ 編輯器實際貼一段用關鍵字當變數名的腳本，看編譯器是否報錯**，這點無法迴避
實測，維持原文的保守寫法（一律避開）是對的。

---

## 額外發現的缺口（任務未列出）

1. **`Rank` 的 `.pos`/`.pr`/... 屬性讀取語法未經官方庫驗證**——目前僅有 xshelp 自帶單一範例，
   若有使用者要寫 `Rank` 相關選股邏輯，risk 是「屬性名稱記對了，但唯一官方範例是否涵蓋所有情境
   （例如：Rank 是否可用在自動交易/警示腳本，還是僅選股）」還沒查證。xshelp 原文只說「選股腳本
   內才能使用」，這點值得寫進 reference 當限制條件。

2. **`switch` 允許巢狀**（`switch(...) begin ... switch(...) begin ... end; end;`）與
   **`case N to M:` 範圍寫法**（canon_entries.json 範例），這兩個語法細節目前完全沒被
   `language.md` 提及，是原任務清單漏掉的子缺口。

3. **`OutputField` 具名參數 `order:=` 只對數值型欄位有意義**（依 xshelp order 條目語意，用於
   選股結果的排序），但目前完全沒有 reference 提到 `OutputField` 系列還有第五個可選具名參數
   `order:=`（現有簽名只寫 4 個位置參數，完全遺漏這個具名參數的存在，不只是命名衝突，是**功能
   遺漏**）。

4. **`Plot` 系列除了 `checkbox:=` 還有 `axis:=`、`ScaleLabel:=`、`ScaleDecimal:=` 等具名參數**
   （官方庫大量出現），`builtin-functions.md` 完全沒收錄這些，屬於同一類「Plot 具名參數」缺口，
   建議與第 4 項一起補。

5. **`fields.md` 的 QPRICE 等欄位清單來源本身待定位**（見 6-2），不是「還沒蒸餾」而是「不確定
   xshelp 有沒有窮舉頁」，這比原先假設的「量大但知道去哪抓」更嚴重，建議下次任務先定位資料源
   再排蒸餾工作量。
