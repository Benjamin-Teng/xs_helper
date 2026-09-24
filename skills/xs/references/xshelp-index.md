# xshelp 名稱索引

> 由 xshelp 官方站索引 API 產生（2026-09-24，共 1621 筆），只收名稱與分組，不含官方說明內容。
> **用法：用搜尋找名稱，不要整份讀入。** 名稱不在本檔＝xshelp 查無，不得使用。
> 確認存在後，語法與說明用 `https://xshelp.xq.com.tw/XSHelp/rest?a=<名稱>` 取回 JSON（**中文名稱需先 URL-encode**，未編碼查無結果）；`name` 完全相符者可能不只一筆（同名分屬多個分組），依分組代碼（`Description`）比對目前所需的大類挑出正確那筆，讀 `desc`（語法）與 `fulldesc`（說明）；
> 給使用者的連結用 `https://xshelp.xq.com.tw/XSHelp/?HelpName=<名稱>&group=<分組代碼>`（中文名需 URL-encode）。
> 重生：`python -B scripts/xshelp_mirror.py fetch` 後 `python -B scripts/xshelp_mirror.py index`。

## 流程控制（37）

### CONTROLFLOW 流程控制（37）

`Above` · `And` · `Begin` · `Below` · `break` · `case` · `Cross` · `Cross Above` · `Cross Below` · `Cross Over` · `Cross Under` · `Crosses` · `Crosses Above` · `Crosses Below` · `Crosses Over` · `Crosses Under` · `default` · `DownTo` · `Else` · `End` · `False` · `For` · `If` · `Not` · `once` · `Or` · `Over` · `repeat` · `return` · `switch` · `Then` · `To` · `True` · `Under` · `until` · `While` · `Xor`

## 宣告（51）

### DECLARATION 宣告（51）

`Adjusted` · `Array` · `Arrays` · `Asc` · `axis` · `Bool` · `checkbox` · `daterange` · `Default` · `Desc` · `dict` · `Double` · `Float` · `Group` · `Input` · `inputkind` · `Inputs` · `Int` · `IntraBarPersist` · `Numeric` · `NumericArray` · `NumericArrayRef` · `NumericRef` · `NumericSeries` · `NumericSimple` · `order` · `param` · `quickedit` · `Rank` · `Ret` · `RetMsg` · `RetSound` · `RetVal` · `String` · `StringArray` · `StringArrayRef` · `StringRef` · `StringSeries` · `StringSimple` · `SymbolGroup` · `symbolprice` · `TrueFalse` · `TrueFalseArray` · `TrueFalseArrayRef` · `TrueFalseRef` · `TrueFalseSeries` · `TrueFalseSimple` · `Var` · `Variable` · `Variables` · `Vars`

## 常數（8）

### CONSTANT 常數（8）

`Friday` · `Monday` · `PI` · `Saturday` · `Sunday` · `Thursday` · `Tuesday` · `Wednesday`

## 忽略字（14）

### SKIPWORD 忽略字（14）

`A` · `An` · `At` · `Based` · `By` · `Does` · `From` · `Is` · `Of` · `On` · `Place` · `Than` · `The` · `Was`

## 內建函數（220）

### ARRAYFUNC 陣列函數（9）

`Array_Compare` · `Array_Copy` · `Array_GetMaxIndex` · `Array_GetType` · `Array_SetMaxIndex` · `Array_SetValRange` · `Array_Sort` · `Array_Sort2d` · `Array_Sum`

### DATEFUNC 日期函數（16）

`CurrentDate` · `DateAdd` · `DateDiff` · `DateToJulian` · `DateToString` · `DateValue` · `DayOfMonth` · `DayOfWeek` · `EncodeDate` · `FormatDate` · `JulianToDate` · `Month` · `StringToDate` · `WeekOfMonth` · `WeekOfYear` · `Year`

### FIELDFUNC 欄位函數（17）

`CheckField` · `CheckSymbolField` · `GetField` · `GetFieldDate` · `GetfieldFiscalQ` · `GetfieldFiscalY` · `GetFieldPublishDate` · `GetQuote` · `GetSymbolField` · `GetSymbolFieldDate` · `GetSymbolFieldTime` · `GetSymbolInfo` · `IsSupportField` · `IsSupportSymbolField` · `Symbol` · `SymbolName` · `UserID`

### GENERALFUNC 一般函數（47）

`BarAdjusted` · `BarFreq` · `BarInterval` · `CallFunction` · `CurrentBar` · `DataAlign` · `ExecOffset` · `File` · `GetBackBar` · `GetBarBack` · `GetBarOffset` · `GetFieldStartOffset` · `GetFirstBarDate` · `GetInfo` · `GetSymbolFieldStartOffset` · `GetSymbolGroup` · `GetTBMode` · `GetTotalBar` · `GroupSize` · `IsFirstCall` · `IsLastBar` · `IsSessionFirstBar` · `IsSessionLastBar` · `MaxBarsBack` · `NoPlot` · `OutputField` · `Playsound` · `Plot` · `PlotFill` · `PlotK` · `PlotLine` · `Print` · `RaiseRunTimeError` · `SetAlign` · `SetBackBar` · `SetBarBack` · `SetBarFreq` · `SetBarMode` · `SetFirstBarDate` · `SetInputName` · `SetOutputName` · `SetPlotLabel` · `SetRemoveOutlier` · `SetTBMode` · `SetTotalBar` · `SymbolExchange` · `SymbolType`

