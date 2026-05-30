# 系統函數（system functions / sysfnc）

> **來源**：全數蒸餾自 `XScript_Preset/函數/<分類>/<名稱>.xs`（已凍結快照，gitignored、不打包）。
> 簽名取自各檔 `input:` 宣告、語意取自實作。此處未收錄、或冷門無源者 → 走 SKILL.md
> 的 **F3 線上查證**（`xshelp.xq.com.tw/XSHelp/`），**不杜撰**（G1）。
> 收錄 224 個 Preset 函數，依官方目錄分 14 類。

---

## 共通慣例（讀本檔前先看）

1. **呼叫方式**：`FuncName(arg1, arg2, …)`。函數名**大小寫不敏感**（`Average` = `average`）。
   少數函數為**中文名**（如 `KO成交量擺盪指標`、`Q指標`、`漲幅排行榜`），照原名呼叫。
2. **回傳機制**（XS 沒有 `return value` 語法，靠指派）：
   - **單值函數**：把結果指派給「**與函數同名的變數**」（如 `Average = …`），或指派給內建回傳槽 `ret` / `retval`（兩者等價，皆代表回傳值）。呼叫端直接 `x = Average(Close,20);` 取用。
   - **多輸出函數**：透過 `numericref` 參數**回填**（呼叫端先 `var:` 宣告變數再傳入），函數本身回傳**狀態碼**（成功通常 `1`、參數錯誤 `-1`）。例：`Stochastic(9,3,3, rsv, k, d);` 結果在 `rsv/k/d`。
3. **參數型別**（簽名縮寫）：

   | 縮寫 | XS 型別 | 意義 |
   |------|---------|------|
   | `Series` | numericseries | 數值時間序列，可 `x[n]` 取前 n 根 |
   | `Num` | numericsimple / numeric | 純量 |
   | `Ref↑` | numericref | **輸出**參考（回填，呼叫端先宣告變數傳入） |
   | `Array` | numericarray | 數值陣列（傳入） |
   | `ArrayRef↑` | numericarrayref | **輸出**陣列參考（回填） |
   | `Str` | stringsimple / string | 字串 |
   | `TFSeries` | truefalseseries | 布林序列 |
   | `TFSimple` | truefalsesimple | 布林純量 |

   回傳型別：`Num`（數值）、`Bool`（布林，源碼 `{@type:function_bool}`）、`Str`（字串，`{@type:function_string}`）、`狀態` = 回傳成功/失敗碼、`(out)` = 主要結果在 `Ref↑` 參數。
4. **`SetBarMode(n)`**（其實是 bif，群組 `GENERALFUNC`）：多數函數源碼開頭有此行，宣告該函數的**計算模式**，呼叫端無須理會、不影響呼叫方式。官方三值語意（xshelp 一手）：
   - `SetBarMode(0)`＝**Auto（預設）**：由系統自動判定屬 simple 或 series。
   - `SetBarMode(1)`＝**Simple**：今期計算與前期**各自獨立、互不引用**（如 `AvgPrice`＝單根 OHLC 算完）。Preset 實證：155 處簡單函數用此。
   - `SetBarMode(2)`＝**Series**：今期計算會**引用前期數值**（連續/遞迴，如 `EMA`/`XAverage`/MACD/RSI）。Preset 實證：47 處遞迴型函數用此。
5. **頻率代碼**（價格取得 / 跨頻率用）：`D`=日、`W`=週、`M`=月、`Q`=季、`H`=半年、`Y`=年；分鐘頻率以數字字串 `"1"/"5"/"60"` 等表示。

---

## 1. 價格取得（價格取得/）