### NUMBERFUNC 數學函數（37）

`AbsValue` · `ArcCosine` · `ArcSine` · `ArcTangent` · `AvgList` · `Ceiling` · `Combination` · `Cos` · `Cosine` · `CoTangent` · `ExpValue` · `Factorial` · `Floor` · `FracPortion` · `IntPortion` · `Log` · `MaxList` · `MaxList2` · `MinList` · `MinList2` · `Mod` · `Neg` · `NthMaxList` · `NthMinList` · `Permutation` · `Pos` · `Power` · `Random` · `Round` · `Sign` · `Sin` · `Sine` · `Square` · `SquareRoot` · `SumList` · `Tan` · `Tangent`

### SDTFUNC SDT函數（38）

`SDT_Average` · `SDT_Average_L` · `SDT_GetKeys` · `SDT_GetKeys_L` · `SDT_GetString` · `SDT_GetString_L` · `SDT_GetValue` · `SDT_GetValue_L` · `SDT_HasKey` · `SDT_HasKey_L` · `SDT_Max` · `SDT_Max_L` · `SDT_Median` · `SDT_Median_L` · `SDT_Min` · `SDT_Min_L` · `SDT_RemoveAll` · `SDT_RemoveAll_L` · `SDT_RemoveKey` · `SDT_RemoveKey_L` · `SDT_SetColumnName` · `SDT_SetColumnName_L` · `SDT_SetString` · `SDT_SetString_L` · `SDT_SetStringIf` · `SDT_SetStringIf_L` · `SDT_SetValue` · `SDT_SetValue_L` · `SDT_SetValueIf` · `SDT_SetValueIf_L` · `SDT_Sort` · `SDT_Sort_L` · `SDT_SortKey` · `SDT_SortKey_L` · `SDT_SortString` · `SDT_SortString_L` · `SDT_Sum` · `SDT_Sum_L`

### STRINGFUNC 字串函數（15）

`InStr` · `LeftStr` · `LowerStr` · `MidStr` · `NumToStr` · `RightStr` · `StrCompare` · `StrEndWith` · `StrLen` · `StrSplit` · `StrStartWith` · `StrToNum` · `StrTrim` · `Text` · `UpperStr`

### TIMEFUNC 時間函數（13）

`CurrentTime` · `CurrentTimeMS` · `EncodeTime` · `FormatTime` · `Hour` · `MilliSecond` · `Minute` · `Second` · `StringToTime` · `TimeAdd` · `TimeDiff` · `TimeToString` · `TimeValue`

### TRANSACTIONFUNC 交易函數（28）

`AddSpread` · `Alert` · `Buy` · `CancelAllOrders` · `Cover` · `DefaultBuyPrice` · `DefaultSellPrice` · `Filled` · `FilledAtBroker` · `FilledAvgPrice` · `FilledEntryDate` · `FilledEntryTime` · `FilledEntryTimeMS` · `FilledRecordBS` · `FilledRecordCount` · `FilledRecordDate` · `FilledRecordIsRealtime` · `FilledRecordPrice` · `FilledRecordQty` · `FilledRecordTime` · `FilledRecordTimeMS` · `IsListedSymbol` · `IsMarketPrice` · `Market` · `Position` · `Sell` · `SetPosition` · `Short`

## 系統函數（267）

### ARRAYSYSFUNC Array函數（4）

`ArrayLinearRegSlope` · `ArrayMASeries` · `ArraySeries` · `ArrayXDaySeries`

### DATERELFUNC 日期相關（10）

`angleprice` · `BarsLast` · `DaysToExpiration` · `DownTrend` · `formatMQY` · `GetLastTradeDate` · `LastDayOfMonth` · `NDaysAngle` · `NthDayofMonth` · `UpTrend`

### FREQUENCYFUNC 跨頻率（29）

`xf_CrossOver` · `xf_CrossUnder` · `xf_DirectionMovement` · `xf_EMA` · `xf_GetBoolean` · `xf_GetCurrentBar` · `xf_GetDTValue` · `xf_GetValue` · `xf_MACD` · `xf_PercentR` · `xf_RSI` · `xf_Stochastic` · `xf_WeightedClose` · `xf_XAverage` · `xfMin_CrossOver` · `xfMin_CrossUnder` · `xfMin_DirectionMovement` · `xfMin_EMA` · `xfMin_GetBoolean` · `xfMin_GetCurrentBar` · `xfMin_GetDTValue` · `xfMin_GetValue` · `xfMin_MACD` · `xfmin_MTM` · `xfMin_PercentR` · `xfMin_RSI` · `xfMin_Stochastic` · `xfMin_WeightedClose` · `xfMin_XAverage`

### FUTUREFUNC 期權相關（12）

`blackscholesmodel` · `BSDelta` · `BSGamma` · `BSPrice` · `BSTheta` · `BSVega` · `DaysToExpirationTF` · `HVolatility` · `IsXLOrder` · `IsXOrder` · `IVolatility` · `NORMSDIST`

### LOGICFUNC 邏輯判斷（13）

`AverageIF` · `CountIf` · `CountIfARow` · `CrossOver` · `CrossUnder` · `DateTime` · `Filter` · `GetBarOffsetForYears` · `IFF` · `SummationIf` · `TrueAll` · `TrueAny` · `TrueCount`

### PRICECULFUNC 價格計算（13）

`Average` · `AvgDeviation` · `DwLimit` · `EMA` · `Range` · `RateOfChange` · `SimpleHighestBar` · `SimpleLowestBar` · `Summation` · `TrueRange` · `UpLimit` · `WMA` · `XAverage`

### PRICEGETFUNC 價格取得（33）

`AvgPrice` · `CloseD` · `CloseH` · `CloseM` · `CloseQ` · `CloseW` · `CloseY` · `FastHighest` · `FastLowest` · `HighD` · `Highest` · `HighH` · `HighM` · `HighQ` · `HighW` · `HighY` · `LowD` · `Lowest` · `LowH` · `LowM` · `LowQ` · `LowW` · `LowY` · `OpenD` · `OpenH` · `OpenM` · `OpenQ` · `OpenW` · `OpenY` · `TrueHigh` · `TrueLow` · `TypicalPrice` · `WeightedClose`

### PRICERELFUNC 價格關係（25）

`Extremes` · `ExtremesArray` · `FastHighestBar` · `FastLowestBar` · `HighDays` · `HighestArray` · `HighestBar` · `LowDays` · `LowestArray` · `LowestBar` · `MoM` · `NthExtremes` · `NthExtremesArray` · `NthHighest` · `NthHighestArray` · `NthHighestBar` · `NthLowest` · `NthLowestArray` · `NthLowestBar` · `OHLCPeriodsAgo` · `QoQ` · `ReadTicks` · `SimpleHighest` · `SimpleLowest` · `YoY`

### QUANTFACTOR 量化因子（51）

`10日內破低次數` · `10日內跌幅超過5%天數` · `120日賣出動能(Kiosotto)` · `150日買進動能(Kiosotto)` · `20日內破低次數` · `52週動能` · `52週動能_最高價` · `Andean Oscillator多頭(20)` · `Andean Oscillator空頭(120)` · `ATR_10日` · `calmar_ratio_250d` · `dd_ma_250d` · `Empty_line指標_20d` · `OBV MACD_OSC柱狀體` · `P_CFV` · `QMJ_safe` · `ROA_P` · `ROA_PB` · `ROE_P` · `ROE_PB` · `ROS_P` · `StochRSI_K` · `Wave Smoother` · `YZVolatility(14)` · `中單5日買賣超金額` · `主力10日內買超天數` · `主力20日籌碼區間買超賣超比` · `人氣指標AR_250` · `企業價值EV` · `借券賣出餘額張數` · `價量動能_20日` · `外資10日內賣超天數` · `外資10日買張佔股本比` · `大單20日買賣超金額` · `小單20日買賣超金額` · `最高價均價幅度` · `本益比5日變異` · `法人10日內賣超天數` · `流動性因子(成交值)` · `海龜20日潛在波動性` · `特大單5日買賣超金額` · `築底指標(ZDZB)` · `綜十10日內買超天數` · `股價毛利比_3` · `股價營利比_12` · `股價營收比_3` · `自由現金流量_P` · `自自20日內買超天數` · `自自20日籌碼區間買超賣超比` · `跌破5年線` · `高低動能_5日`

### STATSFUNC 統計分析（6）

`CoefficientR` · `Correlation` · `Covariance` · `RSquare` · `StandardDev` · `VariancePS`

### TECHINDEXFUNC 技術指標（53）

`ACC` · `ADI` · `ADO` · `AR` · `ATR` · `Bias` · `BiasDiff` · `BollingerBand` · `BollingerBandWidth` · `BR` · `CCI` · `CommodityChannel` · `D_Value` · `DIF` · `DirectionMovement` · `DMO` · `DPO` · `EMP` · `ERC` · `HL_Osc` · `K_Value` · `KeltnerLB` · `KeltnerMA` · `KeltnerUB` · `KO成交量擺盪指標` · `KST確認指標` · `MA_Osc` · `MACD` · `MAM` · `MI` · `MO` · `Momentum` · `MTM` · `MTM_MA` · `PercentB` · `PercentR` · `PSY` · `Q指標` · `RC` · `RSI` · `RSV` · `SAR` · `Stochastic` · `TechScore` · `TRIX` · `TurnOverRate` · `VA` · `VAO` · `VHF` · `VPT` · `VR` · `VVA` · `WAD`

### TRANSACTIONRELFUNC 交易相關（2）

`calcvwapdistribution` · `EnterMarketCloseTime`

### TRENDFUNC 趨勢分析（12）

`Angle` · `LinearReg` · `LinearRegAngle` · `LinearRegSlope` · `SwingHigh` · `SwingHighBar` · `SwingLow` · `SwingLowBar` · `TimeSeriesForecast` · `TSELSindex` · `TSEMFI` · `UpShadow`