> 來源：`XScript_Preset/函數/價格取得/*.xs`

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `AvgPrice` | `(): Num` | 當根均價 `(O+H+L+C)/4` |
| `TypicalPrice` | `(): Num` | 典型價 `(H+L+C)/3` |
| `WeightedClose` | `(): Num` | 加權收盤 `(2C+H+L)/4` |
| `TrueHigh` | `(): Num` | 真實高 `Max(High, Close[1])` |
| `TrueLow` | `(): Num` | 真實低 `Min(Low, Close[1])` |
| `Highest` | `(thePrice:Series, Length:Num): Num` | N 期最高值（增量演算，內部呼叫 `Extremes`） |
| `Lowest` | `(thePrice:Series, Length:Num): Num` | N 期最低值 |
| `FastHighest` | `(thePrice:Series, Length:Num): Num` | 同 `Highest`（快速版） |
| `FastLowest` | `(thePrice:Series, Length:Num): Num` | 同 `Lowest`（快速版） |
| `CloseD`/`OpenD`/`HighD`/`LowD` | `(PeriodsAgo:Num): Num` | 取**日**頻率前 `PeriodsAgo` 根的 收/開/高/低；`=GetField("Close","D")[PeriodsAgo]` |
| `CloseW`/`OpenW`/`HighW`/`LowW` | `(PeriodsAgo:Num): Num` | 取**週**頻率對應價 |
| `CloseM`/`OpenM`/`HighM`/`LowM` | `(PeriodsAgo:Num): Num` | 取**月**頻率對應價 |
| `CloseQ`/`OpenQ`/`HighQ`/`LowQ` | `(PeriodsAgo:Num): Num` | 取**季**頻率對應價 |
| `CloseH`/`OpenH`/`HighH`/`LowH` | `(PeriodsAgo:Num): Num` | 取**半年**頻率對應價 |
| `CloseY`/`OpenY`/`HighY`/`LowY` | `(PeriodsAgo:Num): Num` | 取**年**頻率對應價 |

---

## 2. 價格計算（價格計算/）

> 來源：`XScript_Preset/函數/價格計算/*.xs`

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `Average` | `(thePrice:Series, Length:Num): Num` | 簡單移動平均 SMA = `Summation/Length` |
| `XAverage` | `(thePrice:Series, Length:Num): Num` | 指數平滑移動平均 EMA（標準遞迴 `EMA[1]+α(P-EMA[1])`） |
| `EMA` | `(thePrice:Series, Length:Num): Num` | 指數移動平均（前 Length 根改用累進 SMA 暖機，之後同 XAverage） |
| `WMA` | `(thePrice:Series, Length:Num): Num` | 加權移動平均（權重 Length…1） |
| `Summation` | `(thePrice:Series, Length:Num): Num` | N 期加總 |
| `AvgDeviation` | `(thePrice:Series, Length:Num): Num` | N 期平均絕對離差 |
| `Range` | `(): Num` | `High - Low` |
| `TrueRange` | `(): Num` | `TrueHigh - TrueLow` |
| `RateOfChange` | `(thePrice:Series, Length:Num): Num` | N 期變動率（%） |
| `UpLimit` | `(refPrice:Num): Num` | 依台股級距算 `refPrice` 的漲停價 |
| `DwLimit` | `(refPrice:Num): Num` | 依台股級距算 `refPrice` 的跌停價 |
| `ReadTicks` | `(tick_array:Array[X,Y], readtick_cookie:Ref↑): Num筆數` | 讀取兩次洗價間的逐筆 Tick（自動合併台股 MultiTick），資料填入 `tick_array`（每筆 11 欄），回傳筆數。`cookie` 須宣告 `intrabarpersist` 並照實回傳；陣列第二維須 ≥ 11。詳見源碼檔頭大段註解 |

---

## 3. 價格關係（價格關係/）