### VOLUMERELFUNC 量能相關（4）

`DiffBidAskVolumeLxL` · `DiffBidAskVolumeXL` · `DiffTradeVolumeAtAskBid` · `DiffUpDownVolume`

## 報價欄位（131）

### QBASIC 基本（4）

`最小交易股數` · `發行股數` · `總市值(億)` · `股本(億)`

### QFINANCE 財務（10）

`每股淨值` · `每股營收` · `每股盈餘` · `毛利率` · `營收年增率` · `營收月份` · `營收期增率` · `營益率` · `股東權益報酬率` · `財報期別`

### QFIVE 五檔統計（26）

`委比` · `委買` · `委買1` · `委買2` · `委買3` · `委買4` · `委買5` · `委買賣差` · `委賣` · `委賣1` · `委賣2` · `委賣3` · `委賣4` · `委賣5` · `總委買` · `總委賣` · `買進1` · `買進2` · `買進3` · `買進4` · `買進5` · `賣出1` · `賣出2` · `賣出3` · `賣出4` · `賣出5`

### QMARKET 市場統計（4）

`上漲家數` · `下跌家數` · `漲停家數` · `跌停家數`

### QOFTEN 常用（12）

`估計量` · `參考價` · `單量` · `成交` · `成交時間` · `昨量` · `最低(日)` · `最高(日)` · `總量(日)` · `買進` · `賣出` · `開盤(日)`

### QOPTION 期權（28）

`Delta` · `Gamma` · `RHO` · `Theta` · `Vega` · `價內外百分比` · `內含值` · `到期日` · `剩餘交易日` · `剩餘日` · `執行比例` · `履約價` · `損益兩平` · `時間價值` · `最後交易日` · `有效槓桿` · `標的價格` · `標的漲跌` · `標的漲跌幅` · `波動率` · `波動率差額` · `溢價率百分比` · `獲利率百分比` · `理論價` · `買賣權成交量比率` · `買賣權未平倉量比率` · `買進隱含波動率` · `賣出隱含波動率`

### QPRICE 價格（18）

`一年前收盤價` · `一月前收盤價` · `一週前收盤價` · `三月前收盤價` · `價差` · `內外盤` · `前一價` · `前三價` · `前二價` · `前四價` · `去年收盤價` · `均價` · `基差` · `振幅` · `漲停價` · `漲跌幅` · `買賣價差百分比` · `跌停價`

### QUOTE 報價欄位（6）

`撮合狀態` · `暫緩撮合狀態` · `試搓成交價` · `試搓成交日期` · `試搓成交時間` · `試搓成交量`

### QVOLUME 量能（23）

`內盤量` · `外盤量` · `委買均` · `委賣均` · `成交均量` · `成交比重` · `成交金額(元)` · `累委買筆` · `累委賣筆` · `累成交筆` · `累計委買` · `累計委賣` · `累計成交` · `累買成筆` · `累賣成筆` · `總成交次數` · `量比` · `開盤委買` · `開盤委賣` · `開盤買均` · `開盤買筆` · `開盤賣均` · `開盤賣筆`

## 資料欄位（363）

### TA 資料欄位（5）

`撮合群組` · `累計每股盈餘(發佈值)` · `累計淨利(發佈值)` · `買賣現沖` · `轉換價格`

### TBASIC 基本（9）

`投資建議評級` · `月營收` · `本益比` · `殖利率` · `發行張數(張)` · `總市值(元)` · `股本(億)` · `股本(元)` · `財報股本(億)`

### TCHIP 籌碼（156）