> 來源：`XScript_Preset/函數/價格關係/*.xs`。「Bar」系列回傳的是**K 棒相對位置（offset，0=當根）**。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `Extremes` | `(SourceSeries:Series, Length:Num, DscAsc:Num, refExtremeValue:Ref↑, refExtremeBar:Ref↑): 狀態` | N 期極值核心：`DscAsc`=1 取極大、-1 取極小；回填極值與其 K 棒 offset。多數 Highest/Lowest 系列基於它 |
| `ExtremesArray` | `(SourceArray:Array, Size:Num, DscAsc:Num, refExtremeValue:Ref↑, refExtremeIndex:Ref↑): 狀態` | 陣列版極值（回填值與索引） |
| `NthExtremes` | `(SourceSeries:Series, Length:Num, N:Num, DscAsc:Num, refExtremeValue:Ref↑, refExtremeBar:Ref↑): 狀態` | 第 N 個極值 |
| `NthExtremesArray` | `(SourceArray:Array, Size:Num, N:Num, DscAsc:Num, refExtremeValue:Ref↑, refExtremeIndex:Ref↑): 狀態` | 陣列版第 N 個極值 |
| `HighestBar` / `FastHighestBar` | `(thePrice:Series, Length:Num): Num` | 期間最高值所在 K 棒 offset |
| `LowestBar` / `FastLowestBar` | `(thePrice:Series, Length:Num): Num` | 期間最低值所在 K 棒 offset |
| `HighestArray` | `(thePriceArray:Array, ArraySize:Num): Num` | 陣列最大值 |
| `LowestArray` | `(thePriceArray:Array, ArraySize:Num): Num` | 陣列最小值 |
| `NthHighest` | `(N:Num, thePrice:Series, Length:Num): Num` | N 期內第 N 高值 |
| `NthLowest` | `(N:Num, thePrice:Series, Length:Num): Num` | N 期內第 N 低值 |
| `NthHighestBar` | `(N:Num, thePrice:Series, Length:Num): Num` | 第 N 高值 K 棒 offset |
| `NthLowestBar` | `(N:Num, thePrice:Series, Length:Num): Num` | 第 N 低值 K 棒 offset |
| `NthHighestArray` | `(thePriceArray:Array, Size:Num, N:Num): Num` | 陣列第 N 高值 |
| `NthLowestArray` | `(thePriceArray:Array, Size:Num, N:Num): Num` | 陣列第 N 低值 |
| `SimpleHighest` / `SimpleLowest` | `(thePrice:Series, Length:Num): Num` | 期間最高/最低（簡單迴圈版） |
| `SimpleHighestBar` / `SimpleLowestBar` | `(thePrice:Series, Length:Num): Num` | 期間最高/最低的 K 棒 offset（簡單版） |
| `HighDays` | `(length:Num): Num` | 過去 length 筆內「創新高」次數 |
| `LowDays` | `(length:Num): Num` | 過去 length 筆內「創新低」次數 |
| `OHLCPeriodsAgo` | `(FreqType:Num, FreqAgo:Num, refFreqOpen:Ref↑, refFreqHigh:Ref↑, refFreqLow:Ref↑, refFreqClose:Ref↑): 狀態` | 取指定頻率（1 日 2 週 3 月 3.25 季 3.5 半年 4 年）前 `FreqAgo` 根的 OHLC |
| `MoM` | `(MomVal:Series): Num` | 月增率（%，**僅月頻率**，否則 runtime error） |
| `QoQ` | `(QoQVal:Series): Num` | 季增率（%，**僅季頻率**） |
| `YoY` | `(YoYVal:Series): Num` | 年增率（%，月/季/年頻率，內部用 `RateOfChange`） |

---

## 4. 技術指標（技術指標/）

> 來源：`XScript_Preset/函數/技術指標/*.xs`。多輸出者（DMI/KD/MACD）見「重點函數詳解」。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `MACD` | `(Price:Series, FastLength:Num, SlowLength:Num, MACDLength:Num, DifValue:Ref↑, MACDValue:Ref↑, OscValue:Ref↑): (out)` | MACD：回填 DIF / MACD / OSC（柱） |
| `DIF` | `(FastLength:Num, SlowLength:Num): Num` | MACD 的 DIF 線（以加權收盤計） |
| `Stochastic` | `(length:Num, rsvt:Num, kt:Num, rsv:Ref↑, k:Ref↑, d:Ref↑): 狀態` | KD 核心：回填 RSV / K / D |
| `K_Value` | `(Length:Num, RSVt:Num): Num` | KD 的 K 值 |
| `D_Value` | `(Length:Num, Kt:Num): Num` | KD 的 D 值 |
| `RSV` | `(Length:Num): Num` | RSV 值 |
| `RSI` | `(price:Series, length:Num): Num` | 相對強弱指標 |
| `DirectionMovement` | `(length:Num, pdi_value:Ref↑, ndi_value:Ref↑, adx_value:Ref↑): (out)` | DMI：回填 +DI / -DI / ADX |
| `DMO` | `(Length:Num): Num` | +DI 與 -DI 之差 |
| `CCI` | `(Length:Num): Num` | 順勢指標（= `CommodityChannel`） |
| `CommodityChannel` | `(length:Num): Num` | CCI 核心計算 |
| `ATR` | `(Length:Num): Num` | 平均真實區間 `Average(TrueRange,Length)` |
| `BollingerBand` | `(price:Series, length:Num, _band:Num): Num` | 布林通道 = `MA + _band*標準差`（`_band` 正→上軌、負→下軌） |
| `BollingerBandWidth` | `(Price:Series, Length:Num, UpperBand:Num, LowerBand:Num): Num` | 布林帶寬（%） |
| `PercentB` | `(Price:Series, Length:Num, UpperBand:Num, LowerBand:Num): Num` | %b（價格在帶內位置 %） |
| `PercentR` | `(Length:Num): Num` | 威廉指標 %R |
| `KeltnerMA` | `(n:Num): Num` | 肯特納中軌（`XAverage(Close,n)`） |
| `KeltnerUB` | `(Para:Num): Num` | 肯特納上軌（中軌 + ATR(20)*Para） |
| `KeltnerLB` | `(Para:Num): Num` | 肯特納下軌 |
| `SAR` | `(AFInitial:Num, AFIncrement:Num, AFMax:Num): Num` | 拋物線 SAR 停損轉向 |
| `TRIX` | `(price:Series, length:Num): Num` | 三重指數平滑變化率 |
| `Momentum` | `(price:Series, length:Num): Num` | 運動量 `price - price[length]` |
| `MTM` | `(Length:Num): Num` | 收盤運動量 `Momentum(Close,Length)` |
| `MTM_MA` | `(Length:Num): Num` | MTM 再取平均 |
| `MO` | `(Length:Num): Num` | 運動量震盪（相對，`100*C/C[L]`） |
| `MAM` | `(Length:Num, Distance:Num): Num` | 當期均線 − Distance 期前均線 |
| `MA_Osc` | `(Length1:Num, Length2:Num): Num` | 兩條均線差（均線擺盪） |
| `ACC` | `(Length:Num): Num` | 加速量（Momentum 二次） |
| `Bias` | `(length:Num): Num` | 乖離率（%） |
| `BiasDiff` | `(length1:Num, length2:Num): Num` | 短長期乖離率差 |
| `RC` | `(Length:Num): Num` | 變動率 `(C-C[L])/C[L]` |
| `ERC` | `(Length:Num, EMALength:Num): Num` | RC 的指數平滑 |
| `DPO` | `(Length:Num): Num` | 非趨勢價格擺盪 |
| `VHF` | `(Length:Num): Num` | 趨向關係指標 |
| `MI` | `(Length:Num, SumLength:Num): Num` | 質量指標 |
| `PSY` | `(Length:Num): Num` | 心理線（上漲期數比例 %） |
| `AR` | `(Length:Num): Num` | 人氣指標 |
| `BR` | `(Length:Num): Num` | 買賣意願指標 |
| `ADI` | `(): Num` | 累積/派發（漲跌力道累積） |
| `ADO` | `(): Num` | 聚散擺盪 |
| `HL_Osc` | `(): Num` | HL 擺盪 `100*(H-C[1])/TrueRange` |
| `WAD` | `(): Num` | 威廉 A/D |
| `EMP` | `(): Num` | 多期均價平均（3/6/12/24） |
| `PVC` | `(Length:Num): Num` | 量價變化（% vs N 期均量） |
| `TurnOverRate` | `(period:Num): Num` | 週轉率（%，需股本欄位） |
| `VR` | `(Length:Num): Num` | 容量比率（上漲量/下跌量） |
| `VA` | `(): Num` | 量能累積（`VA[1]+VAO`） |
| `VAO` | `(): Num` | 單根量能值 |
| `VVA` | `(): Num` | VVA 量能指標 |
| `VPT` | `(): Num` | 量價趨勢（PVT） |
| `CV` | `(): Num` | 收盤×量累積 |
| `KO成交量擺盪指標` | `(Length1:Num, Length2:Num): Num` | KO 量能擺盪（中文名；回傳走 `ret`） |
| `KST確認指標` | `(): Num` | KST 指標（中文名；`ret`） |
| `Q指標` | `(t1:Num, t2:Num, t3:Num): Num` | Q 指標（中文名；`ret`） |
| `TechScore` | `(): Num` | 多空綜合分數：彙整 ~16 種指標多空計數（0…N，`ret`） |

---

## 5. 趨勢分析（趨勢分析/）