`CB剩餘張數` · `主力成本` · `主力持股` · `主力累計買賣超金額` · `主力買張` · `主力買賣超張數` · `主力買進金額` · `主力賣出金額` · `主力賣張` · `主動性交易比重` · `主動買力` · `主動賣力` · `借券張數` · `借券賣出張數` · `借券賣出還券張數` · `借券賣出餘額張數` · `借券餘額張數` · `內部人持股` · `內部人持股張數` · `內部人持股比例` · `內部人持股異動` · `分公司交易家數` · `分公司淨買超金額家數` · `分公司淨賣超金額家數` · `分公司買進家數` · `分公司賣出家數` · `券資比` · `吉尼係數` · `地緣券商買賣超張數` · `外資成本` · `外資持股` · `外資持股比例` · `外資買張` · `外資買賣超` · `外資買賣超張數` · `外資買賣超金額` · `外資買進金額` · `外資賣出金額` · `外資賣張` · `大戶持股人數` · `大戶持股張數` · `大戶持股比例` · `官股券商累計買賣超金額` · `官股券商買賣超張數` · `官股券商買進金額` · `官股券商賣出金額` · `實戶買張` · `實戶買賣超張數` · `實戶賣張` · `實質買盤比` · `實質賣盤比` · `市場總分點數` · `庫藏股實際買回張數` · `庫藏股申請家數` · `庫藏股申請總市值` · `庫藏股預計買回張數` · `投信成本` · `投信持股` · `投信持股比例` · `投信買張` · `投信買賣超` · `投信買賣超張數` · `投信買賣超金額` · `投信買進金額` · `投信賣出金額` · `投信賣張` · `控盤者成本線` · `控盤者買張` · `控盤者買賣超張數` · `控盤者賣張` · `收集派發指標` · `散戶持股人數` · `散戶持股張數` · `散戶持股比例` · `散戶買張` · `散戶買賣超張數` · `散戶賣張` · `新產能預計量產日期` · `機構持股` · `機構持股比重` · `法人持股` · `法人持股比例` · `法人買張` · `法人買賣超` · `法人買賣超張數` · `法人買賣超金額` · `法人買進比重` · `法人買進金額` · `法人賣出比重` · `法人賣出金額` · `法人賣張` · `現券償還張數` · `現增比率` · `現增金額` · `現股當沖張數` · `現股當沖買進金額` · `現股當沖賣出金額` · `現金償還張數` · `申報人數` · `申報家數` · `申報總市值` · `當日沖銷張數` · `綜合前十大券商累計買賣超金額` · `綜合前十大券商買賣超張數` · `綜合前十大券商買進金額` · `綜合前十大券商賣出金額` · `總持股人數` · `自營商成本` · `自營商持股` · `自營商持股比例` · `自營商自行買賣買張` · `自營商自行買賣買賣超` · `自營商自行買賣買賣超金額` · `自營商自行買賣買進金額` · `自營商自行買賣賣出金額` · `自營商自行買賣賣張` · `自營商買張` · `自營商買賣超` · `自營商買賣超張數` · `自營商買賣超金額` · `自營商買進金額` · `自營商賣出金額` · `自營商賣張` · `自營商避險買張` · `自營商避險買賣超` · `自營商避險買賣超金額` · `自營商避險買進金額` · `自營商避險賣出金額` · `自營商避險賣張` · `董監持股佔股本比例` · `董監質設比例` · `融券使用率` · `融券增減張數` · `融券買進張數` · `融券賣出張數` · `融券餘額張數` · `融資使用率` · `融資增減` · `融資增減張數` · `融資增減金額` · `融資維持率` · `融資買進張數` · `融資買進金額` · `融資賣出張數` · `融資賣出金額` · `融資餘額` · `融資餘額張數` · `融資餘額金額` · `買家數` · `買進公司家數` · `資券互抵張數` · `賣出公司家數` · `賣家數` · `還券張數` · `關聯券商買賣超張數` · `關鍵券商買賣超張數`

### TEVENT 事件（29）

`停止轉換結束日` · `停止轉換起始日` · `庫藏股結束日期` · `庫藏股開始日期` · `新股上市日` · `最後交易日` · `最後過戶日期` · `法說會日期` · `減資新股上市日` · `減資日期` · `減資最後過戶日` · `減資比例` · `現增價格` · `現增新股上市日` · `現增最後過戶日` · `現增繳款日期` · `股東會日期` · `處置結束日期` · `處置開始日期` · `融券最後回補日` · `除息值` · `除息年度` · `除息日期` · `除權值` · `除權年度` · `除權息值` · `除權息年度` · `除權息日期` · `除權日期`

### TMARKET 市場統計（18）

`TW50KD多空家數` · `TW50MTM多空家數` · `TW50上昇趨勢家數` · `TW50價格上漲家數` · `TW50創新低家數` · `TW50創新高家數` · `TW50均線多空家數` · `TW50大單成交次數` · `TW50大單買進金額` · `TW50大戶買賣力` · `TW50紅K家數` · `上漲家數` · `下跌家數` · `內盤家數` · `外盤家數` · `漲停家數` · `跌停家數` · `騰落指標`

### TOFTEN 常用（17）

`估計量` · `內盤量` · `參考價` · `均價` · `外盤量` · `成交量` · `成交金額(元)` · `收盤價` · `日期` · `時間` · `最低價` · `最高價` · `漲停價` · `買入價` · `賣出價` · `跌停價` · `開盤價`

### TOPTION 期權（61）

`Delta` · `Gamma` · `RHO` · `Theta` · `Vega` · `三大法人交易買口` · `三大法人交易買進金額` · `三大法人交易賣出金額` · `三大法人交易賣口` · `三大法人買方未平倉` · `三大法人買方未平倉金額` · `三大法人賣方未平倉` · `三大法人賣方未平倉金額` · `五大交易人未沖銷買口` · `五大交易人未沖銷賣口` · `五大法人未沖銷買口` · `五大法人未沖銷賣口` · `估計除息點數` · `內含值` · `十大交易人未沖銷買口` · `十大交易人未沖銷賣口` · `十大法人未沖銷買口` · `十大法人未沖銷賣口` · `原始保證金` · `外資交易買口` · `外資交易買進金額` · `外資交易賣出金額` · `外資交易賣口` · `外資買方未平倉口數` · `外資買方未平倉金額` · `外資賣方未平倉口數` · `外資賣方未平倉金額` · `投信交易買口` · `投信交易買進金額` · `投信交易賣出金額` · `投信交易賣口` · `投信買方未平倉口數` · `投信買方未平倉金額` · `投信賣方未平倉口數` · `投信賣方未平倉金額` · `時間價值` · `未平倉` · `波動性指數` · `波動率` · `理論價` · `維持保證金` · `自營商交易買口` · `自營商交易買進金額` · `自營商交易賣出金額` · `自營商交易賣口` · `自營商買方未平倉口數` · `自營商買方未平倉金額` · `自營商賣方未平倉口數` · `自營商賣方未平倉金額` · `買權成交量` · `買權未平倉量` · `買賣權成交量比率` · `買賣權未平倉量比率` · `賣權成交量` · `賣權未平倉量` · `隱含波動率`