> 來源：`XScript_Preset/函數/趨勢分析/*.xs`

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `LinearReg` | `(thePrice:Series, Length:Num, target:Num, _slope:Ref↑, _angle:Ref↑, intercept:Ref↑, forecast:Ref↑): 狀態` | 線性回歸：回填斜率/弧度/截距/`target`日預測值（target 0=現在、-1=未來一天、1=過去一天） |
| `LinearRegSlope` | `(thePrice:Series, Length:Num): Num` | 回歸斜率 |
| `LinearRegAngle` | `(thePrice:Series, Length:Num): Num` | 回歸弧度 |
| `TimeSeriesForecast` | `(thePrice:Series, Length:Num, TgtBar:Num): Num` | 線性回歸外推預測值 |
| `Angle` | `(Date1:Num, Date2:Num): Num` | 兩日期連線的角度 |
| `Angleprice` | `(Date1:Num, ang:Num): Num` | 由角度反推目標價 |
| `NDaysAngle` | `(Length:Num): Num` | N 日走勢角度（上漲 0~90、下跌 0~-90；`ret`） |
| `SwingHigh` | `(Price:Series, Length:Num, LeftStrength:Num, RightStrength:Num, occur:Num): Num` | 第 occur 個波段高點「值」（無則 -1） |
| `SwingHighBar` | `(同上): Num` | 第 occur 個波段高點 K 棒 offset |
| `SwingLow` | `(同上): Num` | 第 occur 個波段低點值 |
| `SwingLowBar` | `(同上): Num` | 第 occur 個波段低點 K 棒 offset |
| `UpTrend` | `(TheSeries:Series, Length:Num): Bool` | 序列是否上升趨勢（判均線；需 2×Length 資料，建議僅最新筆呼叫） |
| `DownTrend` | `(TheSeries:Series, Length:Num): Bool` | 序列是否下降趨勢（同上注意事項） |
| `UpShadow` | `(): Num` | 上影線佔實體（range）比例 |
| `TSELSindex` | `(Length:Num, LowLimit:Num): Num` | 大盤外資多空（連續買超→1，否則 0） |
| `TSEMFI` | `(): Num` | 大盤資金流量 MFI 多空（>50→1，否則 0） |

> ⚠️ `UpTrend`/`DownTrend` 源碼註解的標準用法：`SetBackBar(2*Length); SetTotalBar(2); if CurrentBar <> GetTotalBar() then return; ret = UpTrend(Close, Length);`

---

## 6. 統計分析（統計分析/）

> 來源：`XScript_Preset/函數/統計分析/*.xs`

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `StandardDev` | `(thePrice:Series, Length:Num, DataType:Num): Num` | 標準差（`DataType`=1 母體、0 樣本） |
| `VariancePS` | `(thePrice:Series, Length:Num, DataType:Num): Num` | 變異數（母體/樣本） |
| `CoefficientR` | `(Indep:Series, Dep:Series, Length:Num): Num` | 相關係數 r（-1~1，皮爾森） |
| `Correlation` | `(Indep:Series, Dep:Series, Length:Num): Num` | 同向比率相關（自定義法，-1~1） |
| `RSquare` | `(Indep:Series, Dep:Series, Length:Num): Num` | 判定係數 R² = `CoefficientR²` |
| `Covariance` | `(DepValue:Series, IndepVal:Series, Length:Num): Num` | 共變異數 |

---

## 7. 邏輯判斷（邏輯判斷/）

> 來源：`XScript_Preset/函數/邏輯判斷/*.xs`。`CountIfARow` 與 `TrueCount` 同義（由近往遠連續計數）。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `IFF` | `(Logicoperator:TFSimple, TrueReturnV:Num, FalseReturnV:Num): Num` | 三元選值（條件真回前者、否則後者） |
| `CountIF` | `(TrueAndFalse:TFSeries, Length:Num): Num` | N 期內條件成立**總次數** |
| `CountIfARow` | `(TrueAndFalse:TFSeries, Length:Num): Num` | 由最近往回**連續**成立次數 |
| `TrueCount` | `(TrueAndFalse:TFSeries, Length:Num): Num` | 同 `CountIfARow` |
| `TrueAll` | `(TrueAndFalse:TFSeries, Length:Num): Bool` | N 期是否**全部**成立 |
| `TrueAny` | `(TrueAndFalse:TFSeries, Length:Num): Bool` | N 期是否**任一**成立 |
| `SummationIF` | `(TrueAndFalse:TFSeries, thePrice:Series, Length:Num): Num` | 條件成立期間的 thePrice 加總 |
| `AverageIF` | `(TrueAndFalse:TFSeries, thePrice:Series, Length:Num): Num` | 條件成立期間的 thePrice 平均 |
| `CrossOver` | `(SeriesA:Series, SeriesB:Series): Bool` | A 向上穿越 B（黃金交叉） |
| `CrossUnder` | `(SeriesA:Series, SeriesB:Series): Bool` | A 向下穿越 B（死亡交叉） |
| `Filter` | `(pX:TFSimple, pLength:Num): Bool` | 訊號去抖：成立後 pLength 根內不再放行 |
| `IsXOrder` | `(pv:Num): Bool` | 成交金額 `pv` 是否為**大單**（大+特大；依開盤價級距，用 `intraBarPersist` 跨 tick） |
| `IsXLOrder` | `(pv:Num): Bool` | 成交金額 `pv` 是否為**特大單** |

> ⚠️ `IsXOrder`/`IsXLOrder` 是逐筆洗價情境的典型 `intraBarPersist` 用法，見 [language.md](language.md) §7。

---

## 8. 日期相關（日期相關/）

> 來源：`XScript_Preset/函數/日期相關/*.xs`

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `BarsLast` | `(pX:TFSeries): Num` | 距上次條件 `pX` 成立經過幾根 K 棒 |
| `DateTime` | `(): Num` | `Date*1000000 + Time` 合併數值 |
| `DaysToExpiration` | `(_ExpiredM:Num, _ExpiredY:Num): Num` | 資料日距該月台指期到期日天數 |
| `GetLastTradeDate` | `(_ExpiredM:Num, _ExpiredY:Num): Num` | 台指期結算日（該月第 3 個週三，不計假日） |
| `GetBarOffsetForYears` | `(years:Num): Num` | N 年前對應的 BarOffset（超出範圍回 0） |
| `LastDayOfMonth` | `(SelectedMonth:Num): Num` | 指定月份最後一天的「日」數 |
| `NthDayOfMonth` | `(StartDate:Num, Nth:Num, TargetDay:Num): Num` | 自 StartDate 起第 Nth 個星期 TargetDay 的日期 |
| `FormatMQY` | `(Date1:Num): Str` | 依當前頻率格式化年/月/季字串（function_string） |

---

## 9. 期權相關（期權相關/）

> 來源：`XScript_Preset/函數/期權相關/*.xs`。Greeks 單一函數共用同一組 BS 參數。
> BS 參數：`iCallPutFlag`（"C"買權/"P"賣權）、`iSpotPrice` 標的價、`iStrikePrice` 履約價、
> `iDtoM` 到期天數、`iRate100` 無風險利率(%)、`iB100` 持有成本(%)、`iVolity100` 波動率(%)。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `BlackScholesModel` | `(iCallPutFlag:Str, iSpotPrice:Num, iStrikePrice:Num, iDtoM:Num, iRate100:Num, iB100:Num, iVolity100:Num, oOptPriceValue:Ref↑, oDelta:Ref↑, oGamma:Ref↑, oVega:Ref↑, oTheta:Ref↑, oRho:Ref↑): 狀態` | BS 模型：一次回填理論價與全部 Greeks |
| `BSPrice` | `(…7 個 BS 參數): Num` | 理論價 |
| `BSDelta` | `(…7 個 BS 參數): Num` | Delta |
| `BSGamma` | `(…7 個 BS 參數): Num` | Gamma |
| `BSVega` | `(…7 個 BS 參數): Num` | Vega |
| `BSTheta` | `(…7 個 BS 參數): Num` | Theta |
| `IVolatility` | `(iCallPutFlag:Str, iSpotPrice:Num, iStrikePrice:Num, iDtoM:Num, iRate100:Num, iB100:Num, iPrice:Num): Num` | 隱含波動率（用市價 `iPrice` 反解） |
| `HVolatility` | `(thePrice:Series, Length:Num): Num` | 歷史波動率（%，年化 √260） |
| `DaysToExpirationTF` | `(): Num` | 由商品代碼推算台股期/權到期天數 |
| `NormSDist` | `(zvalue:Num): Num` | 標準常態累積分配近似值 |

---

## 10. 量能相關（量能相關/）

> 來源：`XScript_Preset/函數/量能相關/*.xs`。⚠️ LxL/XL 兩支**僅支援 1 分鐘頻率**（否則 runtime error）。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `DiffBidAskVolumeLxL` | `(): Num` | 近 15 分鐘大戶（大單+特大單）買賣超（=「流動大戶買賣力」指標） |
| `DiffBidAskVolumeXL` | `(): Num` | 近 15 分鐘特大單買賣超 |
| `DiffTradeVolumeAtAskBid` | `(): Num` | 外盤量 − 內盤量（分時買賣力） |
| `DiffUpDownVolume` | `(): Num` | 上漲量 − 下跌量（分時漲跌成交量） |

---

## 11. 排行（排行/）

> 來源：`XScript_Preset/函數/排行/*.xs`。**這些是「自訂排行條件」範本**（中文名，回傳走 `retval`），
> 用於 XS 選股自訂排行情境（依回傳值排序）；內部以 `GetField()` 取欄位，使用者可替換欄位。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `收盤價排行榜` | `(): Num` | 回傳 `GetField("收盤價")`（範本：可換成漲跌幅等任一欄位） |
| `收盤均價排行榜` | `(Length:Num=3): Num` | N 期均價（範本） |
| `漲幅排行榜` | `(Length:Num=20): Num` | N 期漲幅 `RateOfChange(收盤價,Length)` |
| `跌幅排行榜` | `(Length:Num=20): Num` | N 期跌幅（漲幅取負） |
| `乖離率排行榜` | `(Length:Num=5): Num` | `Bias(Length)` |
| `外資連續買超排行榜` | `(Length:Num=10): Num` | 連續 Length 期外資買超→買超總和入榜，否則不入榜 |