### TPRICE 價格（4）

`內外盤` · `基差` · `強弱指標` · `投資建議目標價`

### TVOLUME 量能（64）

`GDP比例` · `上漲量` · `下跌量` · `內盤均量` · `內盤成交次數` · `外盤均量` · `外盤成交次數` · `委買均` · `委賣均` · `成交均量` · `新聞正向分數` · `新聞聲量分數` · `新聞負向分數` · `漲停委買數量` · `漲停委買筆數` · `漲停委賣數量` · `漲停委賣筆數` · `當日序號` · `盤中整股成交量` · `盤中零股成交量` · `盤後量` · `累委買筆` · `累委賣筆` · `累成交筆` · `累計委買` · `累計委賣` · `累計成交` · `累買成筆` · `累賣成筆` · `總成交次數` · `買進中單成交次數` · `買進中單量` · `買進中單金額` · `買進大單成交次數` · `買進大單量` · `買進大單金額` · `買進小單成交次數` · `買進小單量` · `買進小單金額` · `買進特大單成交次數` · `買進特大單量` · `買進特大單金額` · `資金流向` · `賣出中單成交次數` · `賣出中單量` · `賣出中單金額` · `賣出大單成交次數` · `賣出大單量` · `賣出大單金額` · `賣出小單成交次數` · `賣出小單量` · `賣出小單金額` · `賣出特大單成交次數` · `賣出特大單量` · `賣出特大單金額` · `跌停委買數量` · `跌停委買筆數` · `跌停委賣數量` · `跌停委賣筆數` · `量比` · `開盤委買` · `開盤委賣` · `開盤買筆` · `開盤賣筆`

## 選股欄位（492）

### FBASIC 基本（31）

`公司成立日期` · `公司掛牌日期` · `公司類別` · `公司風格` · `公積配股` · `員工人數` · `員工配股率` · `填息天數` · `填權天數` · `投資建議評級` · `新產能預計量產日期` · `月營收年增率` · `月營收月增率` · `現金股利` · `現金股利佔股利比重` · `現金股利殖利率` · `發行張數(張)` · `發行張數(萬張)` · `盈餘配股` · `累計營收` · `累計營收年增率` · `總市值(元)` · `總經理` · `股利合計` · `股本(億)` · `股本(元)` · `股票股利` · `股票股利佔股利比重` · `股票股利殖利率` · `董事長` · `財報股本(億)`

### FCHIP 籌碼（117）

`CB剩餘張數` · `ETF規模` · `主力平均買超成本` · `主力平均賣超成本` · `主力成本` · `主力持股` · `主力買張` · `主力賣張` · `借券張數` · `借券賣出張數` · `借券賣出還券張數` · `借券賣出餘額張數` · `借券餘額張數` · `內部人持股` · `內部人持股張數` · `內部人持股比例` · `內部人持股異動` · `公積及其他佔股本比重` · `分公司交易家數` · `分公司淨買超金額家數` · `分公司淨賣超金額家數` · `分公司買進家數` · `分公司賣出家數` · `券資比` · `吉尼係數` · `地緣券商買賣超張數` · `外資成本` · `外資持股` · `外資持股比例` · `外資買張` · `外資買賣超` · `外資賣張` · `大戶持股人數` · `大戶持股張數` · `大戶持股比例` · `官股券商買賣超張數` · `實戶買張` · `實戶買賣超張數` · `實戶賣張` · `實質買盤比` · `實質賣盤比` · `庫藏股實際買回張數` · `庫藏股預計買回張數` · `投信成本` · `投信持股` · `投信持股比例` · `投信買張` · `投信買賣超` · `投信賣張` · `控盤者成本線` · `控盤者買張` · `控盤者買賣超張數` · `控盤者賣張` · `散戶持股人數` · `散戶持股張數` · `散戶持股比例` · `散戶買張` · `散戶買賣超張數` · `散戶賣張` · `機構持股` · `機構持股比重` · `法人持股` · `法人持股比例` · `法人買張` · `法人賣張` · `現券償還張數` · `現股當沖張數` · `現股當沖買進金額` · `現股當沖賣出金額` · `現金償還張數` · `現金增資佔股本比重` · `當日沖銷張數` · `盈餘轉增資佔股本比重` · `籌碼鎖定率` · `綜合前十大券商買賣超張數` · `總持股人數` · `股票基金持有檔數` · `自營商成本` · `自營商持股` · `自營商持股比例` · `自營商自行買賣買張` · `自營商自行買賣買賣超` · `自營商自行買賣賣張` · `自營商買張` · `自營商買賣超` · `自營商賣張` · `自營商避險買張` · `自營商避險買賣超` · `自營商避險賣張` · `董監持股` · `董監持股佔股本比例` · `董監質設比例` · `融券使用率` · `融券增減張數` · `融券買進張數` · `融券賣出張數` · `融券餘額佔股本比例` · `融券餘額張數` · `融資使用率` · `融資增減張數` · `融資維持率` · `融資買進張數` · `融資賣出張數` · `融資限額張數` · `融資餘額佔股本比例` · `融資餘額張數` · `買家數` · `買進公司家數` · `資券互抵張數` · `賣出公司家數` · `賣家數` · `週轉率` · `還券張數` · `關聯券商買賣超張數` · `關鍵券商買賣超張數` · `集保張數` · `集保張數佔發行張數百分比`