> 註：簽名 `Length:Num=10` 表示該 input 在源碼有預設值（`input: Length(10, numericsimple, "計算期間")`）。

---

## 12. Array 函數（Array函數/）

> 來源：`XScript_Preset/函數/Array函數/*.xs`。回填型，最新一期慣例放 `TargetArray[1]`。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `ArraySeries` | `(TheSeries:Series, Length:Num, TargetArray:ArrayRef↑)` | 把序列前 Length 值寫入陣列（`[1]`=當期、`[2]`=前一期…） |
| `ArrayMASeries` | `(TheSeries:Series, MALength:Num, TargetArray:ArrayRef↑)` | 把序列的 MA(MALength) 序列寫入陣列（`[1]`=當期 MA…） |
| `ArrayXDaySeries` | `(TheSeries:Series, SBB_length:Num, TargetArray:ArrayRef↑)` | 把跨頻率序列存入陣列（搭配 `SetBackBar`） |
| `ArrayLinearRegSlope` | `(ThePriceArray:Array, Length:Num): Num` | 對陣列做線性回歸斜率（最新在 `[1]`；`ret`） |

---

## 13. 交易相關（交易相關/）

> 來源：`XScript_Preset/函數/交易相關/*.xs`

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `EnterMarketCloseTime` | `(exit_period:Num): Bool` | 是否已進入「收盤前 exit_period 分鐘」階段（僅台股/台期；用來停止進場或平倉當沖） |
| `CalcVWAPDistribution` | `(totaldays:Num, start_hhmmss:Num, end_hhmmss:Num, dist_array:ArrayRef↑)` | 計算過去 N 日指定時段每分鐘**累積成交量 %** 分佈，填入 `dist_array`（不支援跨日） |

---

## 14. 跨頻率（跨頻率/）

> 來源：`XScript_Preset/函數/跨頻率/*.xs`。第一個參數一律 `FreqType:Str`（引用頻率）。
> - **`xf_*`**：`FreqType` 支援 `"D"`/`"W"`/`"M"`。
> - **`xfMin_*`**：`FreqType` 額外支援分鐘頻率（`"1"/"2"/"3"/"5"/"10"/"15"/"30"/"60"/"D"/"W"/"M"/"AD"/"AW"/"AM"`），但**不支援 XS 選股、自訂排行、選股回測**（呼叫會 runtime error）。
> `xfMin_*` 與同名 `xf_*` 簽名相同，差別僅 `FreqType` 支援範圍與上述限制。

| 名稱（xf_ / xfMin_） | 簽名 | 說明 |
|------|------|------|
| `xf_GetValue` / `xfMin_GetValue` | `(FreqType:Str, PriceSeries:Series, poi:Num): Num` | 取跨頻數值序列第 poi 筆 |
| `xf_GetBoolean` / `xfMin_GetBoolean` | `(FreqType:Str, TFSeries:TFSeries, poi:Num): Bool` | 取跨頻布林序列第 poi 筆 |
| `xf_GetCurrentBar` / `xfMin_GetCurrentBar` | `(FreqType:Str): Num` | 指定頻率的 CurrentBar 編號 |
| `xf_GetDTValue` / `xfMin_GetDTValue` | `(FreqType:Str, dtValue:Num): Num` | 日期正規化值（判斷是否已跨期） |
| `xf_WeightedClose` / `xfMin_WeightedClose` | `(FreqType:Str): Num` | 跨頻加權收盤 |
| `xf_EMA` / `xfMin_EMA` | `(FreqType:Str, Series:Series, Length:Num): Num` | 跨頻 EMA |
| `xf_XAverage` / `xfMin_XAverage` | `(FreqType:Str, Series:Series, Length:Num): Num` | 跨頻 XAverage |
| `xf_RSI` / `xfMin_RSI` | `(FreqType:Str, Series:Series, Length:Num): Num` | 跨頻 RSI |
| `xf_PercentR` / `xfMin_PercentR` | `(FreqType:Str, Length:Num): Num` | 跨頻威廉指標 |
| `xfmin_MTM` | `(FreqType:Str, Length:Num): Num` | 跨頻 MTM（僅 xfMin 版） |
| `xf_CrossOver` / `xfMin_CrossOver` | `(FreqType:Str, SeriesA:Series, SeriesB:Series): Bool` | 跨頻向上穿越 |
| `xf_CrossUnder` / `xfMin_CrossUnder` | `(FreqType:Str, SeriesA:Series, SeriesB:Series): Bool` | 跨頻向下穿越 |
| `xf_MACD` / `xfMin_MACD` | `(FreqType:Str, Price:Series, FastLength:Num, SlowLength:Num, MACDLength:Num, DifValue:Ref↑, MACDValue:Ref↑, OscValue:Ref↑): (out)` | 跨頻 MACD |
| `xf_Stochastic` / `xfMin_Stochastic` | `(FreqType:Str, Length:Num, rsvt:Num, kt:Num, rsv:Ref↑, k:Ref↑, d:Ref↑): 狀態` | 跨頻 KD |
| `xf_DirectionMovement` / `xfMin_DirectionMovement` | `(FreqType:Str, length:Num, pdi_value:Ref↑, ndi_value:Ref↑, adx_value:Ref↑): (out)` | 跨頻 DMI |

---

## 重點函數詳解（含範例）

最常用函數的可貼用範例。範例皆取自 Preset 函數彼此呼叫的真實寫法。

### 移動平均族

```xs
value1 = Average(Close, 20);      // 20 日簡單均線 SMA
value2 = XAverage(Close, 12);     // 12 日指數均線 EMA
value3 = WMA(Close, 10);          // 10 日加權均線
value4 = Summation(Volume, 5);    // 近 5 根量加總
```

### 極值

```xs
value1 = Highest(High, 20);       // 近 20 根最高價
value2 = Lowest(Low, 20);         // 近 20 根最低價
value3 = HighestBar(High, 20);    // 最高價所在 K 棒 offset（0=當根）
```

### 穿越（回傳布林，可直接當條件）

```xs
if CrossOver(Close, Average(Close, 20)) then
    // 收盤向上穿越 20MA（黃金交叉）
    ;
if CrossUnder(Close, Average(Close, 20)) then
    // 死亡交叉
    ;
```

### MACD（多輸出 → 先宣告變數再傳入）

```xs
var: dif(0), macd(0), osc(0);
MACD(Close, 12, 26, 9, dif, macd, osc);
// dif=快慢線差、macd=訊號線、osc=柱狀體
if osc > 0 then { 多方 } ;
```

### KD（Stochastic，多輸出）

```xs
var: rsv(0), k(0), d(0);
Stochastic(9, 3, 3, rsv, k, d);   // 9 期、K 平滑 3、D 平滑 3
if k > d and k < 80 then { K 向上且未過熱 } ;
```

### DMI（DirectionMovement，多輸出）

```xs
var: pdi(0), ndi(0), adx(0);
DirectionMovement(14, pdi, ndi, adx);
if pdi > ndi then { 多方趨勢 } ;
```

### RSI / 布林 / ATR

```xs
value1 = RSI(Close, 14);                 // RSI
value2 = BollingerBand(Close, 20, 2);    // 布林上軌（+2 標準差）
value3 = BollingerBand(Close, 20, -2);   // 布林下軌（-2 標準差）
value4 = ATR(14);                        // 平均真實區間
```

### 條件統計

```xs
value1 = CountIf(Close > Close[1], 5);              // 近 5 根上漲次數
value2 = TrueAll(Volume > Volume[1], 3);            // 近 3 根是否量量遞增（布林）
value3 = SummationIf(Close > Open, Volume, 10);     // 近 10 根紅K的量加總
value4 = IFF(Close > Open, 1, -1);                  // 三元選值
```

---

## 待補 / 校對

> 以下皆為 **build-time（蒸餾 session）** 工作，須實際編輯本檔。
> ⚠️ **不會由 runtime F3 自動完成** —— F3 只補使用者單次提問、查完即丟，**不回寫 reference**（見 SPEC Out of Scope「不建立自動全量同步」）。

- [x] `SetBarMode(n)` 各值精確語意 → **已補**（見開頭共通慣例第 4 點：0=Auto / 1=Simple / 2=Series，xshelp 一手校對）。
- [ ] `xshelp` 系統函數清單若有 Preset 未涵蓋者（例如 `GetBarOffset` 本體於日期/跨頻多處被呼叫，但分類在 bif/欄位），於 `builtin-functions.md` 蒸餾時交叉補上。
- [ ] 各函數官方中文說明文字：於後續蒸餾 session 用 xshelp 對應頁面 WebFetch 回填校對（動作是蒸餾，非 runtime F3）。