### FEVENT 事件（35）

`下一次董監改選年` · `停止轉換結束日` · `停止轉換起始日` · `庫藏股結束日期` · `庫藏股開始日期` · `新股上市日` · `日期` · `最後交易日` · `最後過戶日期` · `法說會日期` · `減資新股上市日` · `減資日期` · `減資最後過戶日` · `減資比例` · `現增價格` · `現增新股上市日` · `現增最後過戶日` · `現增比率` · `現增繳款日期` · `現增金額` · `股利年度` · `股東會日期` · `董監事就任日期` · `處置結束日期` · `處置開始日期` · `融券最後回補日` · `除息值` · `除息年度` · `除息日期` · `除權值` · `除權年度` · `除權息值` · `除權息年度` · `除權息日期` · `除權日期`

### FFINANCE 財務（209）

`(存貨+應收帳款)／營收` · `10年年化報酬率` · `1年夏普指數` · `1年年化報酬率` · `3年年化報酬率` · `5年年化報酬率` · `EPS法說公佈值` · `EPS預估值` · `一年內到期長期負債` · `企業價值` · `企業價值營收比` · `來自營運之現金流量` · `借款依存度` · `停業部門損益` · `兌換損失` · `兌換盈益` · `其他應付款` · `其他應收款` · `其他收入` · `其他流動負債` · `其他流動資產` · `其他資產` · `利息保障倍數` · `利息支出` · `利息支出率` · `利息收入` · `加權平均股數` · `合約負債` · `員工平均營業額(千元)` · `因子_QMJ安全` · `因子_QMJ獲利` · `因子_一年動能` · `因子_偏態係數` · `因子_前一年獲利` · `因子_前三年獲利` · `因子_前兩年獲利` · `因子_半年動能因子` · `因子_實現損益偏態係數` · `因子_帳面市值比` · `因子_彩券型需求` · `因子_成交值流動性` · `因子_日週轉率流動性` · `因子_最高價動能` · `因子_月週轉率流動性` · `因子_淨營運資產` · `因子_潛在上檔報酬比` · `因子_特質波動度` · `因子_現金流量波動度` · `因子_股票發行量` · `因子_貝他值` · `因子分數_QMJ安全` · `因子分數_QMJ獲利` · `因子分數_一年動能` · `因子分數_偏態係數` · `因子分數_前一年獲利` · `因子分數_前三年獲利` · `因子分數_前兩年獲利` · `因子分數_半年動能因子` · `因子分數_實現損益偏態係數` · `因子分數_帳面市值比` · `因子分數_彩券型需求` · `因子分數_成交值流動性` · `因子分數_日週轉率流動性` · `因子分數_最高價動能` · `因子分數_月週轉率流動性` · `因子分數_淨營運資產` · `因子分數_潛在上檔報酬比` · `因子分數_特質波動度` · `因子分數_現金殖利率` · `因子分數_現金流量波動度` · `因子分數_股東權益報酬率` · `因子分數_股票發行量` · `因子分數_貝他值` · `固定資產` · `固定資產報酬率` · `固定資產成長率` · `固定資產週轉率(次)` · `外幣換算調整數` · `外銷比率` · `存貨` · `存貨及應收帳款／淨值` · `存貨營收比` · `存貨週轉率(次)` · `市值營收比` · `市研率` · `常續性利益(稅後)` · `平均售貨天數` · `平均收帳天數` · `年報酬率` · `庫藏股票帳面值` · `應付商業本票` · `應付帳款付現天數` · `應付帳款及票據` · `應收帳款及票據` · `應收帳款週轉次數` · `應收帳款週轉率(次)` · `或有負債比率` · `所得稅費用` · `投資活動之現金流量` · `投資跌價損失` · `投資跌價損失回轉` · `推銷費用` · `普通股股本` · `有息負債利率` · `有效稅率` · `未分配盈餘` · `未完工程及預付款` · `本期稅後淨利` · `杜邦型ROA` · `杜邦型ROE` · `每人營業利益` · `每股流動淨資產` · `每股淨值(元)` · `每股營業利益(元)` · `每股營業額(元)` · `每股現金流量` · `每股稅前淨利(元)` · `每股自由現金流量` · `法定盈餘公積` · `流動比率` · `流動負債` · `流動資產` · `淨值成長率` · `淨值自由現金流量比` · `淨值週轉率` · `淨營業週期` · `無形資產` · `營收成長率` · `營業利益` · `營業利益成長率` · `營業利益率` · `營業外收入及支出` · `營業外收入合計` · `營業成本` · `營業收入淨額` · `營業毛利` · `營業現金流量／營業利益` · `營業費用` · `營業費用率` · `營運資金` · `特別盈餘公積` · `特別股股本` · `現金再投資％` · `現金及約當現金` · `現金派息比率` · `現金流量允當％` · `現金流量比率` · `理財活動之現金流量` · `用人費用率` · `當期財報截止日` · `盈餘成長係數` · `盈餘殖利率` · `盈餘營收成長率比` · `短期借支` · `短期借款` · `短期投資` · `研發費用` · `研發費用率` · `稀釋後每股淨利` · `稅前息前折舊前淨利` · `稅前息前淨利` · `稅前淨利` · `稅前淨利成長率` · `稅前淨利率` · `稅後淨利成長率` · `稅後淨利率` · `管理+銷售費用／營收` · `管理費用` · `管理費用／季營收` · `經常利益` · `總流通在外股數` · `總資產成長率` · `總資產週轉率(次)` · `聯屬公司間未實現銷貨` · `股價自由現金流量比` · `股利收入` · `股東權益總額` · `背書保證佔淨值比` · `背書保證餘額` · `自由現金流量` · `自由現金流量營收比` · `處分投資利得` · `處分投資損失` · `處分資產利得` · `處分資產損失` · `誠信指標` · `負債及股東權益總額` · `負債對淨值比率` · `負債比率` · `負債總額` · `資本公積` · `資本支出營收比` · `資本支出金額` · `資產報酬率` · `資產總額` · `資金貸放佔淨值比` · `資金貸放餘額` · `退休金準備` · `速動比率` · `遞延所得稅` · `遞延貸項` · `遞延資產` · `銷售費用比` · `長期投資` · `長期負債` · `長期資金適合率` · `長短期負債比率` · `預付費用及預付款` · `預收股款`

### FILTER 選股欄位（3）

`累計每股盈餘(發佈值)` · `累計淨利(發佈值)` · `買賣現沖`

### FOFTEN 常用（19）

`主力買賣超張數` · `均價` · `成交量` · `成交金額(億)` · `收盤價` · `最低價` · `最高價` · `月營收` · `本益比` · `殖利率` · `每股稅後淨利(元)` · `法人買賣超張數` · `漲跌幅` · `營業毛利率` · `總市值(億)` · `股價淨值比` · `股東權益報酬率` · `轉換價格` · `開盤價`

### FPRICE 價格（19）

`Jensen` · `SHARPE` · `Treynor` · `上游股價指標` · `下游股價指標` · `參考價` · `同業股價指標` · `投資建議目標價` · `振幅` · `月平均收益率` · `標準差` · `波動率` · `漲停價` · `真實範圍` · `真實範圍波幅` · `貝他值` · `跌停價` · `週平均收益率` · `高低差`

### FVOLUME 量能（59）

`上漲量` · `下跌量` · `佔全市場成交量比` · `佔大盤成交量比` · `內外盤比` · `內盤均量` · `內盤成交次數` · `內盤量` · `外盤均量` · `外盤成交次數` · `外盤量` · `成交均量` · `成交金額(元)` · `收盤量` · `新聞正向分數` · `新聞聲量分數` · `新聞負向分數` · `漲停委買數量` · `漲停委買筆數` · `漲停委賣數量` · `漲停委賣筆數` · `盤中整股成交量` · `盤中零股成交量` · `盤後量` · `總成交次數` · `總成交筆數` · `買進中單成交次數` · `買進中單量` · `買進中單金額` · `買進大單成交次數` · `買進大單量` · `買進大單金額` · `買進小單成交次數` · `買進小單量` · `買進小單金額` · `買進特大單成交次數` · `買進特大單量` · `買進特大單金額` · `賣出中單成交次數` · `賣出中單量` · `賣出中單金額` · `賣出大單成交次數` · `賣出大單量` · `賣出大單金額` · `賣出小單成交次數` · `賣出小單量` · `賣出小單金額` · `賣出特大單成交次數` · `賣出特大單量` · `賣出特大單金額` · `跌停委買數量` · `跌停委買筆數` · `跌停委賣數量` · `跌停委賣筆數` · `鉅額交易量` · `開盤委買` · `開盤委賣` · `開盤量` · `零股量`

## 屬性欄位（38）

### SYMBOLINFO 商品資訊欄位（38）

`ETD` · `交易單位` · `交易幣別` · `交易所` · `先買現沖` · `到期日` · `即將處置結束股` · `可放空` · `可轉換日` · `執行比例` · `履約價` · `平可空` · `擔保品` · `有可轉債` · `有期貨` · `有熊證` · `有牛證` · `有認售權證` · `有認購權證` · `有選擇權` · `期貨次遠月` · `期貨近月` · `期貨遠月` · `標的物` · `注意股` · `發行張數` · `票面利率` · `第一個回購日` · `累計異常注意股` · `處置股` · `買賣權` · `買賣現沖` · `賣回權價格` · `賣回權日期` · `轉換價格` · `近期處置結束股` · `面額` · `面額幣別`
